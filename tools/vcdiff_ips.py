#!/usr/bin/env python3
"""Decodificador puro Python (stdlib) de patches RFC 3284 VCDIFF (xdelta) e IPS."""

from __future__ import annotations

import struct
import zlib
from dataclasses import dataclass

VCDIFF_MAGIC = b"\xd6\xc3\xc4\x00"
IPS_MAGIC = b"PATCH"
IPS_EOF = b"EOF"

# Flags VCDIFF (RFC 3284)
_VCD_DECOMPRESS = 0x01
_VCD_CODETABLE = 0x02
_VCD_APPHEADER = 0x04

_VCD_SOURCE = 0x01
_VCD_TARGET = 0x02
_VCD_ADLER32 = 0x04

_OP_NOOP = 0
_OP_ADD = 1
_OP_RUN = 2
_OP_COPY = 3


def _read_varint(buf: bytes | memoryview, pos: int) -> tuple[int, int]:
    val = 0
    limit = len(buf)
    while True:
        if pos >= limit:
            raise ValueError("Varint VCDIFF truncado.")
        b = buf[pos]
        pos += 1
        val = (val << 7) | (b & 0x7F)
        if not (b & 0x80):
            return val, pos


def _build_default_code_table() -> tuple[tuple[int, int, int, int, int, int], ...]:
    table: list[tuple[int, int, int, int, int, int]] = [(_OP_RUN, 0, 0, _OP_NOOP, 0, 0)]
    for size in range(0, 18):
        table.append((_OP_ADD, size, 0, _OP_NOOP, 0, 0))
    for mode in range(9):
        table.append((_OP_COPY, 0, mode, _OP_NOOP, 0, 0))
        for size in range(4, 19):
            table.append((_OP_COPY, size, mode, _OP_NOOP, 0, 0))
    for mode in range(6):
        for add_s in range(1, 5):
            for copy_s in range(4, 7):
                table.append((_OP_ADD, add_s, 0, _OP_COPY, copy_s, mode))
    for mode in range(6, 9):
        for add_s in range(1, 5):
            table.append((_OP_ADD, add_s, 0, _OP_COPY, 4, mode))
    for mode in range(9):
        table.append((_OP_COPY, 4, mode, _OP_ADD, 1, 0))
    assert len(table) == 256
    return tuple(table)


_DEFAULT_CODE_TABLE = _build_default_code_table()


@dataclass(frozen=True)
class VcdiffInfo:
    window_count: int
    target_size: int
    has_secondary_compressor: bool
    secondary_compressor_id: int | None


def inspect_vcdiff(delta: bytes) -> VcdiffInfo:
    """Inspeciona cabecalho e janelas de um arquivo VCDIFF sem precisar da ROM base."""
    if len(delta) < 5 or delta[:4] != VCDIFF_MAGIC:
        raise ValueError("Assinatura VCDIFF invalida.")
    hdr_ind = delta[4]
    pos = 5
    sec_id: int | None = None
    if hdr_ind & _VCD_DECOMPRESS:
        if pos >= len(delta):
            raise ValueError("Cabecalho VCDIFF truncado (compressor secundario).")
        sec_id = delta[pos]
        pos += 1
    if hdr_ind & _VCD_CODETABLE:
        tlen, pos = _read_varint(delta, pos)
        pos += tlen
    if hdr_ind & _VCD_APPHEADER:
        alen, pos = _read_varint(delta, pos)
        pos += alen

    windows = 0
    total_target = 0
    while pos < len(delta):
        win_ind = delta[pos]
        pos += 1
        if win_ind & (_VCD_SOURCE | _VCD_TARGET):
            _, pos = _read_varint(delta, pos)
            _, pos = _read_varint(delta, pos)
        delta_len, pos = _read_varint(delta, pos)
        win_end = pos + delta_len
        if win_end > len(delta):
            raise ValueError(f"Janela VCDIFF {windows} truncada.")
        tgt_len, pos = _read_varint(delta, pos)
        total_target += tgt_len
        pos = win_end
        windows += 1

    return VcdiffInfo(
        window_count=windows,
        target_size=total_target,
        has_secondary_compressor=bool(hdr_ind & _VCD_DECOMPRESS),
        secondary_compressor_id=sec_id,
    )


def apply_vcdiff(source: bytes, delta: bytes, *, verify_adler32: bool = True) -> bytes:
    """Aplica um patch RFC 3284 VCDIFF (xdelta sem compressor secundario) sobre source em RAM."""
    if len(delta) < 5 or delta[:4] != VCDIFF_MAGIC:
        raise ValueError("Assinatura VCDIFF invalida.")
    hdr_ind = delta[4]
    pos = 5
    if hdr_ind & _VCD_DECOMPRESS:
        comp_id = delta[pos]
        raise ValueError(f"Compressor secundario VCDIFF nao suportado sem xdelta3: id={comp_id}")
    if hdr_ind & _VCD_CODETABLE:
        raise ValueError("Tabela de codigos customizada VCDIFF nao suportada.")
    if hdr_ind & _VCD_APPHEADER:
        alen, pos = _read_varint(delta, pos)
        pos += alen

    mv_src = memoryview(source)
    mv_delta = memoryview(delta)
    out = bytearray()
    win_idx = 0

    while pos < len(delta):
        win_ind = delta[pos]
        pos += 1
        seg_src: bytes | memoryview = b""
        if win_ind & _VCD_SOURCE:
            src_len, pos = _read_varint(mv_delta, pos)
            src_pos, pos = _read_varint(mv_delta, pos)
            if src_pos + src_len > len(source):
                raise ValueError(f"Janela VCDIFF {win_idx}: segmento source fora dos limites.")
            seg_src = mv_src[src_pos : src_pos + src_len]
        elif win_ind & _VCD_TARGET:
            src_len, pos = _read_varint(mv_delta, pos)
            src_pos, pos = _read_varint(mv_delta, pos)
            if src_pos + src_len > len(out):
                raise ValueError(f"Janela VCDIFF {win_idx}: segmento target fora dos limites.")
            seg_src = bytes(out[src_pos : src_pos + src_len])

        delta_len, pos = _read_varint(mv_delta, pos)
        win_end = pos + delta_len
        if win_end > len(delta):
            raise ValueError(f"Janela VCDIFF {win_idx} truncada.")

        tgt_len, pos = _read_varint(mv_delta, pos)
        del_ind = delta[pos]
        pos += 1
        if del_ind != 0:
            raise ValueError(f"Janela VCDIFF {win_idx}: secoes comprimidas (del_ind={del_ind}) nao suportadas.")

        data_len, pos = _read_varint(mv_delta, pos)
        inst_len, pos = _read_varint(mv_delta, pos)
        addr_len, pos = _read_varint(mv_delta, pos)
        expected_adler: int | None = None
        if win_ind & _VCD_ADLER32:
            expected_adler = struct.unpack_from(">I", delta, pos)[0]
            pos += 4

        data_s = mv_delta[pos : pos + data_len]
        pos += data_len
        inst_s = mv_delta[pos : pos + inst_len]
        pos += inst_len
        addr_s = mv_delta[pos : pos + addr_len]
        pos += addr_len
        if pos != win_end:
            raise ValueError(f"Janela VCDIFF {win_idx}: tamanho inconsistente ({pos} != {win_end}).")

        near = [0, 0, 0, 0]
        near_next = 0
        same = [0] * (3 * 256)
        dp = 0
        ip = 0
        ap = 0
        tgt = bytearray()
        src_n = len(seg_src)

        def decode_addr(here: int, mode: int) -> int:
            nonlocal ap, near_next
            if mode == 0:
                addr, ap = _read_varint(addr_s, ap)
            elif mode == 1:
                d, ap = _read_varint(addr_s, ap)
                addr = here - d
            elif mode < 6:
                d, ap = _read_varint(addr_s, ap)
                addr = near[mode - 2] + d
            else:
                b = addr_s[ap]
                ap += 1
                addr = same[(mode - 6) * 256 + b]
            near[near_next] = addr
            near_next = (near_next + 1) & 3
            same[addr % 768] = addr
            return addr

        def exec_op(op_t: int, sz: int, mode: int) -> None:
            nonlocal dp, ip
            if op_t == _OP_NOOP:
                return
            if sz == 0:
                sz, ip = _read_varint(inst_s, ip)
            if op_t == _OP_ADD:
                tgt.extend(data_s[dp : dp + sz])
                dp += sz
            elif op_t == _OP_RUN:
                b = data_s[dp]
                dp += 1
                tgt.extend(bytes([b]) * sz)
            elif op_t == _OP_COPY:
                here = src_n + len(tgt)
                addr = decode_addr(here, mode)
                if addr + sz <= src_n:
                    tgt.extend(seg_src[addr : addr + sz])
                else:
                    for _ in range(sz):
                        if addr < src_n:
                            tgt.append(seg_src[addr])
                        else:
                            tgt.append(tgt[addr - src_n])
                        addr += 1

        while ip < inst_len:
            code = inst_s[ip]
            ip += 1
            t1, s1, m1, t2, s2, m2 = _DEFAULT_CODE_TABLE[code]
            exec_op(t1, s1, m1)
            exec_op(t2, s2, m2)

        if len(tgt) != tgt_len:
            raise ValueError(f"Janela VCDIFF {win_idx}: target gerado ({len(tgt)}) != esperado ({tgt_len}).")
        if verify_adler32 and expected_adler is not None:
            actual_adler = zlib.adler32(tgt) & 0xFFFFFFFF
            if actual_adler != expected_adler:
                raise ValueError(
                    f"Janela VCDIFF {win_idx}: Adler32 incorreto (obtido {actual_adler:08x}, esperado {expected_adler:08x})."
                )
        out.extend(tgt)
        win_idx += 1

    return bytes(out)


@dataclass(frozen=True)
class IpsRecord:
    offset: int
    length: int
    rle: bool
    data: bytes


def parse_ips(patch: bytes) -> list[IpsRecord]:
    """Decodifica registros de um patch IPS padrao."""
    if len(patch) < 8 or patch[:5] != IPS_MAGIC:
        raise ValueError("Assinatura IPS invalida (esperado PATCH).")
    pos = 5
    records: list[IpsRecord] = []
    while pos + 3 <= len(patch):
        if patch[pos : pos + 3] == IPS_EOF:
            return records
        offset = (patch[pos] << 16) | (patch[pos + 1] << 8) | patch[pos + 2]
        pos += 3
        if pos + 2 > len(patch):
            raise ValueError("Registro IPS truncado (tamanho).")
        size = struct.unpack_from(">H", patch, pos)[0]
        pos += 2
        if size == 0:
            if pos + 3 > len(patch):
                raise ValueError("Registro IPS RLE truncado.")
            rle_len = struct.unpack_from(">H", patch, pos)[0]
            rle_byte = patch[pos + 2 : pos + 3]
            pos += 3
            records.append(IpsRecord(offset=offset, length=rle_len, rle=True, data=rle_byte * rle_len))
        else:
            if pos + size > len(patch):
                raise ValueError("Registro IPS truncado (dados).")
            data = patch[pos : pos + size]
            pos += size
            records.append(IpsRecord(offset=offset, length=size, rle=False, data=data))
    raise ValueError("Patch IPS sem marcador EOF.")


def apply_ips(source: bytes, patch: bytes) -> bytes:
    """Aplica patch IPS sobre uma copia de source em RAM."""
    records = parse_ips(patch)
    out = bytearray(source)
    for rec in records:
        end = rec.offset + rec.length
        if end > len(out):
            out.extend(b"\x00" * (end - len(out)))
        out[rec.offset : end] = rec.data
    return bytes(out)

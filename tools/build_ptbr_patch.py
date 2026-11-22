#!/usr/bin/env python3
"""Gera e valida o patch delta binario DOSPATCH para Castlevania: Dawn of Sorrow (PT-BR)."""

from __future__ import annotations

import argparse
import hashlib
import struct
import sys
import zlib
from pathlib import Path

DOSPATCH_MAGIC = b"DOSPATCH"
DOSPATCH_VERSION = 1
DOSPATCH_HEADER_STRUCT = struct.Struct("<8sII20s20sII")
CHUNK_HEADER_STRUCT = struct.Struct("<II")
DEFAULT_COALESCE_GAP = 16


def compute_chunks(
    source: bytes, target: bytes, max_gap: int = DEFAULT_COALESCE_GAP
) -> list[tuple[int, bytes]]:
    """Extrai intervalos modificados coalescendo lacunas de ate max_gap bytes."""
    common_len = min(len(source), len(target))
    spans: list[tuple[int, int]] = []
    i = 0
    while i < common_len:
        if source[i] != target[i]:
            start = i
            while i < common_len:
                if source[i] != target[i]:
                    i += 1
                    continue
                gap_start = i
                gap_limit = min(common_len, i + max_gap + 1)
                found_next = False
                for probe in range(gap_start, gap_limit):
                    if source[probe] != target[probe]:
                        i = probe
                        found_next = True
                        break
                if not found_next:
                    break
            spans.append((start, i))
        else:
            i += 1

    if len(target) > common_len:
        if spans and common_len - spans[-1][1] <= max_gap:
            spans[-1] = (spans[-1][0], len(target))
        else:
            spans.append((common_len, len(target)))

    return [(start, target[start:end]) for start, end in spans]


def encode_dospatch(source: bytes, target: bytes, max_gap: int = DEFAULT_COALESCE_GAP) -> bytes:
    """Codifica um delta binario compacto verificavel por SHA-1 e CRC32."""
    chunks = compute_chunks(source, target, max_gap=max_gap)
    payload_parts: list[bytes] = []
    for offset, data in chunks:
        payload_parts.append(CHUNK_HEADER_STRUCT.pack(offset, len(data)))
        payload_parts.append(data)
    payload = b"".join(payload_parts)
    payload_crc = zlib.crc32(payload) & 0xFFFFFFFF

    src_sha1 = hashlib.sha1(source).digest()
    dst_sha1 = hashlib.sha1(target).digest()
    header = DOSPATCH_HEADER_STRUCT.pack(
        DOSPATCH_MAGIC,
        DOSPATCH_VERSION,
        len(target),
        src_sha1,
        dst_sha1,
        len(chunks),
        payload_crc,
    )
    return header + payload


def decode_and_apply_dospatch(source: bytes, patch_bytes: bytes) -> bytes:
    """Aplica o patch DOSPATCH validando magic, SHA-1 de origem, CRC32 e SHA-1 final."""
    if len(patch_bytes) < DOSPATCH_HEADER_STRUCT.size:
        raise ValueError("Patch truncado: cabecalho incompleto.")

    magic, version, target_size, src_sha1, dst_sha1, chunk_count, payload_crc = (
        DOSPATCH_HEADER_STRUCT.unpack_from(patch_bytes, 0)
    )
    if magic != DOSPATCH_MAGIC:
        raise ValueError("Assinatura DOSPATCH invalida.")
    if version != DOSPATCH_VERSION:
        raise ValueError(f"Versao DOSPATCH nao suportada: {version}.")

    actual_src_sha1 = hashlib.sha1(source).digest()
    if actual_src_sha1 != src_sha1:
        raise ValueError(
            f"SHA-1 da ROM base nao confere: esperado {src_sha1.hex()}, obtido {actual_src_sha1.hex()}."
        )

    payload = memoryview(patch_bytes)[DOSPATCH_HEADER_STRUCT.size :]
    if (zlib.crc32(payload) & 0xFFFFFFFF) != payload_crc:
        raise ValueError("CRC32 do payload DOSPATCH corrompido.")

    out = bytearray(source[:target_size])
    if len(out) < target_size:
        out.extend(b"\x00" * (target_size - len(out)))

    cursor = 0
    for _ in range(chunk_count):
        if cursor + CHUNK_HEADER_STRUCT.size > len(payload):
            raise ValueError("Payload DOSPATCH truncado no cabecalho de bloco.")
        offset, length = CHUNK_HEADER_STRUCT.unpack_from(payload, cursor)
        cursor += CHUNK_HEADER_STRUCT.size
        if cursor + length > len(payload):
            raise ValueError("Payload DOSPATCH truncado nos dados do bloco.")
        if offset + length > target_size:
            raise ValueError("Bloco DOSPATCH fora dos limites da ROM de destino.")
        out[offset : offset + length] = payload[cursor : cursor + length]
        cursor += length

    if cursor != len(payload):
        raise ValueError("Bytes extras inesperados ao final do DOSPATCH.")

    result = bytes(out)
    actual_dst_sha1 = hashlib.sha1(result).digest()
    if actual_dst_sha1 != dst_sha1:
        raise ValueError(
            f"SHA-1 final da ROM nao confere: esperado {dst_sha1.hex()}, obtido {actual_dst_sha1.hex()}."
        )
    return result


def inspect_dospatch_header(patch_bytes: bytes) -> dict[str, object]:
    """Le os metadados de um arquivo DOSPATCH."""
    if len(patch_bytes) < DOSPATCH_HEADER_STRUCT.size:
        raise ValueError("Patch truncado.")
    magic, version, target_size, src_sha1, dst_sha1, chunk_count, payload_crc = (
        DOSPATCH_HEADER_STRUCT.unpack_from(patch_bytes, 0)
    )
    if magic != DOSPATCH_MAGIC:
        raise ValueError("Assinatura DOSPATCH invalida.")
    return {
        "version": version,
        "target_size": target_size,
        "source_sha1": src_sha1.hex(),
        "target_sha1": dst_sha1.hex(),
        "chunk_count": chunk_count,
        "payload_crc32": payload_crc,
    }


def main(argv: list[str] | None = None) -> int:
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="Gera patch delta DOSPATCH para PT-BR.")
    parser.add_argument(
        "--source",
        type=Path,
        default=root.parent / "Roms" / "Castlevania - Dawn of Sorrow (USA).nds",
        help="ROM USA original (.nds)",
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=root.parent
        / "Roms"
        / "Castlevania - Dawn of Sorrow (BR-USA) (DE) (T1.0) (www.romsportugues.com).nds",
        help="ROM traduzida PT-BR (.nds)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=root / "mods" / "ptbr" / "dos-ptbr.dospatch",
        help="Arquivo .dospatch de saida",
    )
    parser.add_argument("--verify-only", action="store_true", help="Apenas valida o patch existente.")
    args = parser.parse_args(argv)

    source_bytes = args.source.read_bytes()
    if args.verify_only:
        patch_bytes = args.out.read_bytes()
        applied = decode_and_apply_dospatch(source_bytes, patch_bytes)
        meta = inspect_dospatch_header(patch_bytes)
        print(
            f"[ptbr-patch] verified {args.out}: {meta['chunk_count']} chunks, "
            f"target sha1={hashlib.sha1(applied).hexdigest()}"
        )
        return 0

    target_bytes = args.target.read_bytes()
    patch_bytes = encode_dospatch(source_bytes, target_bytes)
    reconstructed = decode_and_apply_dospatch(source_bytes, patch_bytes)
    if reconstructed != target_bytes:
        raise RuntimeError("Falha na verificacao byte-a-byte do patch gerado.")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(patch_bytes)
    meta = inspect_dospatch_header(patch_bytes)
    print(
        f"[ptbr-patch] wrote {args.out} ({len(patch_bytes)} bytes, "
        f"{meta['chunk_count']} chunks, dst_sha1={meta['target_sha1']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

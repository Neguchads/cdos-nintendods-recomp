"""Testes unitarios do pipeline de mods P0/P1 (VCDIFF, IPS, importador, diff NDS e composicao)."""

from __future__ import annotations

import struct
import sys
import tempfile
import unittest
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import compose_dos_mods as cdm  # noqa: E402
import diff_dos_mods as dm  # noqa: E402
import import_mod_bundle as imb  # noqa: E402
import vcdiff_ips as vi  # noqa: E402


def _encode_varint(n: int) -> bytes:
    parts = [n & 0x7F]
    n >>= 7
    while n:
        parts.append((n & 0x7F) | 0x80)
        n >>= 7
    return bytes(reversed(parts))


def _make_simple_vcdiff(target_bytes: bytes) -> bytes:
    """Cria um arquivo RFC 3284 VCDIFF valido com uma janela ADD pura (sem source)."""
    adler = zlib.adler32(target_bytes) & 0xFFFFFFFF
    # Opcode 1 = ADD size 0 (varint)
    inst = bytes([1]) + _encode_varint(len(target_bytes))
    win_body = (
        _encode_varint(len(target_bytes))
        + bytes([0])  # del_ind = 0
        + _encode_varint(len(target_bytes))
        + _encode_varint(len(inst))
        + _encode_varint(0)
        + struct.pack(">I", adler)
        + target_bytes
        + inst
    )
    # win_ind = 0x04 (VCD_ADLER32)
    return vi.VCDIFF_MAGIC + bytes([0, 0x04]) + _encode_varint(len(win_body)) + win_body


def _make_synthetic_nds(file0: bytes, file1: bytes, arm9: bytes) -> bytes:
    """Monta uma ROM NDS sintetica minima com Header, ARM9, FNT e FAT validos."""
    rom = bytearray(0x4000)
    arm9_off = 0x1000
    fnt_off = 0x1800
    fat_off = 0x1C00
    f0_off = 0x2000
    f1_off = 0x2800

    # FNT minimo: 1 diretorio raiz com 2 arquivos ("a.bin", "b.bin")
    sub = bytes([5]) + b"a.bin" + bytes([5]) + b"b.bin" + bytes([0])
    struct.pack_into("<IHH", rom, fnt_off, 8, 0, 1)
    rom[fnt_off + 8 : fnt_off + 8 + len(sub)] = sub
    fnt_sz = 8 + len(sub)

    # FAT: 2 arquivos
    struct.pack_into("<II", rom, fat_off, f0_off, f0_off + len(file0))
    struct.pack_into("<II", rom, fat_off + 8, f1_off, f1_off + len(file1))
    fat_sz = 16

    rom[arm9_off : arm9_off + len(arm9)] = arm9
    rom[f0_off : f0_off + len(file0)] = file0
    rom[f1_off : f1_off + len(file1)] = file1

    struct.pack_into("<IIII", rom, 0x20, arm9_off, 0x02000800, 0x02000000, len(arm9))
    struct.pack_into("<IIII", rom, 0x30, 0x1400, 0x02380000, 0x02380000, 0x100)
    struct.pack_into("<IIII", rom, 0x40, fnt_off, fnt_sz, fat_off, fat_sz)
    struct.pack_into("<II", rom, 0x50, 0, 0)
    return bytes(rom)


class TestModPipelineP0(unittest.TestCase):
    def test_vcdiff_inspect_and_apply_roundtrip(self) -> None:
        target = b"Castlevania Dawn of Sorrow Native Recomp!" * 4
        delta = _make_simple_vcdiff(target)
        info = vi.inspect_vcdiff(delta)
        self.assertEqual(info.window_count, 1)
        self.assertEqual(info.target_size, len(target))
        self.assertFalse(info.has_secondary_compressor)
        self.assertEqual(vi.apply_vcdiff(b"", delta), target)

    def test_ips_parse_and_apply_including_rle(self) -> None:
        src = bytearray(b"A" * 32)
        # Offset 4: "TEST" (4 B), Offset 16: RLE 6x 'Z'
        ips = (
            b"PATCH"
            + struct.pack(">BH", 0, 4)[0:3]  # 3-byte offset = 4
        )
        ips = b"PATCH" + (4).to_bytes(3, "big") + struct.pack(">H", 4) + b"TEST"
        ips += (16).to_bytes(3, "big") + struct.pack(">HHB", 0, 6, ord("Z"))
        ips += b"EOF"
        recs = vi.parse_ips(ips)
        self.assertEqual(len(recs), 2)
        out = vi.apply_ips(bytes(src), ips)
        self.assertEqual(out[4:8], b"TEST")
        self.assertEqual(out[16:22], b"ZZZZZZ")

    def test_import_bundle_classifies_accepts_dos_and_rejects_dominus_and_por(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            zpath = Path(tmp) / "bundle.zip"
            fake_repo = Path(tmp) / "repo"
            fake_repo.mkdir()
            dos_ips = b"PATCH" + (0x10).to_bytes(3, "big") + struct.pack(">H", 2) + b"\x90\x90" + b"EOF"
            dominus_xdelta = _make_simple_vcdiff(b"X" * 1024)
            fake_mp4_dos = b"\x00\x00\x00\x18ftypisom\x00\x00\x02\x00" + b"VIDEO"
            fake_mp4_por = b"\x00\x00\x00\x18ftypisom\x00\x00\x02\x00" + b"PORVID"

            with zipfile.ZipFile(zpath, "w") as zf:
                zf.writestr("DoS/no_touch.ips", dos_ips)
                zf.writestr("Dominus/Dra01dll.xdelta", dominus_xdelta)
                zf.writestr("AI/CVNDS_OPmovie_DoS.webm", fake_mp4_dos)
                zf.writestr("AI/CVNDS_OPmovie_PoR.webm", fake_mp4_por)

            cat = imb.import_bundle(zpath, repo_root=fake_repo)
            self.assertEqual(cat["summary"]["accepted"], 2)
            self.assertEqual(cat["summary"]["rejected"], 2)
            self.assertTrue((fake_repo / "mods" / "local" / "no_touch.ips").is_file())
            self.assertTrue((fake_repo / "mods" / "intro" / "opening.mp4").is_file())
            self.assertTrue((fake_repo / "mods" / "catalog.json").is_file())

    def test_semantic_nds_diff_detects_def_only_ptbr_only_and_conflicts(self) -> None:
        usa = _make_synthetic_nds(b"PORTRAIT_OLD____", b"ENGLISH_TEXT____", b"\x01\x02\x03\x04" * 4)
        def_rom = _make_synthetic_nds(b"PORTRAIT_DIGNITY", b"ENGLISH_TEXT____", b"\x99\x02\x03\x04" * 4)
        ptbr_rom = _make_synthetic_nds(b"PORTRAIT_OTHER__", b"TEXTO_PTBR______", b"\x01\x02\x03\x04" * 4)

        rep = dm.analyze_mod_diffs(usa, def_rom, ptbr_rom)
        self.assertEqual(rep["regions"]["arm9_def_changed"], 4)
        self.assertEqual(rep["regions"]["arm9_ptbr_changed"], 0)
        self.assertEqual(rep["summary_counts"]["ptbr_only_files"], 1)
        self.assertEqual(rep["summary_counts"]["true_conflict_files"], 1)
        self.assertEqual(rep["files_true_conflict"][0]["name"], "a.bin")
        self.assertEqual(rep["files_ptbr_only"][0]["name"], "b.bin")

    def test_compose_definitive_with_ptbr_merges_arm9_files_and_recomputes_header_crc16(self) -> None:
        usa = _make_synthetic_nds(b"PORTRAIT_OLD____", b"ENGLISH_TEXT____", b"\x01\x02\x03\x04" * 4)
        def_rom = bytearray(_make_synthetic_nds(b"PORTRAIT_DIGNITY", b"ENGLISH_TEXT____", b"\x99\x02\x03\x04" * 4))
        ptbr_rom = bytearray(_make_synthetic_nds(b"PORTRAIT_DIGNITY", b"TEXTO_PTBR______", b"\x01\x02\x77\x04" * 4))

        composed, report = cdm.compose_definitive_with_ptbr(usa, bytes(def_rom), bytes(ptbr_rom))
        # ARM9 deve conter 0x99 da Definitive E 0x77 da PT-BR
        self.assertEqual(composed[0x1000], 0x99)
        self.assertEqual(composed[0x1002], 0x77)
        # Retrato da Definitive e texto da PT-BR preservados
        self.assertEqual(composed[0x2000:0x2010], b"PORTRAIT_DIGNITY")
        self.assertEqual(composed[0x2800:0x2810], b"TEXTO_PTBR______")
        # CRC16 do cabecalho recalculado corretamente
        expected_crc = cdm.nds_crc16(composed[:0x15E])
        actual_crc = struct.unpack_from("<H", composed, 0x15E)[0]
        self.assertEqual(actual_crc, expected_crc)
        self.assertEqual(report["header_crc16_hex"], f"{expected_crc:04x}")


if __name__ == "__main__":
    unittest.main()

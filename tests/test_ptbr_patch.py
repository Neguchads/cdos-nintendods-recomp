"""Testes unitarios para o gerador e validador DOSPATCH PT-BR."""

from __future__ import annotations

import hashlib
import sys
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import build_ptbr_patch as bpp  # noqa: E402


class TestDosPatch(unittest.TestCase):
    def test_synthetic_roundtrip_and_coalescing(self) -> None:
        base = bytearray(b"A" * 4096)
        target = bytearray(base)
        target[100:105] = b"HELLO"
        # Lacuna de 8 bytes <= 16 deve coalescer em um unico bloco.
        target[113:118] = b"WORLD"
        target[2000:2020] = b"TESTE-ACENTO-\xc3\xa7\xc3\xa3\xc3\xb5!"

        chunks = bpp.compute_chunks(bytes(base), bytes(target), max_gap=16)
        self.assertEqual(len(chunks), 2)

        patch = bpp.encode_dospatch(bytes(base), bytes(target))
        applied = bpp.decode_and_apply_dospatch(bytes(base), patch)
        self.assertEqual(applied, bytes(target))

    def test_rejects_corrupted_crc_and_wrong_source(self) -> None:
        base = b"0123456789ABCDEF" * 64
        target = b"X123456789ABCDEF" * 64
        patch = bytearray(bpp.encode_dospatch(base, target))

        with self.assertRaises(ValueError):
            bpp.decode_and_apply_dospatch(b"\x00" * len(base), bytes(patch))

        bad_crc = bytearray(patch)
        bad_crc[-1] ^= 0xFF
        with self.assertRaises(ValueError):
            bpp.decode_and_apply_dospatch(base, bytes(bad_crc))

        bad_magic = bytearray(patch)
        bad_magic[0:4] = b"NOPE"
        with self.assertRaises(ValueError):
            bpp.decode_and_apply_dospatch(base, bytes(bad_magic))

    def test_repo_patch_if_present_matches_expected_sha1(self) -> None:
        patch_path = ROOT / "mods" / "ptbr" / "dos-ptbr.dospatch"
        usa_rom = ROOT.parent / "Roms" / "Castlevania - Dawn of Sorrow (USA).nds"
        if not patch_path.exists() or not usa_rom.exists():
            self.skipTest("Patch ou ROM base ausente neste ambiente.")
        patch_bytes = patch_path.read_bytes()
        meta = bpp.inspect_dospatch_header(patch_bytes)
        self.assertEqual(meta["source_sha1"], "47530ff87e608f88105a314fdf36dc385f8dec94")
        self.assertEqual(meta["target_sha1"], "c9a1552bcdcd8fdf3c052d975e6838da7ead08d1")
        applied = bpp.decode_and_apply_dospatch(usa_rom.read_bytes(), patch_bytes)
        self.assertEqual(
            hashlib.sha1(applied).hexdigest(),
            "c9a1552bcdcd8fdf3c052d975e6838da7ead08d1",
        )

    def test_repo_does_not_bundle_third_party_dospatch_files(self) -> None:
        # Clean-room & creator-permission guard: no third-party .dospatch bundled under mods/ptbr or mods/definitive.
        self.assertFalse((ROOT / "mods" / "ptbr" / "dos-ptbr.dospatch").exists())
        self.assertFalse((ROOT / "mods" / "definitive" / "dos-definitive-en.dospatch").exists())
        self.assertFalse((ROOT / "mods" / "definitive" / "dos-definitive-ptbr.dospatch").exists())


if __name__ == "__main__":
    unittest.main()

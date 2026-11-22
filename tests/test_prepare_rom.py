#!/usr/bin/env python3
"""Testes unitários e de integração para tools/prepare_rom.py."""

from __future__ import annotations

import json
import struct
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import prepare_rom  # noqa: E402


class PrepareRomTests(unittest.TestCase):
    def test_parse_nds_header_extracts_fields(self) -> None:
        buf = bytearray(0x400)
        buf[0x00:0x0C] = b"CASTLEVANIA1"
        buf[0x0C:0x10] = b"ACVE"
        buf[0x10:0x12] = b"A4"
        buf[0x1E] = 0
        struct.pack_into("<IIII", buf, 0x20, 0x4000, 0x02000800, 0x02000000, 0x1000)
        struct.pack_into("<IIII", buf, 0x30, 0x8000, 0x02380000, 0x02380000, 0x0800)
        struct.pack_into("<IIII", buf, 0x40, 0x9000, 0x100, 0xA000, 0x20)
        struct.pack_into("<IIII", buf, 0x50, 0x5000, 0x40, 0, 0)

        hdr = prepare_rom.parse_nds_header(bytes(buf))
        self.assertEqual(hdr.title, b"CASTLEVANIA1")
        self.assertEqual(hdr.game_code, b"ACVE")
        self.assertEqual(hdr.arm9_entry, 0x02000800)
        self.assertEqual(hdr.arm7_ram, 0x02380000)
        self.assertEqual(hdr.ov9_size, 0x40)

    def test_validate_retail_rom_rejects_wrong_size_and_hash(self) -> None:
        with self.assertRaises(ValueError):
            prepare_rom.validate_retail_rom(b"\x00" * 1024)

        fake = bytearray(prepare_rom.EXPECTED_ROM_SIZE)
        fake[0x00:0x0C] = b"CASTLEVANIA1"
        fake[0x0C:0x10] = b"ACVE"
        with self.assertRaises(ValueError):
            prepare_rom.validate_retail_rom(bytes(fake))

    def test_extract_arm9_overlays_rejects_compressed(self) -> None:
        buf = bytearray(0x1000)
        struct.pack_into("<IIII", buf, 0x40, 0x100, 0x10, 0x200, 0x10)
        struct.pack_into("<IIII", buf, 0x50, 0x300, 0x20, 0, 0)
        struct.pack_into("<II", buf, 0x200, 0x400, 0x500)
        # flags com bit 24 setado -> comprimido
        struct.pack_into("<IIIIIIII", buf, 0x300, 0, 0x0219E3E0, 0x100, 0, 0, 0, 0, 0x01000080)
        hdr = prepare_rom.parse_nds_header(bytes(buf))
        with self.assertRaises(ValueError):
            prepare_rom.extract_arm9_overlays(bytes(buf), hdr)

    def test_format_program_toml_parses_cleanly(self) -> None:
        payload = b"\x01\x02\x03\x04" * 16
        text = prepare_rom.format_program_toml(
            name="Test ARM9",
            program_id="dos_arm9",
            cpu="arm9",
            isa="armv5te",
            load_address=0x02000000,
            entry_pc=0x02000800,
            binary=payload,
        )
        parsed = tomllib.loads(text)
        self.assertEqual(parsed["program"]["id"], "dos_arm9")
        self.assertEqual(parsed["program"]["load_address"], 0x02000000)
        self.assertEqual(parsed["program"]["size"], len(payload))
        self.assertEqual(parsed["identity"]["sha1"], prepare_rom.sha1_hex(payload))
        self.assertEqual(parsed["entry_point"][0]["addr"], 0x02000800)

    def test_prepare_real_rom_when_available(self) -> None:
        rom_path = prepare_rom.DEFAULT_ROM
        if not rom_path.is_file():
            self.skipTest(f"ROM real não disponível: {rom_path}")
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "inputs"
            manifest = prepare_rom.prepare_rom(rom_path, out_dir)
            self.assertEqual(manifest["arm9"]["size"], 0xC6B98)
            self.assertEqual(manifest["arm7"]["size"], 0x26654)
            self.assertEqual(len(manifest["overlays_arm9"]), 41)
            self.assertTrue((out_dir / "arm9.bin").is_file())
            self.assertTrue((out_dir / "arm7.bin").is_file())
            arm9_toml = tomllib.loads((out_dir / "arm9.toml").read_text("utf-8"))
            arm7_toml = tomllib.loads((out_dir / "arm7.toml").read_text("utf-8"))
            self.assertEqual(arm9_toml["identity"]["sha1"], manifest["arm9"]["sha1"])
            self.assertEqual(arm7_toml["identity"]["sha1"], manifest["arm7"]["sha1"])
            ov_files = list((out_dir / "overlays").glob("ov9_*.bin"))
            self.assertEqual(len(ov_files), 41)
            manifest_disk = json.loads((out_dir / "overlays_manifest.json").read_text("utf-8"))
            self.assertEqual(manifest_disk["rom"]["game_code"], "ACVE")


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Testes unitários para tools/promote_banks.py."""

from __future__ import annotations

import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import promote_banks  # noqa: E402


class PromoteBanksTests(unittest.TestCase):
    def test_parse_dsd_symbols_extracts_arm_and_thumb(self) -> None:
        sample = "\n".join(
            [
                "Entry kind:function(arm,size=0x100) addr:0x02000800",
                "VBlankIntrWait kind:function(thumb,size=0x6) addr:0x020001f8",
                "g_table kind:data(size=0x20) addr:0x02050000",
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "symbols.txt"
            p.write_text(sample, encoding="utf-8")
            funcs = promote_banks.parse_dsd_symbols(p)
        self.assertEqual(
            funcs,
            [
                (0x02000800, "arm", "Entry"),
                (0x020001F8, "thumb", "VBlankIntrWait"),
            ],
        )

    def test_deduplicate_seeds_filters_bounds_alignment_and_duplicates(self) -> None:
        list_a = [
            (0x02000800, "arm", "runtime", "rt_entry"),
            (0x02000802, "arm", "bad_align", ""),  # ARM precisa alinhar em 4
            (0x02000902, "thumb", "runtime", ""),
            (0x03000000, "arm", "oob", ""),
        ]
        list_b = [
            (0x02000800, "arm", "dsd", "Entry"),  # duplicado, deve perder para list_a
            (0x02000A00, "arm", "dsd", "FuncA"),
        ]
        merged = promote_banks.deduplicate_seeds(
            [list_a, list_b], addr_start=0x02000000, addr_end=0x02100000
        )
        self.assertEqual(
            merged,
            [
                (0x02000800, "arm", "runtime", "rt_entry"),
                (0x02000902, "thumb", "runtime", ""),
                (0x02000A00, "arm", "dsd", "FuncA"),
            ],
        )

    def test_write_program_with_seeds_valid_toml(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "prog.toml"
            promote_banks.write_program_with_seeds(
                p,
                name="Test",
                program_id="dosprom_arm9_test",
                cpu="arm9",
                isa="armv5te",
                load_address=0x02000000,
                entry_pc=0x02000800,
                binary=b"\x00" * 64,
                seeds=[(0x02000800, "arm", "dsd", "Entry")],
            )
            parsed = tomllib.loads(p.read_text("utf-8"))
        self.assertEqual(parsed["program"]["id"], "dosprom_arm9_test")
        self.assertEqual(parsed["program"]["load_address"], 0x02000000)
        self.assertEqual(parsed["entry_point"][0]["name"], "Entry")


if __name__ == "__main__":
    unittest.main()

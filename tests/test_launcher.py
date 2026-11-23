"""Testes para o executavel standalone CastlevaniaDawnOfSorrow.exe e icone PE embutido."""

from __future__ import annotations

import struct
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import build as build_tool  # noqa: E402


def pe_resource_types(exe_path: Path) -> set[int]:
    """Extrai os IDs de tipos de recurso da tabela .rsrc de um executavel PE (stdlib pura)."""
    data = exe_path.read_bytes()
    if data[:2] != b"MZ":
        raise AssertionError(f"{exe_path.name} nao possui cabecalho MZ")
    pe_offset = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe_offset : pe_offset + 4] != b"PE\x00\x00":
        raise AssertionError(f"{exe_path.name} nao possui assinatura PE")

    num_sections = struct.unpack_from("<H", data, pe_offset + 6)[0]
    opt_header_size = struct.unpack_from("<H", data, pe_offset + 20)[0]
    opt_start = pe_offset + 24
    magic = struct.unpack_from("<H", data, opt_start)[0]
    # DataDirectory[2] = Resource Table (offset 96 em PE32, 112 em PE32+)
    dd_offset = opt_start + (112 if magic == 0x20B else 96)
    rsrc_rva, rsrc_size = struct.unpack_from("<II", data, dd_offset + 2 * 8)
    if rsrc_rva == 0 or rsrc_size == 0:
        return set()

    sect_start = opt_start + opt_header_size
    rsrc_raw = None
    for i in range(num_sections):
        off = sect_start + i * 40
        vsize, va, raw_size, raw_ptr = struct.unpack_from("<IIII", data, off + 8)
        span = max(vsize, raw_size)
        if va <= rsrc_rva < va + span:
            rsrc_raw = raw_ptr + (rsrc_rva - va)
            break
    if rsrc_raw is None:
        return set()

    # IMAGE_RESOURCE_DIRECTORY: 12 bytes + NumberOfNamedEntries (H) + NumberOfIdEntries (H)
    num_named, num_id = struct.unpack_from("<HH", data, rsrc_raw + 12)
    types: set[int] = set()
    entries_start = rsrc_raw + 16
    for i in range(num_named + num_id):
        name_or_id, _offset_to_data = struct.unpack_from("<II", data, entries_start + i * 8)
        if (name_or_id & 0x80000000) == 0:
            types.add(name_or_id)
    return types


class TestWindowsLauncherAndIcon(unittest.TestCase):
    def test_launcher_sources_and_icon_rc_exist(self) -> None:
        rc_path = ROOT / "launcher" / "app_icon.rc"
        cpp_path = ROOT / "launcher" / "launcher_win32.cpp"
        self.assertTrue(rc_path.is_file(), "Falta launcher/app_icon.rc")
        self.assertTrue(cpp_path.is_file(), "Falta launcher/launcher_win32.cpp")
        rc_text = rc_path.read_text(encoding="utf-8")
        self.assertIn("assets/recomplauncher/icon.ico", rc_text)
        self.assertTrue((ROOT / "assets" / "recomplauncher" / "icon.ico").is_file())

    def test_build_tool_exposes_launcher_target_and_cli(self) -> None:
        self.assertEqual(build_tool.LAUNCHER_EXE, ROOT / "CastlevaniaDawnOfSorrow.exe")
        parser = build_tool.build_parser()
        ns = parser.parse_args(["launcher"])
        self.assertEqual(ns.command, "launcher")

    def test_built_exes_embed_windows_icon_resources(self) -> None:
        launcher_exe = ROOT / "CastlevaniaDawnOfSorrow.exe"
        runner_exe = ROOT / "runtime" / "nds_runner.exe"
        if not launcher_exe.is_file() or not runner_exe.is_file():
            self.skipTest("Executaveis Windows ainda nao compilados neste ambiente.")
        # RT_ICON = 3, RT_GROUP_ICON = 14
        for exe in (launcher_exe, runner_exe):
            rtypes = pe_resource_types(exe)
            self.assertIn(3, rtypes, f"{exe.name} sem recurso RT_ICON (3): {rtypes}")
            self.assertIn(14, rtypes, f"{exe.name} sem recurso RT_GROUP_ICON (14): {rtypes}")

    def test_launcher_exe_print_command_resolves_runner_and_paths(self) -> None:
        launcher_exe = ROOT / "CastlevaniaDawnOfSorrow.exe"
        if not launcher_exe.is_file():
            self.skipTest("CastlevaniaDawnOfSorrow.exe nao compilado neste ambiente.")
        fake_rom = ROOT / "game.toml"
        proc = subprocess.run(
            [str(launcher_exe), "--print-command", "--rom", str(fake_rom)],
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, f"stderr={proc.stderr}")
        self.assertIn("nds_runner.exe", proc.stdout)
        self.assertIn("--config", proc.stdout)
        self.assertIn("game.toml", proc.stdout)
        self.assertIn("--ptbr-patch", proc.stdout)
        self.assertIn("dos-ptbr.dospatch", proc.stdout)
        self.assertIn(str(fake_rom), proc.stdout)


if __name__ == "__main__":
    unittest.main()

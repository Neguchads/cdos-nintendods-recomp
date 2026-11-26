"""Testes para o executavel standalone CastlevaniaDawnOfSorrow.exe e icone PE embutido."""

from __future__ import annotations

import struct
import subprocess
import sys
import tempfile
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
        # RT_ICON = 3, RT_GROUP_ICON = 14, RT_VERSION = 16, RT_MANIFEST = 24
        for exe in (launcher_exe, runner_exe):
            rtypes = pe_resource_types(exe)
            self.assertIn(3, rtypes, f"{exe.name} sem recurso RT_ICON (3): {rtypes}")
            self.assertIn(14, rtypes, f"{exe.name} sem recurso RT_GROUP_ICON (14): {rtypes}")
            self.assertIn(16, rtypes, f"{exe.name} sem recurso RT_VERSION (16): {rtypes}")
            self.assertIn(24, rtypes, f"{exe.name} sem recurso RT_MANIFEST (24): {rtypes}")

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
        self.assertIn("--mod-registry", proc.stdout)
        self.assertIn(str(fake_rom), proc.stdout)

    def test_launcher_setup_validates_rom_installs_locally_and_creates_shortcut(self) -> None:
        launcher_exe = ROOT / "CastlevaniaDawnOfSorrow.exe"
        real_rom = ROOT.parent / "Roms" / "Castlevania - Dawn of Sorrow (USA).nds"
        if not launcher_exe.is_file() or not real_rom.is_file():
            self.skipTest("CastlevaniaDawnOfSorrow.exe ou ROM USA nao disponiveis neste ambiente.")
        with tempfile.TemporaryDirectory() as tmp:
            install = Path(tmp) / "cdos-install"
            install.mkdir(parents=True, exist_ok=True)
            (install / "CastlevaniaDawnOfSorrow.exe").write_bytes(launcher_exe.read_bytes())
            (install / "game.toml").write_bytes((ROOT / "game.toml").read_bytes())
            (install / "runtime").mkdir(parents=True, exist_ok=True)
            (install / "runtime" / "nds_runner.exe").write_bytes(b"MZ-stub")
            (install / "mods" / "ptbr").mkdir(parents=True, exist_ok=True)
            (install / "mods" / "ptbr" / "dos-ptbr.dospatch").write_bytes(b"DOSPATCH")

            bad_rom = Path(tmp) / "invalid.nds"
            bad_rom.write_bytes(b"not-a-valid-ds-rom")
            bad_proc = subprocess.run(
                [str(install / "CastlevaniaDawnOfSorrow.exe"), "--setup-only", "--rom", str(bad_rom)],
                cwd=str(install),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            self.assertNotEqual(bad_proc.returncode, 0, "Setup aceitou ROM invalida")

            shortcut_path = Path(tmp) / "Castlevania - Dawn of Sorrow.lnk"
            ok_proc = subprocess.run(
                [
                    str(install / "CastlevaniaDawnOfSorrow.exe"),
                    "--setup-only",
                    "--rom",
                    str(real_rom),
                    "--shortcut-path",
                    str(shortcut_path),
                ],
                cwd=str(install),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            self.assertEqual(ok_proc.returncode, 0, f"setup falhou: out={ok_proc.stdout} err={ok_proc.stderr}")
            installed_rom = install / "game" / "Castlevania - Dawn of Sorrow (USA).nds"
            self.assertTrue(installed_rom.is_file(), "ROM nao instalada em game/")
            self.assertEqual(installed_rom.stat().st_size, 67108864)
            self.assertTrue(shortcut_path.is_file(), "Atalho .lnk nao criado")
            self.assertGreater(shortcut_path.stat().st_size, 100)

            # Com a ROM instalada em game/, --print-command sem --rom deve resolver game/ automaticamente.
            cmd_proc = subprocess.run(
                [str(install / "CastlevaniaDawnOfSorrow.exe"), "--print-command"],
                cwd=str(install),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            self.assertEqual(cmd_proc.returncode, 0, f"stderr={cmd_proc.stderr}")
            self.assertIn(str(installed_rom), cmd_proc.stdout)


if __name__ == "__main__":
    unittest.main()

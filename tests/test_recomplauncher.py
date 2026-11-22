"""Testes de integracao e empacotamento para RecompLauncher."""

from __future__ import annotations

import json
import sys
import tempfile
import tomllib
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import package_recomplauncher as pr  # noqa: E402


class TestRecompLauncher(unittest.TestCase):
    def test_manifest_validates_cleanly(self) -> None:
        errors = pr.validate_manifest(ROOT / "recomplauncher.json")
        self.assertEqual(errors, [], f"Erros de manifesto: {errors}")

    def test_manifest_has_expected_schema_and_ptbr_setting(self) -> None:
        data = json.loads((ROOT / "recomplauncher.json").read_text(encoding="utf-8"))
        self.assertEqual(data["format"], 1)
        setting_ids = {s["id"] for s in data["settings"]}
        self.assertIn("ui_language", setting_ids)
        self.assertIn("game_language", setting_ids)
        self.assertIn("skip_launcher", setting_ids)
        self.assertIn("pip_size", setting_ids)
        self.assertIn("vsync", setting_ids)
        self.assertIn("stick_deadzone", setting_ids)

    def test_stage_release_excludes_roms(self) -> None:
        if not (ROOT / "runtime" / "nds_runner.exe").is_file():
            self.skipTest("runtime/nds_runner.exe nao compilado.")
        with tempfile.TemporaryDirectory() as tmp:
            stage = Path(tmp) / "stage"
            pr.stage_release_tree(ROOT, out_dir=stage, make_zip=False)
            self.assertTrue((stage / "recomplauncher.json").is_file())
            self.assertTrue((stage / "mods" / "ptbr" / "dos-ptbr.dospatch").is_file())
            self.assertTrue((stage / "runtime" / "nds_runner.exe").is_file())
            self.assertTrue((stage / "SHA256SUMS.txt").is_file())
            nds_files = list(stage.rglob("*.nds"))
            self.assertEqual(nds_files, [])

    def test_manifest_repo_and_project_configs_are_valid(self) -> None:
        data = json.loads((ROOT / "recomplauncher.json").read_text(encoding="utf-8"))
        self.assertEqual(data["repo"], "Neguchads/cdos-nintendods-recomp")
        self.assertIn("graphics", data["system"]["windows"])
        self.assertIn("graphics", data["system"]["linux"])
        self.assertNotIn("notes", data["system"]["linux"])

        presets_data = json.loads((ROOT / "CMakePresets.json").read_text(encoding="utf-8"))
        preset_names = {p["name"] for p in presets_data["configurePresets"]}
        self.assertTrue(
            {
                "windows-mingw-dx12",
                "linux-vulkan-release",
                "steamdeck-vulkan",
                "android-arm64-vulkan",
            }.issubset(preset_names)
        )

        game_cfg = tomllib.loads((ROOT / "game.toml").read_text(encoding="utf-8"))
        self.assertEqual(game_cfg["game"]["id"], "ACVE")
        self.assertEqual(
            game_cfg["game"]["sha1"],
            "47530ff87e608f88105a314fdf36dc385f8dec94",
        )

        android_manifest = (
            ROOT / "android" / "app" / "src" / "main" / "AndroidManifest.xml"
        ).read_text(encoding="utf-8")
        xml_root = ET.fromstring(android_manifest)
        self.assertEqual(xml_root.tag, "manifest")


if __name__ == "__main__":
    unittest.main()

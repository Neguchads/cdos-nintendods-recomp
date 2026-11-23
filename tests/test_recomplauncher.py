"""Testes de integracao e empacotamento para RecompLauncher (manifesto SDK 1.0 + kit de midia)."""

from __future__ import annotations

import json
import struct
import sys
import tempfile
import tomllib
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import package_recomplauncher as pr  # noqa: E402

ART = ROOT / "assets" / "recomplauncher"
SHOTS = ROOT / "assets" / "screenshots"


def png_info(path: Path) -> tuple[int, int, int]:
    """(largura, altura, tipo de cor) lidos do IHDR; stdlib pura (sem Pillow no CI)."""
    data = path.read_bytes()[:33]
    assert data[:8] == b"\x89PNG\r\n\x1a\n", f"{path.name} nao e PNG"
    width, height = struct.unpack(">II", data[16:24])
    return width, height, data[25]


def jpeg_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    assert data[:2] == b"\xff\xd8", f"{path.name} nao e JPEG"
    i = 2
    while i < len(data):
        assert data[i] == 0xFF, "marcador JPEG invalido"
        marker = data[i + 1]
        length = struct.unpack(">H", data[i + 2 : i + 4])[0]
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            height, width = struct.unpack(">HH", data[i + 5 : i + 9])
            return width, height
        i += 2 + length
    raise AssertionError("SOF nao encontrado")


def ico_sizes(path: Path) -> set[tuple[int, int]]:
    data = path.read_bytes()
    reserved, kind, count = struct.unpack("<HHH", data[:6])
    assert (reserved, kind) == (0, 1), f"{path.name} nao e ICO"
    sizes = set()
    for n in range(count):
        entry = data[6 + 16 * n : 22 + 16 * n]
        sizes.add((entry[0] or 256, entry[1] or 256))
    return sizes


class TestRecompLauncher(unittest.TestCase):
    def test_manifest_validates_cleanly(self) -> None:
        errors = pr.validate_manifest(ROOT / "recomplauncher.json")
        self.assertEqual(errors, [], f"Erros de manifesto: {errors}")

    def test_manifest_has_expected_schema_and_ptbr_setting(self) -> None:
        data = json.loads((ROOT / "recomplauncher.json").read_text(encoding="utf-8"))
        self.assertEqual(data["format"], 1)
        setting_ids = {s["id"] for s in data["settings"]}
        for needed in ("ui_language", "game_language", "skip_launcher", "pip_size", "vsync", "stick_deadzone"):
            self.assertIn(needed, setting_ids)

    def test_stage_release_excludes_roms(self) -> None:
        if not (ROOT / "runtime" / "nds_runner.exe").is_file() or not (ROOT / "CastlevaniaDawnOfSorrow.exe").is_file():
            self.skipTest("runtime/nds_runner.exe ou CastlevaniaDawnOfSorrow.exe nao compilados.")
        with tempfile.TemporaryDirectory() as tmp:
            stage = Path(tmp) / "stage"
            pr.stage_release_tree(ROOT, out_dir=stage, make_zip=False)
            self.assertTrue((stage / "recomplauncher.json").is_file())
            self.assertTrue((stage / "CastlevaniaDawnOfSorrow.exe").is_file())
            self.assertTrue((stage / "mods" / "ptbr" / "dos-ptbr.dospatch").is_file())
            self.assertTrue((stage / "runtime" / "nds_runner.exe").is_file())
            self.assertTrue((stage / "assets" / "recomplauncher" / "icon.png").is_file())
            self.assertTrue((stage / "SHA256SUMS.txt").is_file())
            self.assertEqual(list(stage.rglob("*.nds")), [])
            self.assertFalse((stage / "recompdata").exists())

    def test_manifest_repo_and_project_configs_are_valid(self) -> None:
        data = json.loads((ROOT / "recomplauncher.json").read_text(encoding="utf-8"))
        self.assertEqual(data["repo"], "Neguchads/cdos-nintendods-recomp")
        self.assertEqual(data["$schema"], "https://recomplauncher.com/schema/recomplauncher.json")
        self.assertIn("graphics", data["system"]["windows"])
        self.assertIn("graphics", data["system"]["linux"])
        self.assertNotIn("notes", data["system"]["linux"])

        presets_data = json.loads((ROOT / "CMakePresets.json").read_text(encoding="utf-8"))
        preset_names = {p["name"] for p in presets_data["configurePresets"]}
        self.assertTrue(
            {"windows-mingw-dx12", "linux-vulkan-release", "steamdeck-vulkan", "android-arm64-vulkan"}.issubset(preset_names)
        )

        game_cfg = tomllib.loads((ROOT / "game.toml").read_text(encoding="utf-8"))
        self.assertEqual(game_cfg["game"]["id"], "ACVE")
        self.assertEqual(game_cfg["game"]["sha1"], "47530ff87e608f88105a314fdf36dc385f8dec94")

        android_manifest = (ROOT / "android" / "app" / "src" / "main" / "AndroidManifest.xml").read_text(encoding="utf-8")
        self.assertEqual(ET.fromstring(android_manifest).tag, "manifest")

    def test_manifest_uses_sdk_inputs_dumps_and_new_defaults(self) -> None:
        data = json.loads((ROOT / "recomplauncher.json").read_text(encoding="utf-8"))
        self.assertNotIn("game", data)
        self.assertNotIn("prepare", data)
        game = next(i for i in data["inputs"] if i["id"] == "game")
        self.assertEqual(game["formats"], [{"type": "file", "extensions": ["nds"]}])
        self.assertEqual(game["check"], {"ids": ["ACVE"]})
        self.assertEqual(game["dumps"][0], {"name": "USA (ACVE)", "size": 67108864, "crc32": "135737f6"})
        self.assertIn("{input:game}", data["start"]["args"])
        self.assertTrue(pr.REQUIRED_INI_KEYS.issubset(data["config"][0]["new"]))
        self.assertEqual(data["looks"]["graphics_key"], "dos_render_driver")
        self.assertEqual({a["open"] for a in data["actions"]}, {"saves", "screenshots", "logs"})
        self.assertEqual(data["exit_codes"]["0"], "ok")

    def test_media_kit_dimensions_and_formats(self) -> None:
        self.assertEqual(pr.validate_media(), [], "kit de midia incompleto")
        self.assertEqual(png_info(ART / "icon.png")[:2], (256, 256))
        self.assertEqual(png_info(ART / "icon.png")[2], 6, "icon.png deve ser RGBA")
        self.assertTrue({(256, 256), (64, 64), (48, 48), (32, 32), (16, 16)}.issubset(ico_sizes(ART / "icon.ico")))
        self.assertEqual(png_info(ART / "cover.png")[:2], (600, 900))
        self.assertEqual(jpeg_size(ART / "cover.jpg"), (600, 900))
        self.assertEqual(png_info(ART / "hero.png")[:2], (1920, 620))
        self.assertEqual(jpeg_size(ART / "hero.jpg"), (1920, 620))
        self.assertEqual(png_info(ART / "logo.png"), (1000, 500, 6))
        self.assertEqual(png_info(ART / "wallpaper.png")[:2], (1920, 1080))
        self.assertEqual(png_info(ART / "artwork.png")[:2], (1024, 1024))
        for shot in ("gameplay-dx12-pip.png", "imgui-menu-f1.png", "vulkan-spirv-ptbr.png"):
            self.assertEqual(png_info(SHOTS / shot)[:2], (1920, 1080), shot)
        for path in list(ART.iterdir()) + list(SHOTS.iterdir()):
            self.assertLess(path.stat().st_size, 1_800_000, f"{path.name} maior que 1.8 MB")

    def test_catalog_entry_points_to_the_media_kit(self) -> None:
        entry = json.loads((ART / "catalog-entry.json").read_text(encoding="utf-8"))
        self.assertEqual(entry["repo"], "Neguchads/cdos-nintendods-recomp")
        self.assertEqual(entry["origin"], "ds")
        self.assertEqual(entry["media_design"]["kind"], "ds")
        for slot, name in (("icon", "icon.png"), ("cover", "cover.jpg"), ("hero", "hero.jpg"), ("logo", "logo.png")):
            self.assertTrue(entry[slot].endswith(f"/assets/recomplauncher/{name}"), slot)
            self.assertTrue((ART / name).is_file(), name)

    def test_start_args_resolve_install_and_data_paths_independent_of_cwd(self) -> None:
        """RecompLauncher spawns runtime/nds_runner.exe with cwd={install}/runtime; args cannot rely on cwd={install}."""
        data = json.loads((ROOT / "recomplauncher.json").read_text(encoding="utf-8"))
        args = data["start"]["args"]

        self.assertEqual(args[0], "{data}/run/bios")
        self.assertEqual(args[args.index("--config") + 1], "{install}/game.toml")
        self.assertEqual(args[args.index("--ptbr-patch") + 1], "{install}/mods/ptbr/dos-ptbr.dospatch")

        for arg in args:
            if arg.startswith("{install}/"):
                rel = arg.removeprefix("{install}/")
                self.assertTrue((ROOT / rel).is_file(), f"Arquivo ausente para placeholder {arg}: {rel}")

    def test_validate_manifest_rejects_bare_relative_start_args(self) -> None:
        base = json.loads((ROOT / "recomplauncher.json").read_text(encoding="utf-8"))
        cases = [
            ("bios_rel", lambda a: a.__setitem__(0, "run/bios")),
            ("config_rel", lambda a: a.__setitem__(a.index("--config") + 1, "game.toml")),
            ("patch_rel", lambda a: a.__setitem__(a.index("--ptbr-patch") + 1, "mods/ptbr/dos-ptbr.dospatch")),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            for name, mutate in cases:
                with self.subTest(case=name):
                    mutated = json.loads(json.dumps(base))
                    mutate(mutated["start"]["args"])
                    path = Path(tmp) / f"{name}.json"
                    path.write_text(json.dumps(mutated), encoding="utf-8")
                    errors = pr.validate_manifest(path)
                    self.assertNotEqual(errors, [], f"validate_manifest aceitou caminho relativo em {name}")

    def test_stage_release_excludes_runtime_profiling_and_capture_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fake_root = Path(tmp) / "repo"
            for rel in (
                "recomplauncher.json",
                "game.toml",
                "play.bat",
                "README.md",
                "mods/ptbr/dos-ptbr.dospatch",
                "docs/RECOMPLAUNCHER.md",
            ):
                dst = fake_root / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes((ROOT / rel).read_bytes())
            (fake_root / "assets" / "recomplauncher").mkdir(parents=True, exist_ok=True)
            for item in (ROOT / "assets" / "recomplauncher").iterdir():
                if item.is_file():
                    (fake_root / "assets" / "recomplauncher" / item.name).write_bytes(item.read_bytes())

            runtime = fake_root / "runtime"
            runtime.mkdir(parents=True, exist_ok=True)
            (fake_root / "CastlevaniaDawnOfSorrow.exe").write_bytes(b"MZ-launcher")
            (runtime / "nds_runner.exe").write_bytes(b"MZ-stub")
            (runtime / "SDL3.dll").write_bytes(b"MZ-sdl3")
            for junk in ("profile.ndshp", "trace.jsonl", "frame.bmp", "snap.png", "debug.log"):
                (runtime / junk).write_bytes(b"junk")

            stage = Path(tmp) / "stage"
            pr.stage_release_tree(fake_root, out_dir=stage, make_zip=False)
            staged_runtime = {p.name for p in (stage / "runtime").iterdir()}
            self.assertEqual(staged_runtime, {"nds_runner.exe", "SDL3.dll"})
            self.assertTrue((stage / "CastlevaniaDawnOfSorrow.exe").is_file())
            self.assertTrue((stage / "assets" / "recomplauncher" / "icon.png").is_file())


if __name__ == "__main__":
    unittest.main()

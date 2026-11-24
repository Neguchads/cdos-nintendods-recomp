import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT/"tools"))
from rbs_cache import PhaseCache, key
from rbs_artifact import validate, REQUIRED


class CacheTests(unittest.TestCase):
    def test_hit_invalidation_missing_output_and_failed_build(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            inp, out = root/"in", root/"out"
            inp.write_text("a")
            cache = PhaseCache(root/"cache")
            calls = []
            def action():
                calls.append(1)
                out.write_text(inp.read_text())
            def step():
                return cache.run("stage", key([inp]), [out], action)
            self.assertTrue(step())
            self.assertFalse(step())
            inp.write_text("b")
            self.assertTrue(step())
            out.unlink()
            self.assertTrue(step())
            out.write_text("corrupt")
            self.assertTrue(step())
            def failure():
                raise RuntimeError("failure")
            with self.assertRaises(RuntimeError):
                cache.run("stage", "different", [out], failure)
            self.assertTrue(step())
            self.assertEqual(len(calls), 5)


class ArtifactTests(unittest.TestCase):
    def package(self, path, extra=None, corrupt=False):
        data = {n: b"MZsynthetic" if n.endswith((".exe",".dll")) else b"synthetic"
                for n in REQUIRED-{"SHA256SUMS.txt"}}
        data["recomplauncher.json"] = json.dumps({"repo":"Neguchads/cdos-nintendods-recomp",
            "format":1,"start":{"args":["{data}/run/bios","--config","{install}/game.toml"]}}).encode()
        if extra:
            data[extra] = b"forbidden"
        checks = "".join(f"{hashlib.sha256(v).hexdigest()}  {n}\n" for n,v in data.items())
        data["SHA256SUMS.txt"] = checks.encode()
        if corrupt:
            data["game.toml"] = b"corrupt"
        with zipfile.ZipFile(path,"w") as z:
            for n,v in data.items():
                z.writestr(n,v)

    def test_package_gate(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t)/"test.zip"
            self.package(p)
            validate(p)
            for bad in ["../escape", "runtime/secret.sav", "game/game.nds", "mods/intro/opening.mp4",
                        "runtime/extra.exe", "recompdata/saves/dos.sav"]:
                self.package(p, bad)
                with self.assertRaises(ValueError):
                    validate(p)
            self.package(p, corrupt=True)
            with self.assertRaises(ValueError):
                validate(p)


class SaveContractTests(unittest.TestCase):
    def test_legacy_data_paths_are_preserved(self):
        # Contract-level test, not an emulator migration or playthrough.
        manifest = json.loads((ROOT/"recomplauncher.json").read_text(encoding="utf-8"))
        args = manifest["start"]["args"]
        expected = {"--save-path":"{data}/saves/dos.sav",
                    "--runtime-settings-path":"{data}/saves/dos-settings.ini",
                    "--savestate-dir":"{data}/run/savestates"}
        for flag, value in expected.items():
            self.assertEqual(args[args.index(flag)+1], value)
        self.assertTrue(set(expected.values()) <= set(manifest["saves"]))
        for value in manifest["saves"]:
            self.assertTrue(value.startswith("{data}/"))
            self.assertNotIn("..", value.split("/"))

    def test_synthetic_player_data_separate_from_install(self):
        with tempfile.TemporaryDirectory() as t:
            base = Path(t)
            data, install = base/"data", base/"install"
            save = data/"saves/dos.sav"
            save.parent.mkdir(parents=True)
            save.write_bytes(bytes(range(256))*32)
            before = save.read_bytes()
            install.mkdir()
            (install/"game.toml").write_text("old")
            (install/"game.toml").write_text("new")
            self.assertEqual(save.read_bytes(), before)

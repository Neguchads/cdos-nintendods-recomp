"""Exercise the real release staging path with synthetic files, never a game."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import package_recomplauncher as package
from rbs_artifact import validate, REQUIRED


class ReleaseStagingTests(unittest.TestCase):
    def fixture(self, root):
        source = {"recomplauncher.json": (ROOT / "recomplauncher.json").read_bytes(),
                  "README.md": b"synthetic", "play.bat": b"synthetic",
                  "docs/RECOMPLAUNCHER.md": b"synthetic",
                  "mods/registry.json": b"{}"}
        for name in REQUIRED - {"SHA256SUMS.txt", "recomplauncher.json"}:
            source[name] = b"MZsynthetic" if name.endswith((".exe", ".dll")) else b"synthetic"
        for name in package.MEDIA_FILES:
            if name.startswith("assets/recomplauncher/"):
                source[name] = b"synthetic media placeholder"
        for name, content in source.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)

    def test_clean_install_update_and_unrelated_runtime_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "source"
            root.mkdir()
            self.fixture(root)
            save = root / "recompdata" / "saves" / "dos.sav"
            save.parent.mkdir(parents=True)
            save.write_bytes(b"synthetic old save")
            local = root / "runtime" / "private.sav"
            local.write_bytes(b"synthetic runtime data")
            (root / "runtime" / "extra.dll").write_bytes(b"MZunused")
            dest = root / "dist" / "synthetic"
            archive = dest.with_suffix(".zip")
            original = hashlib.sha256(save.read_bytes()).hexdigest()
            package.stage_release_tree(root, dest)
            validate(archive)
            self.assertFalse((dest / "runtime/private.sav").exists())
            self.assertFalse((dest / "runtime/extra.dll").exists())
            self.assertFalse((dest / "recompdata").exists())
            (root / "game.toml").write_text("updated synthetic config", encoding="utf-8")
            package.stage_release_tree(root, dest)
            validate(archive)
            self.assertEqual((dest / "game.toml").read_text(), "updated synthetic config")
            self.assertEqual(hashlib.sha256(save.read_bytes()).hexdigest(), original)
            self.assertEqual(local.read_bytes(), b"synthetic runtime data")
            unexpected = dest / "user-added.sav"
            unexpected.write_bytes(b"preserve me")
            with self.assertRaises(ValueError):
                package.stage_release_tree(root, dest)
            self.assertEqual(unexpected.read_bytes(), b"preserve me")

    def test_refuse_source_or_existing_user_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "source"
            root.mkdir()
            self.fixture(root)
            external = Path(tmp) / "unrelated"
            external.mkdir()
            important = external / "important.txt"
            important.write_text("preserve")
            for dest in (root, root.parent, root / "runtime", root / "recompdata", external):
                with self.subTest(dest=dest), self.assertRaises(ValueError):
                    package.stage_release_tree(root, dest)
            self.assertEqual(important.read_text(), "preserve")
            self.assertTrue((root / "recomplauncher.json").is_file())

if __name__ == "__main__":
    unittest.main()

"""Testes das Issues #16 (Custom Music .wav/.mp3/.ogg) e #7 (Widescreen Theatre / Smart Crop / 16:10)."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import list_bgm_tracks as lbt  # noqa: E402


class TestCustomMusicAndWidescreen(unittest.TestCase):
    def test_bgm_catalog_has_all_30_tracks_and_matching_rules(self) -> None:
        self.assertEqual(len(lbt.BGM_TRACKS), 30)
        self.assertEqual(lbt.match_track_key("11"), 11)
        self.assertEqual(lbt.match_track_key("11_pitch_black_intrusion"), 11)
        self.assertEqual(lbt.match_track_key("SDL_BGM_ST00_1_"), 11)
        self.assertEqual(lbt.match_track_key("sdl_bgm_st00_1"), 11)
        self.assertEqual(lbt.match_track_key("pitch_black_intrusion"), 11)
        self.assertEqual(lbt.match_track_key("SDL_BGM_BOSS1_"), 2)
        self.assertIsNone(lbt.match_track_key("not_a_real_track"))

    def test_scan_music_dir_supports_wav_mp3_ogg_and_rejects_traversal_in_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mdir = Path(tmp) / "music"
            mdir.mkdir()
            (mdir / "11_pitch_black_intrusion.ogg").write_bytes(b"OggS")
            (mdir / "SDL_BGM_BOSS1_.mp3").write_bytes(b"ID3")
            (mdir / "07.wav").write_bytes(b"RIFF")
            (mdir / "random_note.txt").write_text("ignored", encoding="utf-8")
            (mdir / "unmatched_song.mp3").write_bytes(b"ID3")

            rep = lbt.scan_music_dir(mdir)
            self.assertEqual(rep["errors"], [])
            self.assertEqual(rep["matched"], {7: "07.wav", 2: "SDL_BGM_BOSS1_.mp3", 11: "11_pitch_black_intrusion.ogg"})
            self.assertEqual(rep["unmatched"], ["unmatched_song.mp3"])

            # Manifest with path traversal must report an error
            (mdir / "music.json").write_text(
                json.dumps({"tracks": {"13": {"file": "../escape.mp3"}}}),
                encoding="utf-8",
            )
            rep_bad = lbt.scan_music_dir(mdir)
            self.assertTrue(any("invalid file" in e for e in rep_bad["errors"]))  # type: ignore[arg-type]

    def test_recomplauncher_manifest_exposes_widescreen_and_custom_music_options(self) -> None:
        manifest = json.loads((ROOT / "recomplauncher.json").read_text(encoding="utf-8"))
        new_cfg = manifest["config"][0]["new"]
        self.assertEqual(new_cfg["dos_custom_music"], "true")
        self.assertEqual(new_cfg["dos_custom_music_volume"], "100")
        self.assertEqual(new_cfg["dos_widescreen_crop_y"], "0")

        settings_by_id = {s["id"]: s for s in manifest["settings"]}
        layout_vals = {c["set"]["dos_layout"] for c in settings_by_id["layout"]["choices"]}
        self.assertIn("widescreen-theatre", layout_vals)
        aspect_vals = {c["set"]["dos_aspect_mode"] for c in settings_by_id["aspect_mode"]["choices"]}
        self.assertIn("smart-crop-16x9", aspect_vals)
        self.assertIn("balanced-16x10", aspect_vals)
        self.assertIn("custom_music", settings_by_id)
        self.assertIn("custom_music_volume", settings_by_id)
        self.assertIn("widescreen_crop_y", settings_by_id)


if __name__ == "__main__":
    unittest.main()

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

            # Manifest with path traversal or rooted/drive paths must report errors
            (mdir / "music.json").write_text(
                json.dumps(
                    {
                        "tracks": {
                            "13": {"file": "../escape.mp3"},
                            "14": {"file": "/root_escape.mp3"},
                            "15": {"file": "C:/drive_escape.wav"},
                        }
                    }
                ),
                encoding="utf-8",
            )
            rep_bad = lbt.scan_music_dir(mdir)
            self.assertEqual(len(rep_bad["errors"]), 3)
            self.assertTrue(all("invalid file" in e for e in rep_bad["errors"]))  # type: ignore[arg-type]

    def test_recomplauncher_manifest_exposes_widescreen_and_custom_music_options(self) -> None:
        manifest = json.loads((ROOT / "recomplauncher.json").read_text(encoding="utf-8"))
        new_cfg = manifest["config"][0]["new"]
        self.assertEqual(new_cfg["dos_custom_music"], "true")
        self.assertEqual(new_cfg["dos_custom_music_volume"], "100")
        self.assertEqual(new_cfg["dos_widescreen_crop_y"], "0")

        settings_by_id = {s["id"]: s for s in manifest["settings"]}
        layout_vals = {c["set"]["dos_layout"] for c in settings_by_id["layout"]["choices"]}
        self.assertIn("widescreen-theatre", layout_vals)
        self.assertIn("minimap-hud", layout_vals)
        aspect_vals = {c["set"]["dos_aspect_mode"] for c in settings_by_id["aspect_mode"]["choices"]}
        self.assertIn("smart-crop-16x9", aspect_vals)
        self.assertIn("balanced-16x10", aspect_vals)
        self.assertIn("custom_music", settings_by_id)
        self.assertIn("custom_music_volume", settings_by_id)
        self.assertIn("widescreen_crop_y", settings_by_id)

    def test_music_wizard_imports_arbitrary_names_and_configures_stage_and_jukebox(self) -> None:
        sys.path.insert(0, str(ROOT / "mods" / "music"))
        import configurar_musica as cm  # noqa: E402

        with tempfile.TemporaryDirectory() as tmp:
            src_dir = Path(tmp) / "Downloads"
            mdir = Path(tmp) / "music"
            src_dir.mkdir()
            mdir.mkdir()
            song1 = src_dir / "minha_musica_aleatoria.mp3"
            song2 = src_dir / "rock_castelo.ogg"
            song1.write_bytes(b"ID3test1")
            song2.write_bytes(b"OggStest2")

            n1 = cm.import_audio_file_to_music_dir(song1, mdir)
            n2 = cm.import_audio_file_to_music_dir(song2, mdir)
            self.assertEqual(n1, "minha_musica_aleatoria.mp3")
            self.assertTrue((mdir / n1).is_file())
            self.assertTrue((mdir / n2).is_file())

            cm.assign_track_in_manifest(mdir, 7, n1, loop=True, gain_db=-1.5)
            cm.configure_jukebox_in_manifest(mdir, [n1, n2], enabled=True, shuffle=True, append=False)

            rep = lbt.scan_music_dir(mdir)
            self.assertEqual(rep["errors"], [])
            self.assertEqual(rep["matched"], {7: "minha_musica_aleatoria.mp3"})
            self.assertTrue(rep["jukebox_enabled"])
            self.assertEqual(rep["jukebox_playlist"], ["minha_musica_aleatoria.mp3", "rock_castelo.ogg"])
            self.assertTrue((ROOT / "mods" / "music" / "Configurar_Musica.bat").is_file())

    def test_recomplauncher_manifest_exposes_bandlimited_filter_and_true_widescreen(self) -> None:
        data = json.loads((ROOT / "recomplauncher.json").read_text(encoding="utf-8"))
        self.assertEqual(data["config"][0]["new"].get("dos_true_widescreen"), "false")
        settings = {s["id"]: s for s in data["settings"]}
        self.assertIn("true_widescreen", settings)
        self.assertEqual(settings["true_widescreen"]["defaults"].get("dos_true_widescreen"), "false")
        hd_values = {c["set"].get("dos_hd_filter") for c in settings["hd_filter"]["choices"]}
        self.assertEqual(
            hd_values,
            {
                "pixellate",
                "pixel-aa",
                "bandlimited-pixel",
                "mmpx",
                "omniscale",
                "scalefx-hybrid",
                "nearest",
                "bilinear",
            },
        )
        self.assertEqual(data["config"][0]["new"].get("dos_hd_filter"), "pixellate")
        self.assertEqual(data["config"][0]["new"].get("dos_anti_dither"), "false")
        self.assertEqual(data["config"][0]["new"].get("dos_sharpen"), "off")
        self.assertIn("anti_dither", settings)

    def test_recomplauncher_manifest_exposes_expanded_display_and_graphics_suite(self) -> None:
        data = json.loads((ROOT / "recomplauncher.json").read_text(encoding="utf-8"))
        new_cfg = data["config"][0]["new"]
        for key, expected in [
            ("dos_wide_hud_mode", "edge"),
            ("dos_display_index", "-1"),
            ("dos_window_scale", "0"),
            ("dos_safe_zone", "0"),
            ("dos_frame_interpolation", "false"),
            ("dos_vsync", "off"),
            ("dos_post_fx_intensity", "100"),
            ("dos_crt_curvature", "0"),
            ("dos_antialiasing", "0"),
            ("dos_gamma", "100"),
            ("dos_color_temp", "0"),
            ("dos_bloom", "0"),
        ]:
            self.assertEqual(new_cfg.get(key), expected, f"missing/wrong default for {key}")

        settings = {s["id"]: s for s in data["settings"]}
        aspect_vals = {c["set"].get("dos_aspect_mode") for c in settings["aspect_mode"]["choices"]}
        self.assertIn("ultrawide-21x9", aspect_vals)
        vsync_vals = {c["set"].get("dos_vsync") for c in settings["vsync"]["choices"]}
        self.assertEqual(vsync_vals, {"off", "on", "adaptive", "sync60"})
        for sid in [
            "wide_hud_mode",
            "window_scale",
            "safe_zone",
            "frame_interpolation",
            "post_fx_intensity",
            "crt_curvature",
            "antialiasing",
            "gamma",
            "color_temp",
            "bloom",
        ]:
            self.assertIn(sid, settings, f"missing setting {sid}")


if __name__ == "__main__":
    unittest.main()

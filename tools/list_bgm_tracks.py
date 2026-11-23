#!/usr/bin/env python3
"""Lista as 30 faixas BGM de Castlevania: Dawn of Sorrow e valida arquivos em mods/music/."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BGM_TRACKS: list[dict[str, object]] = [
    {"id": 0, "sdat_name": "SDL_BGM_ARR1_", "slug": "vampire_killer_arr", "title": "Vampire Killer (Arranged)", "default_loop": True},
    {"id": 1, "sdat_name": "SDL_BGM_ARR2_", "slug": "bloody_tears_arr", "title": "Bloody Tears (Arranged)", "default_loop": True},
    {"id": 2, "sdat_name": "SDL_BGM_BOSS1_", "slug": "into_the_dark_night", "title": "Into the Dark Night (Boss 1)", "default_loop": True},
    {"id": 3, "sdat_name": "SDL_BGM_BOSS2_", "slug": "evil_invitation", "title": "Evil Invitation (Boss 2)", "default_loop": True},
    {"id": 4, "sdat_name": "SDL_BGM_ENDING_", "slug": "ending", "title": "Ending Theme", "default_loop": False},
    {"id": 5, "sdat_name": "SDL_BGM_EV_BOSS_", "slug": "event_boss", "title": "Event Boss / Tension", "default_loop": True},
    {"id": 6, "sdat_name": "SDL_BGM_L2_BOSS_", "slug": "final_boss_menace", "title": "Final Boss (Menace)", "default_loop": True},
    {"id": 7, "sdat_name": "SDL_BGM_NAME_", "slug": "file_select", "title": "Name Entry / File Select", "default_loop": True},
    {"id": 8, "sdat_name": "SDS_BGM_OVER_", "slug": "game_over", "title": "Game Over", "default_loop": False},
    {"id": 9, "sdat_name": "SDL_BGM_PRE_", "slug": "prelude", "title": "Prelude / Prologue", "default_loop": True},
    {"id": 10, "sdat_name": "SDL_BGM_SHOP_", "slug": "hammer_shop", "title": "Hammer's Shop", "default_loop": True},
    {"id": 11, "sdat_name": "SDL_BGM_ST00_1_", "slug": "pitch_black_intrusion", "title": "Pitch Black Intrusion (Lost Village 1)", "default_loop": True},
    {"id": 12, "sdat_name": "SDL_BGM_ST00_2_", "slug": "lost_village_2", "title": "Lost Village (Interior)", "default_loop": True},
    {"id": 13, "sdat_name": "SDL_BGM_ST01_", "slug": "draculas_tears", "title": "Dracula's Tears (Wizardry Lab)", "default_loop": True},
    {"id": 14, "sdat_name": "SDL_BGM_ST02_", "slug": "garden_of_madness", "title": "Garden of Madness", "default_loop": True},
    {"id": 15, "sdat_name": "SDL_BGM_ST03_", "slug": "dark_chapel", "title": "Dark Chapel (Chapel)", "default_loop": True},
    {"id": 16, "sdat_name": "SDL_BGM_ST04_", "slug": "demon_guest_house", "title": "Demon Guest House", "default_loop": True},
    {"id": 17, "sdat_name": "SDL_BGM_ST05_", "slug": "condemned_tower", "title": "Condemned Tower", "default_loop": True},
    {"id": 18, "sdat_name": "SDL_BGM_ST06_", "slug": "subterranean_hell", "title": "Subterranean Hell", "default_loop": True},
    {"id": 19, "sdat_name": "SDL_BGM_ST07_", "slug": "silenced_ruins", "title": "Silenced Ruins", "default_loop": True},
    {"id": 20, "sdat_name": "SDL_BGM_ST08_", "slug": "cursed_clock_tower", "title": "Cursed Clock Tower", "default_loop": True},
    {"id": 21, "sdat_name": "SDL_BGM_ST09_", "slug": "the_pinnacle", "title": "The Pinnacle", "default_loop": True},
    {"id": 22, "sdat_name": "SDL_BGM_ST10_", "slug": "mine_of_judgment", "title": "Mine of Judgment", "default_loop": True},
    {"id": 23, "sdat_name": "SDL_BGM_ST11_", "slug": "the_abyss", "title": "The Abyss", "default_loop": True},
    {"id": 24, "sdat_name": "SDL_BGM_ST12_", "slug": "abyss_depths", "title": "Abyss Depths / Extra", "default_loop": True},
    {"id": 25, "sdat_name": "SDS_BGM_STAFF_", "slug": "credits_staff", "title": "Credits / Staff Roll", "default_loop": False},
    {"id": 26, "sdat_name": "SDL_BGM_TR_BOSS1_", "slug": "boss_theme_3", "title": "Scarlet Battle Soul (Boss 3)", "default_loop": True},
    {"id": 27, "sdat_name": "SDL_BGM_TR_BOSS2_", "slug": "boss_theme_4", "title": "Last Battle / Death & Julius", "default_loop": True},
    {"id": 28, "sdat_name": "SDL_BGM_WIND_", "slug": "wind_ambience", "title": "Wind Ambience", "default_loop": True},
    {"id": 29, "sdat_name": "SDL_BGM_YOKO_", "slug": "yoko_shop", "title": "Yoko's Soul Synthesis", "default_loop": True},
]

SUPPORTED_EXTS = {".wav", ".mp3", ".ogg"}


def match_track_key(key: str) -> int | None:
    lc = key.strip().lower()
    if not lc:
        return None
    stripped = lc.strip("_")
    if lc[0].isdigit():
        p = 0
        while p < len(lc) and lc[p].isdigit():
            p += 1
        if p == len(lc) or lc[p] in ("_", "-", " "):
            n = int(lc[:p])
            if 0 <= n < len(BGM_TRACKS):
                return n
    for t in BGM_TRACKS:
        sdat_lc = str(t["sdat_name"]).lower()
        if lc == sdat_lc or stripped == sdat_lc.strip("_") or lc == t["slug"] or stripped == t["slug"]:
            return int(t["id"])  # type: ignore[arg-type]
    return None


def scan_music_dir(music_dir: Path) -> dict[str, object]:
    matched: dict[int, str] = {}
    unmatched: list[str] = []
    errors: list[str] = []

    if not music_dir.is_dir():
        return {"dir": str(music_dir), "matched": matched, "unmatched": unmatched, "errors": ["directory not found"]}

    for p in sorted(music_dir.iterdir()):
        if not p.is_file() or p.suffix.lower() not in SUPPORTED_EXTS:
            continue
        tid = match_track_key(p.stem)
        if tid is None:
            unmatched.append(p.name)
        else:
            matched[tid] = p.name

    manifest = music_dir / "music.json"
    if manifest.is_file():
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            tracks = data.get("tracks", {})
            if isinstance(tracks, dict):
                for k, v in tracks.items():
                    tid = match_track_key(str(k))
                    if tid is None:
                        errors.append(f"music.json: unknown track key '{k}'")
                        continue
                    rel = str(v.get("file", "")) if isinstance(v, dict) else ""
                    if not rel or ".." in rel or Path(rel).is_absolute() or Path(rel).suffix.lower() not in SUPPORTED_EXTS:
                        errors.append(f"music.json: invalid file '{rel}' for track '{k}'")
                        continue
                    if not (music_dir / rel).is_file():
                        errors.append(f"music.json: missing file '{rel}' for track '{k}'")
                        continue
                    matched[tid] = rel
        except Exception as exc:  # noqa: BLE001
            errors.append(f"music.json parse error: {exc}")

    return {"dir": str(music_dir), "matched": matched, "unmatched": unmatched, "errors": errors}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scan", type=Path, default=None, help="Diretorio mods/music para validar")
    ap.add_argument("--json", action="store_true", help="Saida em JSON")
    args = ap.parse_args(argv)

    if args.scan is not None:
        rep = scan_music_dir(args.scan)
        if args.json:
            print(json.dumps(rep, indent=2))
        else:
            print(f"[music] dir={rep['dir']} matched={len(rep['matched'])} unmatched={len(rep['unmatched'])} errors={len(rep['errors'])}")
            for tid, fname in sorted(rep["matched"].items()):  # type: ignore[union-attr]
                t = BGM_TRACKS[tid]
                print(f"  #{tid:02d} {t['sdat_name']:18s} ({t['title']}) <- {fname}")
            for u in rep["unmatched"]:  # type: ignore[union-attr]
                print(f"  [ignored] {u}")
            for e in rep["errors"]:  # type: ignore[union-attr]
                print(f"  [error] {e}")
        return 1 if rep["errors"] else 0

    if args.json:
        print(json.dumps(BGM_TRACKS, indent=2))
    else:
        for t in BGM_TRACKS:
            print(f"#{int(t['id']):02d}  {str(t['sdat_name']):18s}  {str(t['slug']):24s}  {t['title']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

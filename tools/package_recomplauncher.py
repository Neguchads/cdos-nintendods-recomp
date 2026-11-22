#!/usr/bin/env python3
"""Valida recomplauncher.json e empacota distribuicao limpa (sem ROM) para RecompLauncher."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "recomplauncher.json"

REQUIRED_INI_KEYS = {
    "dos_ui_language",
    "dos_game_language",
    "dos_skip_launcher",
    "dos_fullscreen",
    "dos_layout",
    "dos_pip_main",
    "dos_pip_corner",
    "dos_pip_size",
    "dos_pip_opacity",
    "dos_aspect_mode",
    "dos_render_driver",
    "dos_vsync",
    "dos_hd_filter",
    "dos_color_mode",
    "dos_sharpen",
    "dos_post_fx",
    "dos_brightness",
    "dos_contrast",
    "dos_saturation",
    "dos_vignette",
    "dos_hud_mode",
    "dos_pause_on_menu",
    "dos_pause_unfocused",
    "dos_audio_enabled",
    "dos_audio_mode",
    "dos_audio_volume",
    "dos_audio_fx",
    "dos_mute_unfocused",
    "dos_button_prompts",
    "dos_stick_deadzone",
}

FORBIDDEN_EXTENSIONS = {".nds", ".gba", ".cia", ".3ds"}


def validate_manifest(manifest_path: Path = MANIFEST_PATH) -> list[str]:
    """Valida campos obrigatorios, schema v1 e paridade de chaves INI."""
    errors: list[str] = []
    if not manifest_path.is_file():
        return [f"Manifesto ausente: {manifest_path}"]

    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"JSON invalido em {manifest_path}: {exc}"]

    if data.get("format") != 1:
        errors.append(f"Campo 'format' deve ser 1 (obtido {data.get('format')!r})")
    if not str(data.get("$schema", "")).startswith("https://"):
        errors.append("Campo '$schema' ausente ou invalido")
    if not data.get("name"):
        errors.append("Campo 'name' vazio")

    game = data.get("game", {})
    check = game.get("check", {})
    if game.get("kind") != "rom" or check.get("sha1") != "47530ff87e608f88105a314fdf36dc385f8dec94":
        errors.append("Bloco 'game.check.sha1' nao confere com ACVE USA (47530ff8...)")

    for sec in ("prepare", "start", "saves", "folders", "config", "settings"):
        if sec not in data:
            errors.append(f"Secao obrigatoria ausente: '{sec}'")

    start_args = data.get("start", {}).get("args", [])
    if "--ptbr-patch" not in start_args:
        errors.append("start.args deve repassar --ptbr-patch mods/ptbr/dos-ptbr.dospatch")

    cfg_list = data.get("config", [])
    cfg_paths = [f.get("path", "") for c in cfg_list for f in c.get("file", [])]
    if "{data}/saves/dos-settings.ini" not in cfg_paths:
        errors.append("config[].file deve apontar para {data}/saves/dos-settings.ini")

    seen_keys: set[str] = set()
    for entry in data.get("settings", []):
        eid = entry.get("id", "<sem-id>")
        defaults = entry.get("defaults", {})
        if not isinstance(defaults, dict) or not defaults:
            errors.append(f"Setting '{eid}' sem bloco 'defaults'")
            continue
        seen_keys.update(defaults.keys())
        if "slider" in entry:
            sl = entry["slider"]
            if "key" not in sl or sl["min"] >= sl["max"]:
                errors.append(f"Slider invalido em '{eid}'")
            else:
                seen_keys.add(sl["key"])
        elif "choices" in entry:
            if not entry["choices"]:
                errors.append(f"Choices vazio em '{eid}'")
            for ch in entry["choices"]:
                seen_keys.update(ch.get("set", {}).keys())
        else:
            errors.append(f"Setting '{eid}' precisa definir 'choices' ou 'slider'")

    missing = sorted(REQUIRED_INI_KEYS - seen_keys)
    if missing:
        errors.append(f"Chaves INI ausentes em 'settings': {', '.join(missing)}")

    return errors


def stage_release_tree(
    root: Path = ROOT,
    out_dir: Path | None = None,
    make_zip: bool = True,
) -> Path:
    """Cria pacote distribuivel sem ROM proprietaria pronto para RecompLauncher."""
    errors = validate_manifest(root / "recomplauncher.json")
    if errors:
        raise RuntimeError("Falha na validacao de recomplauncher.json:\n- " + "\n- ".join(errors))

    runtime_dir = root / "runtime"
    required_files = [
        root / "recomplauncher.json",
        root / "game.toml",
        root / "play.bat",
        root / "README.md",
        root / "mods" / "ptbr" / "dos-ptbr.dospatch",
        root / "docs" / "RECOMPLAUNCHER.md",
        runtime_dir / "nds_runner.exe",
        runtime_dir / "SDL3.dll",
    ]
    for path in required_files:
        if not path.is_file():
            raise FileNotFoundError(f"Artefato obrigatorio ausente para pacote: {path}")

    target_dir = out_dir or (root / "dist" / "castlevania-dos-recomp-win64")
    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    copy_items = [
        ("recomplauncher.json", False),
        ("game.toml", False),
        ("play.bat", False),
        ("README.md", False),
        ("mods/ptbr/dos-ptbr.dospatch", False),
        ("docs/RECOMPLAUNCHER.md", False),
        ("docs/MULTIPLATFORM.md", True),
        ("runtime", False),
    ]
    for rel, optional in copy_items:
        src = root / rel
        if not src.exists():
            if optional:
                continue
            raise FileNotFoundError(f"Origem ausente: {src}")
        dst = target_dir / rel
        if src.is_dir():
            shutil.copytree(
                src,
                dst,
                ignore=shutil.ignore_patterns("*.log", "*.tmp", "dispatch_miss*"),
            )
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    (target_dir / "run" / "bios").mkdir(parents=True, exist_ok=True)
    (target_dir / "run" / "savestates").mkdir(parents=True, exist_ok=True)
    (target_dir / "saves").mkdir(parents=True, exist_ok=True)

    # Garante zero ROM proprietaria ou save pessoal no pacote gerado.
    for p in target_dir.rglob("*"):
        if p.is_file() and p.suffix.lower() in FORBIDDEN_EXTENSIONS:
            raise RuntimeError(f"Arquivo proibido encontrado no staging: {p}")

    sha256_lines: list[str] = []
    for p in sorted(target_dir.rglob("*")):
        if p.is_file():
            digest = hashlib.sha256(p.read_bytes()).hexdigest()
            sha256_lines.append(f"{digest}  {p.relative_to(target_dir).as_posix()}")
    (target_dir / "SHA256SUMS.txt").write_text("\n".join(sha256_lines) + "\n", encoding="utf-8")

    if make_zip:
        zip_path = target_dir.parent / f"{target_dir.name}.zip"
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for p in sorted(target_dir.rglob("*")):
                if p.is_file():
                    zf.write(p, arcname=p.relative_to(target_dir))
        print(f"[package] zip criado: {zip_path} ({zip_path.stat().st_size} bytes)")

    print(f"[package] staging pronto em: {target_dir}")
    return target_dir


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--validate-only", action="store_true", help="Apenas valida recomplauncher.json")
    ap.add_argument("--no-zip", action="store_true", help="Nao compacta em .zip")
    ap.add_argument("--out", type=Path, default=None, help="Pasta destino de staging")
    args = ap.parse_args(argv)

    errs = validate_manifest()
    if errs:
        for e in errs:
            print(f"[erro] {e}", file=sys.stderr)
        return 1
    print(f"[recomplauncher] OK: {MANIFEST_PATH} valido (todas as {len(REQUIRED_INI_KEYS)} chaves INI cobertas)")

    if args.validate_only:
        return 0

    stage_release_tree(ROOT, out_dir=args.out, make_zip=not args.no_zip)
    return 0


if __name__ == "__main__":
    sys.exit(main())

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
    "dos_content_profile",
    "dos_enhanced_intro",
    "dos_skip_launcher",
    "dos_fullscreen",
    "dos_layout",
    "dos_pip_main",
    "dos_pip_corner",
    "dos_pip_size",
    "dos_pip_opacity",
    "dos_aspect_mode",
    "dos_widescreen_crop_y",
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
    "dos_custom_music",
    "dos_custom_music_volume",
    "dos_mute_unfocused",
    "dos_button_prompts",
    "dos_stick_deadzone",
}

FORBIDDEN_EXTENSIONS = {".nds", ".rom", ".gba", ".cia", ".3ds", ".sav", ".state", ".savestate"}

SCHEMA_URL = "https://recomplauncher.com/schema/recomplauncher.json"
REPO = "Neguchads/cdos-nintendods-recomp"
ROM_CRC32 = "135737f6"
ROM_SIZE = 67108864
MEDIA_FILES = [
    "assets/recomplauncher/icon.png",
    "assets/recomplauncher/icon.ico",
    "assets/recomplauncher/cover.png",
    "assets/recomplauncher/cover.jpg",
    "assets/recomplauncher/hero.png",
    "assets/recomplauncher/hero.jpg",
    "assets/recomplauncher/logo.png",
    "assets/recomplauncher/wallpaper.png",
    "assets/recomplauncher/artwork.png",
    "assets/recomplauncher/catalog-entry.json",
    "assets/screenshots/gameplay-dx12-pip.png",
    "assets/screenshots/imgui-menu-f1.png",
    "assets/screenshots/vulkan-spirv-ptbr.png",
]


def validate_manifest(manifest_path: Path = MANIFEST_PATH) -> list[str]:
    """Valida o manifesto no formato atual do SDK do RecompLauncher (inputs, config.new, looks...)."""
    errors: list[str] = []
    if not manifest_path.is_file():
        return [f"Manifesto ausente: {manifest_path}"]

    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"JSON invalido em {manifest_path}: {exc}"]

    if data.get("format") != 1:
        errors.append(f"Campo 'format' deve ser 1 (obtido {data.get('format')!r})")
    if data.get("$schema") != SCHEMA_URL:
        errors.append(f"Campo '$schema' deve ser {SCHEMA_URL}")
    if not data.get("name"):
        errors.append("Campo 'name' vazio")
    if data.get("repo") != REPO:
        errors.append(f"Campo 'repo' deve ser {REPO}")
    if "game" in data:
        errors.append("Use 'inputs' no lugar de 'game' (o RecompLauncher 1.0 para de ler 'game')")
    if "prepare" in data:
        errors.append("Nao use 'prepare': o runtime nao tem etapa de preparo sem janela")

    inputs = data.get("inputs", [])
    game_input = next((i for i in inputs if i.get("id") == "game"), None)
    if game_input is None:
        errors.append("Falta o input 'game'")
    else:
        exts = [e for f in game_input.get("formats", []) for e in f.get("extensions", [])]
        if exts != ["nds"]:
            errors.append(f"inputs[game].formats deve aceitar so .nds (obtido {exts})")
        if game_input.get("check", {}).get("ids") != ["ACVE"]:
            errors.append("inputs[game].check.ids deve ser ['ACVE']")
        dumps = game_input.get("dumps", [])
        if not dumps or dumps[0].get("crc32") != ROM_CRC32 or dumps[0].get("size") != ROM_SIZE:
            errors.append(f"inputs[game].dumps[0] deve ter crc32 {ROM_CRC32} e size {ROM_SIZE}")

    for sec in ("start", "saves", "folders", "config", "settings", "actions", "looks", "system", "exit_codes"):
        if sec not in data:
            errors.append(f"Secao obrigatoria ausente: '{sec}'")

    start_args = data.get("start", {}).get("args", [])
    for needed in ("--ptbr-patch", "--rom", "{input:game}", "--config"):
        if needed not in start_args:
            errors.append(f"start.args deve conter {needed}")
    if any("{game}" in a for a in start_args):
        errors.append("start.args nao pode usar {game}; use {input:game}")
    # RecompLauncher executa start.program com cwd = {install}/runtime; caminhos relativos quebram.
    if not start_args or start_args[0] != "{data}/run/bios":
        errors.append("start.args[0] deve ser '{data}/run/bios' (cwd do RecompLauncher e runtime/)")
    for flag, expected in (
        ("--config", "{install}/game.toml"),
        ("--ptbr-patch", "{install}/mods/ptbr/dos-ptbr.dospatch"),
        ("--definitive-en-patch", "{install}/mods/definitive/dos-definitive-en.dospatch"),
        ("--definitive-ptbr-patch", "{install}/mods/definitive/dos-definitive-ptbr.dospatch"),
        ("--intro-video", "{install}/mods/intro/opening.mp4"),
        ("--mod-registry", "{install}/mods/registry.json"),
        ("--mod-data-dir", "{data}/mods"),
        # Runtime user data must never be written into the read-only install tree.
        ("--runtime-settings-path", "{data}/saves/dos-settings.ini"),
        ("--savestate-dir", "{data}/run/savestates"),
        ("--save-path", "{data}/saves/dos.sav"),
        ("--firmware-state-path", "{data}/run/firmware_state.bin"),
    ):
        if flag not in start_args:
            errors.append(f"start.args deve conter {flag}")
        else:
            idx = start_args.index(flag)
            actual = start_args[idx + 1] if idx + 1 < len(start_args) else None
            if actual != expected:
                errors.append(f"start.args apos {flag} deve ser {expected!r} (obtido {actual!r})")

    cfg_list = data.get("config", [])
    cfg_paths = [f.get("path", "") for c in cfg_list for f in c.get("file", [])]
    if "{data}/saves/dos-settings.ini" not in cfg_paths:
        errors.append("config[].file deve apontar para {data}/saves/dos-settings.ini")
    new_keys = set(cfg_list[0].get("new", {})) if cfg_list else set()
    missing_new = sorted(REQUIRED_INI_KEYS - new_keys)
    if missing_new:
        errors.append(f"config[0].new sem as chaves: {', '.join(missing_new)}")

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
            if len(entry["choices"]) < 2:
                errors.append(f"'{eid}' precisa de pelo menos 2 choices")
            for ch in entry["choices"]:
                seen_keys.update(ch.get("set", {}).keys())
        else:
            errors.append(f"Setting '{eid}' precisa definir 'choices' ou 'slider'")

    missing = sorted(REQUIRED_INI_KEYS - seen_keys)
    if missing:
        errors.append(f"Chaves INI ausentes em 'settings': {', '.join(missing)}")

    folder_names = set(data.get("folders", {}))
    for act in data.get("actions", []):
        if act.get("open") and act["open"] not in folder_names:
            errors.append(f"actions[{act.get('id')}].open aponta para pasta inexistente: {act['open']}")

    errors.extend(validate_media())
    return errors


def validate_media(root: Path = ROOT) -> list[str]:
    """Confere que o kit de midia do RecompLauncher existe (dimensoes: ver tools/prepare_media_assets.py)."""
    errors: list[str] = []
    for rel in MEDIA_FILES:
        if not (root / rel).is_file():
            errors.append(f"Arquivo de midia ausente: {rel}")
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

    root = root.resolve()
    # The runtime and media trees may contain local saves, logs, game files or
    # arbitrary DLLs. Package an explicit file list, not recursive directories.
    copy_items = [
        ("recomplauncher.json", False),
        ("CastlevaniaDawnOfSorrow.exe", False),
        ("game.toml", False),
        ("play.bat", False),
        ("README.md", False),
        ("mods/ptbr/dos-ptbr.dospatch", False),
        ("mods/definitive/dos-definitive-en.dospatch", False),
        ("mods/definitive/dos-definitive-ptbr.dospatch", False),
        ("mods/registry.json", False),
        ("mods/catalog.json", True),
        ("mods/music/README.md", True),
        ("mods/music/configurar_musica.py", True),
        ("mods/music/Configurar_Musica.bat", True),
        ("docs/RECOMPLAUNCHER.md", False),
        ("docs/CREDITS.md", True),
        ("docs/MULTIPLATFORM.md", True),
        ("docs/LICENSE_REVIEW.md", True),
        ("runtime/nds_runner.exe", False),
        ("runtime/SDL3.dll", False),
        ("runtime/libc++.dll", False),
        ("runtime/libunwind.dll", False),
        *[(name, False) for name in MEDIA_FILES if name.startswith("assets/recomplauncher/")],
    ]
    selected = []
    for rel, optional in copy_items:
        src = root / rel
        if not src.exists() and optional:
            continue
        if not src.is_file():
            raise FileNotFoundError(f"Artefato obrigatorio ausente para pacote: {src}")
        if not src.resolve().is_relative_to(root) or any(
            p.is_symlink() for p in (src, *src.parents) if p != root and p.is_relative_to(root)
        ):
            raise ValueError(f"Symlink nao permitido no pacote: {rel}")
        selected.append((rel, src))

    requested = Path(out_dir) if out_dir is not None else root / "dist" / "castlevania-dos-recomp-win64"
    if requested.is_symlink():
        raise ValueError("Destino de staging nao pode ser symlink")
    target_dir = requested.resolve()
    dist = root / "dist"
    if target_dir == root or target_dir in root.parents or (
        target_dir.is_relative_to(root) and (target_dir == dist or not target_dir.is_relative_to(dist))
    ):
        raise ValueError("Destino de staging sobrepoe codigo-fonte ou dados do jogador")
    if target_dir.exists():
        # Never delete a user directory. Only replace an intact previous package
        # whose checksum manifest covers exactly every staged file.
        if not target_dir.is_dir() or any(p.is_symlink() for p in target_dir.rglob("*")):
            raise ValueError("Destino existente nao e staging seguro")
        existing = {p.relative_to(target_dir).as_posix(): p for p in target_dir.rglob("*") if p.is_file()}
        if existing:
            marker = existing.get("SHA256SUMS.txt")
            if marker is None or "recomplauncher.json" not in existing:
                raise ValueError("Destino existente nao foi gerado pelo empacotador")
            try:
                previous_manifest = json.loads(existing["recomplauncher.json"].read_text(encoding="utf-8"))
                checks = dict((name, digest) for digest, name in (
                    line.split("  ", 1) for line in marker.read_text(encoding="utf-8").splitlines()
                ))
            except (OSError, ValueError) as exc:
                raise ValueError("Staging anterior invalido; nao sera removido") from exc
            if previous_manifest.get("repo") != REPO or set(checks) != set(existing) - {"SHA256SUMS.txt"}:
                raise ValueError("Staging anterior possui arquivos adicionais ou checksum incompleto")
            for name, digest in checks.items():
                if hashlib.sha256(existing[name].read_bytes()).hexdigest() != digest:
                    raise ValueError(f"Staging anterior modificado; preservado: {name}")
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    for rel, src in selected:
        dst = target_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    # Pasta de BIOS (vazia): o runner a recebe como argumento. Saves e savestates vao para {data}
    # (recompdata/), que o RecompLauncher cria; nunca envie 'recompdata' na release.
    (target_dir / "run" / "bios").mkdir(parents=True, exist_ok=True)

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

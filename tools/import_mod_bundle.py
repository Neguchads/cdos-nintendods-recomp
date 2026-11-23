#!/usr/bin/env python3
"""Importa, classifica e valida o pacote de mods CDOS NDS (ZIP ou pasta) sem alterar a ROM USA."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import vcdiff_ips  # noqa: E402
import mod_resolver  # noqa: E402

EXPECTED_DOS_ROM_SIZE = 67_108_864
EXPECTED_POR_ROM_SIZE = 134_217_728

# Limites de seguranca contra zip bomb e path traversal
MAX_ZIP_ENTRIES = 256
MAX_ZIP_ENTRY_BYTES = 160 * 1024 * 1024  # 160 MiB
MAX_ZIP_TOTAL_BYTES = 512 * 1024 * 1024  # 512 MiB
MAX_ZIP_RATIO = 200.0

# Metadados conhecidos de proveniencia e creditos verificados
KNOWN_MOD_CREDITS: dict[str, dict[str, object]] = {
    "67c1b8958725d79b78274f1429b2e97784c0f83b0641a7fcf0aa529e05af0aef": {
        "id": "dos-definitive-edition",
        "name": "Castlevania: Dawn of Sorrow - Definitive Edition",
        "authors": [
            "Thirteen 1355 (Definitive Edition compilation & QoL)",
            "ShadowOne333, acediez, JohannGralog, Justin3009, DarkSamus993 (Dawn of Dignity portraits; original art by Ayami Kojima)",
            "LagoLunatic (No Required Touch Screen & Fixed Luck)",
        ],
        "source_url": "https://retro-replay.com/romhacking/hacks/castlevania-dawn-of-sorrow-definitive-edition/",
        "local_filename": "CVDawnDefinitive.xdelta",
    },
    "a5e3174ef9f7c2dd7a7e9f0e99f206414f1371d64064c535644b62c0e8dbb592": {
        "id": "dos-no-required-touch-v1.1",
        "name": "Castlevania: Dawn of Sorrow - No Required Touch Screen v1.1",
        "authors": ["LagoLunatic"],
        "source_url": "https://github.com/LagoLunatic/DSVEdit",
        "local_filename": "dos_no_required_touch_screen_v1.1.ips",
    },
    "b0eee73409bca9191eb57ae110c15d2ed2e3394cb4890601bedbfdd34fc47c45": {
        "id": "dos-ai-opening-video",
        "name": "Castlevania Dominus AI Intro Video (Dawn of Sorrow)",
        "authors": ["Joedu22256"],
        "source_url": "https://www.nexusmods.com/castlevaniadominuscollection/mods/12",
        "local_filename": "opening.mp4",
    },
}


def detect_media_signature(data: bytes) -> str:
    """Detecta tipo binario real por assinatura (nao confia na extensao)."""
    patch_fmt = vcdiff_ips.detect_patch_format(data)
    if patch_fmt != "unknown":
        return patch_fmt
    if len(data) >= 12 and data[4:8] == b"ftyp":
        return "mp4"
    if len(data) >= 4 and data[:4] == b"\x1a\x45\xdf\xa3":
        return "webm_ebml"
    return "other"


def _safe_filename(name: str) -> str:
    leaf = Path(name.replace("\\", "/")).name
    cleaned = "".join(ch if (ch.isalnum() or ch in "._- ") else "_" for ch in leaf).strip()
    if not cleaned or cleaned in (".", "..") or ".." in cleaned:
        raise ValueError(f"Nome de arquivo inseguro no pacote: {name!r}")
    return cleaned


def classify_entry(rel_path: str, data: bytes) -> dict[str, object]:
    """Classifica um arquivo do pacote quanto a compatibilidade com Castlevania: DoS Recomp."""
    norm = rel_path.replace("\\", "/")
    lower = norm.lower()
    sha256 = hashlib.sha256(data).hexdigest()
    sig = detect_media_signature(data)
    credit = KNOWN_MOD_CREDITS.get(sha256, {})

    entry: dict[str, object] = {
        "source_path": norm,
        "size_bytes": len(data),
        "sha256": sha256,
        "detected_format": sig,
        "status": "ignored",
        "role": "unclassified",
        "reason": "",
    }
    if credit:
        entry["mod_id"] = credit["id"]
        entry["name"] = credit["name"]
        entry["authors"] = credit["authors"]
        entry["source_url"] = credit["source_url"]

    if sig == "xdelta1":
        entry["status"] = "rejected"
        entry["role"] = "xdelta1_legacy_unsupported"
        entry["reason"] = (
            "Assinatura XDELTA1 legado (%XDZ00x%) detectada; incompativel com VCDIFF (RFC 3284). "
            "Converta primeiro com xdelta1 sobre a ROM USA verificada."
        )
        return entry

    if sig in ("bps", "ups"):
        entry["status"] = "rejected"
        entry["role"] = f"{sig}_unsupported"
        entry["reason"] = f"Formato de patch '{sig.upper()}' nao suportado diretamente; use VCDIFF, IPS ou DOSPATCH."
        return entry

    if sig == "dospatch":
        entry["status"] = "accepted"
        entry["role"] = "dos_rom_dospatch_profile"
        safe_name = _safe_filename(str(credit.get("local_filename", Path(norm).name)))
        entry["target_local_path"] = f"mods/profiles/{safe_name}"
        entry["reason"] = "Delta DOSPATCH valido pronto para verificacao SHA-1/CRC32."
        return entry

    if sig == "vcdiff":
        info = vcdiff_ips.inspect_vcdiff(data)
        entry["vcdiff_windows"] = info.window_count
        entry["vcdiff_target_size"] = info.target_size
        if info.target_size == EXPECTED_DOS_ROM_SIZE:
            entry["status"] = "accepted"
            entry["role"] = "dos_rom_baseline_xdelta"
            safe_name = _safe_filename(str(credit.get("local_filename", Path(norm).name)))
            entry["target_local_path"] = f"mods/local/{safe_name}"
            entry["reason"] = "VCDIFF valido para ROM de Dawn of Sorrow (64 MiB)."
        elif info.target_size == EXPECTED_POR_ROM_SIZE:
            entry["status"] = "rejected"
            entry["role"] = "portrait_of_ruin_rom_xdelta"
            entry["reason"] = "Alvo de 128 MiB (Portrait of Ruin / Simon's Legacy); incompativel com DoS."
        else:
            entry["status"] = "rejected"
            entry["role"] = "dominus_pc_xdelta"
            entry["reason"] = (
                f"Alvo VCDIFF de {info.target_size} B (Dominus Collection PC / DLL / alldata.bin); "
                "incompativel com ROM DS de 64 MiB."
            )
        return entry

    if sig == "ips":
        records = vcdiff_ips.parse_ips(data)
        entry["ips_records"] = len(records)
        entry["status"] = "accepted"
        entry["role"] = "dos_rom_audit_ips"
        safe_name = _safe_filename(str(credit.get("local_filename", Path(norm).name)))
        entry["target_local_path"] = f"mods/local/{safe_name}"
        entry["reason"] = "IPS valido para DoS USA (redundante com Definitive; mantido para auditoria/testes)."
        return entry

    if sig in ("mp4", "webm_ebml"):
        if "dos" in Path(norm).name.lower():
            entry["status"] = "accepted"
            entry["role"] = "dos_opening_video"
            ext = ".mp4" if sig == "mp4" else ".webm"
            entry["target_local_path"] = f"mods/intro/opening{ext}"
            entry["reason"] = (
                "Video de abertura de DoS detectado por assinatura real MP4 (ftyp)."
                if sig == "mp4"
                else "Video de abertura de DoS (WebM/EBML)."
            )
        else:
            entry["status"] = "rejected"
            entry["role"] = "other_game_video"
            entry["reason"] = "Video de outro jogo da coletanea (OoE/PoR); fora do escopo de DoS."
        return entry

    if lower.endswith((".txt", ".md", ".json")):
        entry["status"] = "ignored"
        entry["role"] = "documentation"
        entry["reason"] = "Documentacao / metadado informativo."
    return entry


def _validate_zip_member(info: zipfile.ZipInfo) -> None:
    name = info.filename.replace("\\", "/")
    if name.startswith("/") or ".." in Path(name).parts or ":" in name:
        raise ValueError(f"Entrada ZIP com path traversal bloqueada: {info.filename!r}")
    if info.file_size > MAX_ZIP_ENTRY_BYTES:
        raise ValueError(f"Entrada ZIP excede limite ({info.file_size} > {MAX_ZIP_ENTRY_BYTES}): {info.filename!r}")
    if info.file_size > 1_048_576 and info.compress_size > 0:
        ratio = info.file_size / float(info.compress_size)
        if ratio > MAX_ZIP_RATIO:
            raise ValueError(
                f"Suspeita de zip bomb em {info.filename!r} (razao {ratio:.1f}x > {MAX_ZIP_RATIO}x)."
            )


def iter_bundle_files(source: Path) -> list[tuple[str, bytes]]:
    """Le arquivos de um .zip, diretorio extraido ou patch individual com limites de seguranca."""
    if source.is_file() and source.suffix.lower() == ".zip":
        items: list[tuple[str, bytes]] = []
        total_uncompressed = 0
        with zipfile.ZipFile(source) as zf:
            members = [m for m in sorted(zf.infolist(), key=lambda x: x.filename) if not m.is_dir()]
            if len(members) > MAX_ZIP_ENTRIES:
                raise ValueError(f"ZIP excede limite de entradas ({len(members)} > {MAX_ZIP_ENTRIES}).")
            for info in members:
                _validate_zip_member(info)
                total_uncompressed += info.file_size
                if total_uncompressed > MAX_ZIP_TOTAL_BYTES:
                    raise ValueError(
                        f"Tamanho total descomprimido do ZIP excede limite ({total_uncompressed} > {MAX_ZIP_TOTAL_BYTES})."
                    )
                items.append((info.filename, zf.read(info.filename)))
        return items

    if source.is_file():
        if source.stat().st_size > MAX_ZIP_ENTRY_BYTES:
            raise ValueError(f"Arquivo excede limite permitido: {source}")
        return [(source.name, source.read_bytes())]

    if source.is_dir():
        items = []
        for path in sorted(source.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(source).as_posix()
            # Evita reimportar o proprio arquivo zip quando a pasta contem ambos
            if path.suffix.lower() == ".zip":
                continue
            # Ignora pasta Images solta da area de downloads
            if rel.lower().startswith("images/"):
                continue
            if path.stat().st_size > MAX_ZIP_ENTRY_BYTES:
                continue
            items.append((rel, path.read_bytes()))
        return items

    raise FileNotFoundError(f"Fonte de pacote nao encontrada: {source}")


def import_bundle(
    source: Path,
    repo_root: Path = ROOT,
    *,
    data_dir: Path | None = None,
    dry_run: bool = False,
) -> dict[str, object]:
    """Classifica todas as entradas, grava compativeis em {data} (atomico) e gera catalogo."""
    write_root = (data_dir or repo_root).resolve()
    entries: list[dict[str, object]] = []
    imported: list[str] = []
    rejected: list[str] = []

    for rel_path, data in iter_bundle_files(source):
        entry = classify_entry(rel_path, data)
        entries.append(entry)
        if entry["status"] == "accepted":
            rel_dst = str(entry["target_local_path"])
            imported.append(rel_dst)
            if not dry_run:
                dst = mod_resolver.safe_join_under(write_root, *Path(rel_dst).parts)
                mod_resolver.atomic_write_bytes(dst, data)
        elif entry["status"] == "rejected":
            rejected.append(str(entry["source_path"]))

    catalog = {
        "schema": "cdos.mod-catalog.v1",
        "source_name": source.name,
        "summary": {
            "total_inspected": len(entries),
            "accepted": len(imported),
            "rejected": len(rejected),
        },
        "imported_files": sorted(imported),
        "entries": entries,
    }

    if not dry_run:
        catalog_path = mod_resolver.safe_join_under(write_root, "mods", "catalog.json")
        mod_resolver.atomic_write_text(
            catalog_path, json.dumps(catalog, indent=2, ensure_ascii=False) + "\n"
        )

    return catalog


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--source",
        "--zip",
        dest="source",
        type=Path,
        required=True,
        help="Caminho para .zip, pasta extraida ou patch individual (alias: --zip)",
    )
    ap.add_argument("--repo-root", type=Path, default=ROOT, help="Raiz do repositorio (compatibilidade)")
    ap.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Diretorio gravavel {data} destino (evita gravar em {install})",
    )
    ap.add_argument("--dry-run", action="store_true", help="Apenas classifica sem gravar arquivos")
    args = ap.parse_args(argv)

    catalog = import_bundle(
        args.source,
        repo_root=args.repo_root,
        data_dir=args.data_dir,
        dry_run=args.dry_run,
    )
    summary = catalog["summary"]
    print(
        f"[import-mods] inspecionados={summary['total_inspected']} "
        f"aceitos={summary['accepted']} rejeitados={summary['rejected']}"
    )
    for item in catalog["entries"]:
        if item["status"] in ("accepted", "rejected"):
            print(f"  [{item['status'].upper()}] {item['source_path']} -> {item['reason']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

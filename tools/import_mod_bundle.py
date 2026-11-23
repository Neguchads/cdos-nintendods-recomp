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

EXPECTED_DOS_ROM_SIZE = 67_108_864
EXPECTED_POR_ROM_SIZE = 134_217_728

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
    if len(data) >= 4 and data[:4] == vcdiff_ips.VCDIFF_MAGIC:
        return "vcdiff"
    if len(data) >= 5 and data[:5] == vcdiff_ips.IPS_MAGIC:
        return "ips"
    if len(data) >= 12 and data[4:8] == b"ftyp":
        return "mp4"
    if len(data) >= 4 and data[:4] == b"\x1a\x45\xdf\xa3":
        return "webm_ebml"
    return "other"


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

    if sig == "vcdiff":
        info = vcdiff_ips.inspect_vcdiff(data)
        entry["vcdiff_windows"] = info.window_count
        entry["vcdiff_target_size"] = info.target_size
        if info.target_size == EXPECTED_DOS_ROM_SIZE:
            entry["status"] = "accepted"
            entry["role"] = "dos_rom_baseline_xdelta"
            entry["target_local_path"] = f"mods/local/{credit.get('local_filename', Path(norm).name)}"
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
        entry["target_local_path"] = f"mods/local/{credit.get('local_filename', Path(norm).name)}"
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


def iter_bundle_files(source: Path) -> list[tuple[str, bytes]]:
    """Le todos os arquivos de um .zip ou diretorio extraido."""
    if source.is_file() and source.suffix.lower() == ".zip":
        items: list[tuple[str, bytes]] = []
        with zipfile.ZipFile(source) as zf:
            for info in sorted(zf.infolist(), key=lambda x: x.filename):
                if info.is_dir():
                    continue
                items.append((info.filename, zf.read(info.filename)))
        return items

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
            items.append((rel, path.read_bytes()))
        return items

    raise FileNotFoundError(f"Fonte de pacote nao encontrada: {source}")


def import_bundle(
    source: Path,
    repo_root: Path = ROOT,
    *,
    dry_run: bool = False,
) -> dict[str, object]:
    """Classifica todas as entradas, copia as compativeis para mods/local e mods/intro e grava catalogo."""
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
                dst = repo_root / rel_dst
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(data)
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
        catalog_path = repo_root / "mods" / "catalog.json"
        catalog_path.parent.mkdir(parents=True, exist_ok=True)
        catalog_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return catalog


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", type=Path, required=True, help="Caminho para CDOS NDS.zip ou pasta extraida")
    ap.add_argument("--repo-root", type=Path, default=ROOT, help="Raiz do repositorio destino")
    ap.add_argument("--dry-run", action="store_true", help="Apenas classifica sem gravar arquivos")
    args = ap.parse_args(argv)

    catalog = import_bundle(args.source, repo_root=args.repo_root, dry_run=args.dry_run)
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

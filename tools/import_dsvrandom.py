#!/usr/bin/env python3
"""Importador local de saidas do DSVania Randomizer (LagoLunatic/dsvrandom) para DOSPATCH.

Recebe uma ROM randomizada (.nds) ou patch (.xdelta/.ips/.dospatch/.zip) gerado localmente pelo
usuario no DSVania Randomizer, valida integridade contra a ROM retail USA ACVE (SHA-1 travado),
executa auditoria estrutural (Header/ARM9/ARM7/Overlays/NitroFS), gera DOSPATCH deterministico
com verificacao roundtrip e grava atomicamente em {data}/mods/profiles/dsvrandom-<seed>.dospatch.

Nunca copia nem redistribui ROMs comerciais.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import build_ptbr_patch as bpp  # noqa: E402
import diff_dos_mods as ddm  # noqa: E402
import import_local_mod as ilm  # noqa: E402
import mod_resolver as mr  # noqa: E402

USA_ROM_DEFAULT = ROOT.parent / "Roms" / "Castlevania - Dawn of Sorrow (USA).nds"
USA_SHA1 = "47530ff87e608f88105a314fdf36dc385f8dec94"
MIN_NDS_BYTES = 16 * 1024 * 1024


def import_dsvrandom_output(
    source_path: Path,
    seed: str,
    usa_rom: bytes,
    *,
    data_mods_dir: Path,
    preset: str = "external",
    dsvrandom_version: str = "1.4.8",
) -> dict[str, object]:
    """Valida saida externa do DSVania Randomizer e grava DOSPATCH + manifesto em {data}/mods/."""
    if not source_path.is_file():
        raise FileNotFoundError(f"Arquivo de entrada nao encontrado: {source_path}")

    src_sha1 = hashlib.sha1(usa_rom).hexdigest()
    if src_sha1 != USA_SHA1:
        raise ValueError(f"ROM USA base invalida: esperado {USA_SHA1}, obtido {src_sha1}")

    clean_seed = mr.sanitize_seed(seed)
    if not clean_seed:
        raise ValueError(f"Seed invalida (esperado [A-Za-z0-9_-]{{1,32}}): {seed!r}")
    profile_id = mr.sanitize_safe_id(f"dsvrandom-{clean_seed.lower()}")
    if not profile_id:
        raise ValueError(f"Nao foi possivel derivar profile_id seguro para seed {seed!r}")
    profile_file = f"{profile_id}.dospatch"

    raw_bytes = source_path.read_bytes()
    source_sha256 = hashlib.sha256(raw_bytes).hexdigest()

    if source_path.suffix.lower() == ".nds":
        if len(raw_bytes) < MIN_NDS_BYTES:
            raise ValueError(f"ROM randomizada muito pequena ({len(raw_bytes)} B); esperado >= {MIN_NDS_BYTES} B.")
        game_code = raw_bytes[0x0C:0x10]
        if game_code != b"ACVE":
            raise ValueError(f"ROM randomizada nao e Dawn of Sorrow USA (game_code={game_code!r}, esperado b'ACVE').")
        if raw_bytes == usa_rom:
            raise ValueError("A ROM informada e identica a ROM USA limpa (nenhuma modificacao do randomizer).")
        target_rom = raw_bytes
        input_kind = "nds_rom"
    else:
        inner_name, fmt, patch_bytes = ilm.extract_first_compatible_patch(source_path.name, raw_bytes)
        rep = ilm.compile_profile_from_patch(
            profile_id,
            fmt,
            patch_bytes,
            usa_rom,
            data_mods_dir=data_mods_dir,
            profile_file=profile_file,
        )
        rep["seed"] = clean_seed
        rep["preset"] = preset
        rep["dsvrandom_version"] = dsvrandom_version
        rep["input_kind"] = f"patch:{fmt}"
        rep["input_name"] = inner_name
        rep["input_sha256"] = source_sha256
        rep["validation_level"] = "external_randomizer"
        meta_path = mr.safe_join_under(data_mods_dir, "cache", f"{profile_id}.json")
        mr.atomic_write_text(meta_path, json.dumps(rep, indent=2) + "\n")
        return rep

    # Converte ROM randomizada em delta DOSPATCH deterministico (nunca copia a ROM .nds para {data}).
    dospatch_bytes = bpp.encode_dospatch(usa_rom, target_rom)
    hdr_info = bpp.inspect_dospatch_header(dospatch_bytes)
    verified_rom = bpp.decode_and_apply_dospatch(usa_rom, dospatch_bytes)
    if verified_rom != target_rom:
        raise RuntimeError(f"Falha no roundtrip DOSPATCH para {profile_id}")

    changed_bytes = sum(1 for a, b in zip(usa_rom, target_rom) if a != b) + abs(len(target_rom) - len(usa_rom))
    arm9_diff = 0
    arm7_diff = 0
    changed_overlays: list[int] = []
    relocated_overlays: list[int] = []
    structural_ok = False
    structural_err = ""
    try:
        reg_a = ddm.parse_nds_regions(usa_rom)
        reg_b = ddm.parse_nds_regions(target_rom)
        a9s_a, a9e_a, _ = reg_a["arm9"]  # type: ignore[misc]
        a9s_b, a9e_b, _ = reg_b["arm9"]  # type: ignore[misc]
        arm9_diff = sum(1 for x, y in zip(usa_rom[a9s_a:a9e_a], target_rom[a9s_b:a9e_b]) if x != y) + abs(
            (a9e_a - a9s_a) - (a9e_b - a9s_b)
        )
        a7s_a, a7e_a, _ = reg_a["arm7"]  # type: ignore[misc]
        a7s_b, a7e_b, _ = reg_b["arm7"]  # type: ignore[misc]
        arm7_diff = sum(1 for x, y in zip(usa_rom[a7s_a:a7e_a], target_rom[a7s_b:a7e_b]) if x != y) + abs(
            (a7e_a - a7s_a) - (a7e_b - a7s_b)
        )
        ov_a = reg_a["overlays_arm9"]  # type: ignore[assignment]
        ov_b = reg_b["overlays_arm9"]  # type: ignore[assignment]
        for ov_id in sorted(set(ov_a) | set(ov_b)):
            if ov_id not in ov_a or ov_id not in ov_b:
                changed_overlays.append(ov_id)
                continue
            sa, ea = ov_a[ov_id]["rom_start"], ov_a[ov_id]["rom_end"]
            sb, eb = ov_b[ov_id]["rom_start"], ov_b[ov_id]["rom_end"]
            if (sa, ea) != (sb, eb):
                relocated_overlays.append(ov_id)
            if usa_rom[sa:ea] != target_rom[sb:eb]:
                changed_overlays.append(ov_id)
        structural_ok = True
    except Exception as exc:  # noqa: BLE001
        structural_err = str(exc)

    dst_patch = mr.safe_join_under(data_mods_dir, "profiles", profile_file)
    mr.atomic_write_bytes(dst_patch, dospatch_bytes)

    report: dict[str, object] = {
        "profile_id": profile_id,
        "seed": clean_seed,
        "preset": preset,
        "dsvrandom_version": dsvrandom_version,
        "input_kind": input_kind,
        "input_sha256": source_sha256,
        "source_rom_sha1": src_sha1,
        "target_rom_sha1": hashlib.sha1(target_rom).hexdigest(),
        "target_rom_size": len(target_rom),
        "dospatch_path": str(dst_patch),
        "dospatch_bytes": len(dospatch_bytes),
        "dospatch_sha256": hashlib.sha256(dospatch_bytes).hexdigest(),
        "chunks": int(hdr_info["chunk_count"]),
        "changed_bytes": changed_bytes,
        "structural_audit_ok": structural_ok,
        "structural_audit_error": structural_err,
        "arm9_changed_bytes": arm9_diff,
        "arm7_changed_bytes": arm7_diff,
        "changed_overlays": changed_overlays,
        "relocated_overlays": relocated_overlays,
        "validation_state": "unverified",
        "validation_level": "external_randomizer",
    }
    meta_path = mr.safe_join_under(data_mods_dir, "cache", f"{profile_id}.json")
    mr.atomic_write_text(meta_path, json.dumps(report, indent=2) + "\n")
    return report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", type=Path, required=True, help="ROM .nds ou patch (.xdelta/.ips/.dospatch/.zip) gerado pelo dsvrandom")
    ap.add_argument("--seed", required=True, help="Seed usada no DSVania Randomizer ([A-Za-z0-9_-]{1,32})")
    ap.add_argument("--rom", type=Path, default=USA_ROM_DEFAULT, help="Caminho da ROM retail USA ACVE limpa")
    ap.add_argument("--data-mods-dir", type=Path, default=ROOT / "mods", help="Diretorio {data}/mods")
    ap.add_argument("--preset", default="external", help="Rotulo opcional de configuracao/preset")
    ap.add_argument("--dsvrandom-version", default="1.4.8", help="Versao do DSVania Randomizer usada")
    args = ap.parse_args(argv)

    if not args.rom.is_file():
        raise SystemExit(f"[erro] ROM USA limpa ausente: {args.rom}")
    usa_rom = args.rom.read_bytes()
    rep = import_dsvrandom_output(
        args.source,
        args.seed,
        usa_rom,
        data_mods_dir=args.data_mods_dir,
        preset=args.preset,
        dsvrandom_version=args.dsvrandom_version,
    )
    print(
        f"[dsvrandom] OK {rep['profile_id']}: dospatch={rep['dospatch_bytes']}B "
        f"chunks={rep['chunks']} arm9_diff={rep['arm9_changed_bytes']}B "
        f"overlays={len(rep['changed_overlays'])} target_sha1={rep['target_rom_sha1']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

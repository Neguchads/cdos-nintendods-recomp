#!/usr/bin/env python3
"""Compara semanticamente ROM USA, Definitive Edition e PT-BR por Header, ARM9, ARM7, Overlays e NitroFS."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import build_ptbr_patch as bp  # noqa: E402
import vcdiff_ips  # noqa: E402


def parse_nds_regions(rom: bytes) -> dict[str, object]:
    """Extrai Header, ARM9, ARM7, tabela de overlays ARM9, FNT e FAT de uma ROM NDS."""
    if len(rom) < 0x200:
        raise ValueError("ROM NDS menor que o cabecalho minimo (0x200 bytes).")
    arm9_off, arm9_entry, arm9_load, arm9_sz = struct.unpack_from("<IIII", rom, 0x20)
    arm7_off, arm7_entry, arm7_load, arm7_sz = struct.unpack_from("<IIII", rom, 0x30)
    fnt_off, fnt_sz, fat_off, fat_sz = struct.unpack_from("<IIII", rom, 0x40)
    ov9_off, ov9_sz = struct.unpack_from("<II", rom, 0x50)
    ov7_off, ov7_sz = struct.unpack_from("<II", rom, 0x58)

    fat_count = fat_sz // 8
    fat: list[tuple[int, int]] = [
        struct.unpack_from("<II", rom, fat_off + i * 8) for i in range(fat_count)
    ]

    overlays_arm9: dict[int, dict[str, int]] = {}
    ov9_count = ov9_sz // 32
    for i in range(ov9_count):
        ov_id, ram_addr, ram_sz, bss_sz, s_init, e_init, file_id, flags = struct.unpack_from(
            "<IIIIIIII", rom, ov9_off + i * 32
        )
        start, end = fat[file_id] if file_id < len(fat) else (0, 0)
        overlays_arm9[ov_id] = {
            "overlay_id": ov_id,
            "file_id": file_id,
            "ram_addr": ram_addr,
            "ram_size": ram_sz,
            "rom_start": start,
            "rom_end": end,
            "flags": flags,
        }

    # Decodifica FNT para mapear file_id -> caminho NitroFS
    file_names: dict[int, str] = {}
    if fnt_off > 0 and fnt_sz >= 8 and fnt_off + fnt_sz <= len(rom):
        root_sub_off, root_first_id, total_dirs = struct.unpack_from("<IHH", rom, fnt_off)
        dir_paths: dict[int, str] = {0xF000: ""}
        # Primeira passada: descobre nomes de subdiretorios
        for dir_idx in range(total_dirs):
            dir_id = 0xF000 + dir_idx
            entry_off = fnt_off + dir_idx * 8
            if entry_off + 8 > fnt_off + fnt_sz:
                break
            sub_off, first_fid, _parent = struct.unpack_from("<IHH", rom, entry_off)
            cur = fnt_off + sub_off
            fid = first_fid
            prefix = dir_paths.get(dir_id, f"dir_{dir_id:04x}")
            while cur < fnt_off + fnt_sz:
                type_len = rom[cur]
                cur += 1
                if type_len == 0:
                    break
                is_dir = bool(type_len & 0x80)
                name_len = type_len & 0x7F
                name = rom[cur : cur + name_len].decode("ascii", errors="replace")
                cur += name_len
                if is_dir:
                    child_id = struct.unpack_from("<H", rom, cur)[0]
                    cur += 2
                    dir_paths[child_id] = f"{prefix}/{name}" if prefix else name
                else:
                    file_names[fid] = f"{prefix}/{name}" if prefix else name
                    fid += 1

    return {
        "arm9": (arm9_off, arm9_off + arm9_sz, arm9_load),
        "arm7": (arm7_off, arm7_off + arm7_sz, arm7_load),
        "fnt": (fnt_off, fnt_off + fnt_sz),
        "fat": (fat_off, fat_off + fat_sz),
        "ov9_table": (ov9_off, ov9_off + ov9_sz),
        "ov7_table": (ov7_off, ov7_off + ov7_sz),
        "fat_entries": fat,
        "overlays_arm9": overlays_arm9,
        "file_names": file_names,
    }


def _changed_count(a: bytes, b: bytes, start: int, end: int) -> int:
    return sum(1 for i in range(start, end) if a[i] != b[i])


def analyze_mod_diffs(rom_usa: bytes, rom_def: bytes, rom_ptbr: bytes) -> dict[str, object]:
    """Produz relatorio semantico completo de diferencas e colisoes entre Definitive e PT-BR."""
    if not (len(rom_usa) == len(rom_def) == len(rom_ptbr)):
        raise ValueError("As tres ROMs devem ter o mesmo tamanho para analise comparativa.")

    usa_meta = parse_nds_regions(rom_usa)
    def_meta = parse_nds_regions(rom_def)
    pt_meta = parse_nds_regions(rom_ptbr)

    arm9_s, arm9_e, _ = usa_meta["arm9"]
    arm7_s, arm7_e, _ = usa_meta["arm7"]
    fat_usa: list[tuple[int, int]] = usa_meta["fat_entries"]
    fat_def: list[tuple[int, int]] = def_meta["fat_entries"]
    fat_pt: list[tuple[int, int]] = pt_meta["fat_entries"]
    names: dict[int, str] = usa_meta["file_names"]
    ov_by_fid = {ov["file_id"]: ov["overlay_id"] for ov in usa_meta["overlays_arm9"].values()}

    arm9_conflicts: list[dict[str, object]] = []
    for off in range(arm9_s, arm9_e):
        if rom_usa[off] != rom_def[off] and rom_usa[off] != rom_ptbr[off] and rom_def[off] != rom_ptbr[off]:
            arm9_conflicts.append(
                {
                    "offset": hex(off),
                    "usa": hex(rom_usa[off]),
                    "definitive": hex(rom_def[off]),
                    "ptbr": hex(rom_ptbr[off]),
                }
            )

    relocated_fat: list[dict[str, object]] = []
    files_def_only: list[dict[str, object]] = []
    files_ptbr_only: list[dict[str, object]] = []
    files_identical_overlap: list[dict[str, object]] = []
    files_true_conflict: list[dict[str, object]] = []

    for fid, (s0, e0) in enumerate(fat_usa):
        s_def, e_def = fat_def[fid] if fid < len(fat_def) else (0, 0)
        s_pt, e_pt = fat_pt[fid] if fid < len(fat_pt) else (0, 0)
        label = f"overlay_{ov_by_fid[fid]:03d}" if fid in ov_by_fid else names.get(fid, f"file_{fid}")

        if (s0, e0) != (s_def, e_def) or (s0, e0) != (s_pt, e_pt):
            relocated_fat.append(
                {
                    "file_id": fid,
                    "name": label,
                    "usa": [hex(s0), e0 - s0],
                    "definitive": [hex(s_def), e_def - s_def],
                    "ptbr": [hex(s_pt), e_pt - s_pt],
                }
            )
            continue

        b_usa = rom_usa[s0:e0]
        b_def = rom_def[s0:e0]
        b_pt = rom_ptbr[s0:e0]
        c_def = b_usa != b_def
        c_pt = b_usa != b_pt
        if not c_def and not c_pt:
            continue

        item: dict[str, object] = {
            "file_id": fid,
            "name": label,
            "is_overlay": fid in ov_by_fid,
            "rom_offset": hex(s0),
            "size": e0 - s0,
        }
        if c_def and not c_pt:
            item["changed_bytes"] = _changed_count(b_usa, b_def, 0, len(b_usa))
            files_def_only.append(item)
        elif c_pt and not c_def:
            item["changed_bytes"] = _changed_count(b_usa, b_pt, 0, len(b_usa))
            files_ptbr_only.append(item)
        else:
            if b_def == b_pt:
                item["changed_bytes"] = _changed_count(b_usa, b_def, 0, len(b_usa))
                files_identical_overlap.append(item)
            else:
                same_ov = 0
                true_conf = 0
                def_o = 0
                pt_o = 0
                for idx in range(len(b_usa)):
                    u, d, p = b_usa[idx], b_def[idx], b_pt[idx]
                    if d != u and p != u:
                        if d == p:
                            same_ov += 1
                        else:
                            true_conf += 1
                    elif d != u:
                        def_o += 1
                    elif p != u:
                        pt_o += 1
                item["same_overlap_bytes"] = same_ov
                item["true_conflict_bytes"] = true_conf
                item["def_only_bytes"] = def_o
                item["ptbr_only_bytes"] = pt_o
                files_true_conflict.append(item)

    return {
        "schema": "cdos.semantic-diff.v1",
        "rom_sha1": {
            "usa": hashlib.sha1(rom_usa).hexdigest(),
            "definitive": hashlib.sha1(rom_def).hexdigest(),
            "ptbr": hashlib.sha1(rom_ptbr).hexdigest(),
        },
        "regions": {
            "header_def_changed": _changed_count(rom_usa, rom_def, 0, 0x4000),
            "header_ptbr_changed": _changed_count(rom_usa, rom_ptbr, 0, 0x4000),
            "arm9_def_changed": _changed_count(rom_usa, rom_def, arm9_s, arm9_e),
            "arm9_ptbr_changed": _changed_count(rom_usa, rom_ptbr, arm9_s, arm9_e),
            "arm9_true_conflicts": len(arm9_conflicts),
            "arm7_def_changed": _changed_count(rom_usa, rom_def, arm7_s, arm7_e),
            "arm7_ptbr_changed": _changed_count(rom_usa, rom_ptbr, arm7_s, arm7_e),
            "relocated_fat_entries": len(relocated_fat),
        },
        "arm9_conflict_details": arm9_conflicts,
        "relocated_fat": relocated_fat,
        "summary_counts": {
            "def_only_files": len(files_def_only),
            "ptbr_only_files": len(files_ptbr_only),
            "identical_overlap_files": len(files_identical_overlap),
            "true_conflict_files": len(files_true_conflict),
        },
        "files_def_only": files_def_only,
        "files_ptbr_only": files_ptbr_only,
        "files_identical_overlap": files_identical_overlap,
        "files_true_conflict": files_true_conflict,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--rom",
        type=Path,
        default=ROOT.parent / "Roms" / "Castlevania - Dawn of Sorrow (USA).nds",
        help="ROM USA original (.nds)",
    )
    ap.add_argument(
        "--definitive",
        type=Path,
        default=ROOT / "mods" / "local" / "CVDawnDefinitive.xdelta",
        help="Patch VCDIFF Definitive Edition",
    )
    ap.add_argument(
        "--ptbr",
        type=Path,
        default=ROOT / "mods" / "ptbr" / "dos-ptbr.dospatch",
        help="Patch DOSPATCH PT-BR",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=ROOT / "mods" / "reports" / "definitive-vs-ptbr.json",
        help="Relatorio JSON de saida",
    )
    args = ap.parse_args(argv)

    rom_usa = args.rom.read_bytes()
    rom_def = vcdiff_ips.apply_vcdiff(rom_usa, args.definitive.read_bytes())
    rom_ptbr = bp.decode_and_apply_dospatch(rom_usa, args.ptbr.read_bytes())

    report = analyze_mod_diffs(rom_usa, rom_def, rom_ptbr)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    sc = report["summary_counts"]
    reg = report["regions"]
    print(
        f"[diff-mods] OK -> {args.out}\n"
        f"  ARM9: def={reg['arm9_def_changed']}B ptbr={reg['arm9_ptbr_changed']}B conflitos={reg['arm9_true_conflicts']}B\n"
        f"  FAT realocados={reg['relocated_fat_entries']} | def_only={sc['def_only_files']} "
        f"ptbr_only={sc['ptbr_only_files']} identicos={sc['identical_overlap_files']} "
        f"conflitos={sc['true_conflict_files']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

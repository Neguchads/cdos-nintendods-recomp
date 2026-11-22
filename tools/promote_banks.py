#!/usr/bin/env python3
"""Promove funções descobertas pelo ds-decomp (dsd) e por manifestos de cobertura
para bancos C nativos validados por conteúdo (`--validate-live-bytes`)."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUTS_DIR = ROOT / "generated" / "inputs"
BASE_BANKS_DIR = ROOT / "generated" / "banks"
PROMOTED_DIR = ROOT / "generated" / "banks-promoted"
PROMOTED_INPUTS_DIR = ROOT / "generated" / "inputs-promoted"
SEEDS_ROOT = ROOT / "generated" / "seeds"
DSD_PROJECT_ARM9 = ROOT / "analysis" / "dsd" / "project" / "arm9"
NDSRECOMP_DIR = (
    ROOT.parent / "ndsrecomp"
    if (ROOT.parent / "ndsrecomp").is_dir()
    else ROOT / "framework" / "ndsrecomp"
)
INGEST_SCRIPT = NDSRECOMP_DIR / "tools" / "ingest_coverage_manifests.py"
RECOMPILER_EXE = ROOT / "generated" / "build-recompiler" / "nds_recompile.exe"
ROM_SHA1 = "47530ff87e608f88105a314fdf36dc385f8dec94"
ITCM_OFFSET_IN_ARM9 = 0xC0740
ITCM_SIZE = 0x63C0
ITCM_LOAD = 0x01FF8000

DSD_FUNC_RE = re.compile(
    r"^(?P<name>\S+)\s+kind:function\((?P<mode>arm|thumb)\b[^)]*\)\s+addr:(?P<addr>0x[0-9a-fA-F]+)"
)


def sha1_bytes(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def parse_dsd_symbols(symbols_path: Path) -> list[tuple[int, str, str]]:
    """Extrai lista [(addr, mode, name)] de um symbols.txt do dsd."""
    if not symbols_path.is_file():
        return []
    out: list[tuple[int, str, str]] = []
    for line in symbols_path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = DSD_FUNC_RE.match(line.strip())
        if m:
            out.append((int(m.group("addr"), 16), m.group("mode"), m.group("name")))
    return out


def parse_seed_toml_entries(toml_path: Path) -> list[tuple[int, str, str, str]]:
    """Extrai lista [(addr, mode, kind, note)] de um arquivo TOML com [[entry_point]]."""
    if not toml_path.is_file():
        return []
    entries: list[tuple[int, str, str, str]] = []
    cur: dict[str, str] = {}
    for raw in toml_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line == "[[entry_point]]":
            if "addr" in cur and "mode" in cur:
                entries.append(
                    (
                        int(cur["addr"], 16),
                        cur["mode"],
                        cur.get("kind", "seed"),
                        cur.get("name", ""),
                    )
                )
            cur = {}
            continue
        if "=" in line and not line.startswith("["):
            k, v = line.split("=", 1)
            cur[k.strip()] = v.strip().strip('"')
    if "addr" in cur and "mode" in cur:
        entries.append(
            (
                int(cur["addr"], 16),
                cur["mode"],
                cur.get("kind", "seed"),
                cur.get("name", ""),
            )
        )
    return entries


def deduplicate_seeds(
    seed_lists: list[list[tuple[int, str, str, str]]],
    *,
    addr_start: int | None = None,
    addr_end: int | None = None,
) -> list[tuple[int, str, str, str]]:
    """Mescla listas de seeds preservando o primeiro (addr, mode) observado."""
    seen: set[tuple[int, str]] = set()
    merged: list[tuple[int, str, str, str]] = []
    for lst in seed_lists:
        for addr, mode, kind, name in lst:
            if mode not in ("arm", "thumb"):
                continue
            stride = 2 if mode == "thumb" else 4
            if addr % stride != 0:
                continue
            if addr_start is not None and addr < addr_start:
                continue
            if addr_end is not None and addr >= addr_end:
                continue
            key = (addr, mode)
            if key in seen:
                continue
            seen.add(key)
            merged.append((addr, mode, kind, name))
    return merged


def write_program_with_seeds(
    path: Path,
    *,
    name: str,
    program_id: str,
    cpu: str,
    isa: str,
    load_address: int,
    entry_pc: int,
    binary: bytes,
    seeds: list[tuple[int, str, str, str]],
) -> None:
    lines = [
        "# AUTO-GERADO por tools/promote_banks.py",
        "[program]",
        f"name = {json.dumps(name, ensure_ascii=True)}",
        f"id = {json.dumps(program_id, ensure_ascii=True)}",
        f"cpu = {json.dumps(cpu, ensure_ascii=True)}",
        f"isa = {json.dumps(isa, ensure_ascii=True)}",
        f"load_address = 0x{load_address:08X}",
        f"size = 0x{len(binary):08X}",
        f"entry_pc = 0x{entry_pc:08X}",
        "authoritative_entry_points = false",
        "",
        "[identity]",
        f"sha1 = {json.dumps(sha1_bytes(binary), ensure_ascii=True)}",
        "",
    ]
    for addr, mode, kind, sym_name in seeds:
        lines.append("[[entry_point]]")
        lines.append(f"addr = 0x{addr:08X}")
        lines.append(f'mode = "{mode}"')
        if sym_name:
            lines.append(f"name = {json.dumps(sym_name, ensure_ascii=True)}")
        if kind:
            lines.append(f"kind = {json.dumps(kind, ensure_ascii=True)}")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def shards_for(seed_count: int, binary_size: int) -> int:
    # Bancos promovidos em NDS_TITLE_BANK_DIRS precisam de >= 2 shards (*_[0-9][0-9].c).
    if seed_count >= 2000 or binary_size >= 0x80000:
        return 8
    if seed_count >= 300 or binary_size >= 0x20000:
        return 4
    return 2


def run_recompiler(
    config_toml: Path,
    bin_path: Path,
    out_dir: Path,
    bank_name: str,
    shards: int,
    *,
    no_reloc_scan: bool = True,
) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    if no_reloc_scan:
        env["NDSRECOMP_NO_RELOC_SCAN"] = "1"
    cmd = [
        str(RECOMPILER_EXE),
        "--config",
        str(config_toml),
        "--bin",
        str(bin_path),
        "--out",
        str(out_dir),
        "--bank",
        bank_name,
        "--shards",
        str(shards),
        "--validate-live-bytes",
    ]
    proc = subprocess.run(
        cmd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"nds_recompile falhou para {bank_name} (rc={proc.returncode}):\n{proc.stdout}"
        )
    dispatch = out_dir / f"{bank_name}_dispatch.c"
    if not dispatch.is_file() or dispatch.stat().st_size == 0:
        raise RuntimeError(f"dispatch ausente para {bank_name}: {dispatch}")
    funcs = 0
    for line in proc.stdout.splitlines():
        m = re.search(r"\[emit\] bank '[^']+': (\d+) functions", line)
        if m:
            funcs = int(m.group(1))
    print(f"  [promote] {bank_name:<28} shards={shards} funcs={funcs}")
    return {"bank": bank_name, "shards": shards, "functions": funcs}


def find_coverage_manifests() -> list[Path]:
    candidates: list[Path] = []
    for folder in (ROOT / "saves", ROOT / "runtime", ROOT / "run"):
        if folder.is_dir():
            candidates.extend(sorted(folder.glob("*-coverage-*.json")))
    return candidates


def ingest_runtime_coverage(manifests: list[Path], out_dir: Path) -> None:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    if not manifests:
        print("[promote] aviso: nenhum manifesto *-coverage-*.json encontrado; usando apenas seeds dsd")
        return
    cmd = [
        sys.executable,
        str(INGEST_SCRIPT),
        "--out",
        str(out_dir),
        "--images",
        str(INPUTS_DIR),
        "--rom-sha1",
        ROM_SHA1,
        "--bank-prefix",
        "dosprom",
    ]
    if (BASE_BANKS_DIR / "dos_arm9_dispatch.c").is_file():
        cmd += ["--owned-rows-arm9", str(BASE_BANKS_DIR / "dos_arm9_dispatch.c")]
    if (BASE_BANKS_DIR / "dos_arm7_dispatch.c").is_file():
        cmd += ["--owned-rows-arm7", str(BASE_BANKS_DIR / "dos_arm7_dispatch.c")]
    cmd += [str(m) for m in manifests]
    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ingest_coverage_manifests falhou:\n{proc.stdout}")
    print(f"[promote] ingeridos {len(manifests)} manifesto(s) de cobertura")


def promote_all() -> dict[str, object]:
    if not RECOMPILER_EXE.is_file():
        raise SystemExit("nds_recompile.exe ausente. Rode: python tools/build.py recompiler")
    for req in (
        INPUTS_DIR / "arm9.bin",
        INPUTS_DIR / "arm7.bin",
        INPUTS_DIR / "overlays.json",
    ):
        if not req.is_file():
            raise SystemExit(f"input ausente ({req}). Rode: python tools/build.py prepare")

    runtime_dir = SEEDS_ROOT / "runtime"
    manifests = find_coverage_manifests()
    ingest_runtime_coverage(manifests, runtime_dir)

    if PROMOTED_DIR.exists():
        shutil.rmtree(PROMOTED_DIR)
    PROMOTED_DIR.mkdir(parents=True, exist_ok=True)
    if PROMOTED_INPUTS_DIR.exists():
        shutil.rmtree(PROMOTED_INPUTS_DIR)
    PROMOTED_INPUTS_DIR.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, object]] = []
    arm9_bin = (INPUTS_DIR / "arm9.bin").read_bytes()
    arm7_bin = (INPUTS_DIR / "arm7.bin").read_bytes()

    # 1) ARM9 Main promovido (seeds base + runtime + dsd)
    base_arm9_seeds = parse_seed_toml_entries(INPUTS_DIR / "arm9.toml")
    rt_arm9_seeds = parse_seed_toml_entries(runtime_dir / "seeds" / "arm9_arm9_02000000.toml")
    dsd_arm9_seeds = [
        (addr, mode, "dsd", name)
        for addr, mode, name in parse_dsd_symbols(DSD_PROJECT_ARM9 / "symbols.txt")
    ]
    merged_arm9 = deduplicate_seeds(
        [base_arm9_seeds, rt_arm9_seeds, dsd_arm9_seeds],
        addr_start=0x02000000,
        addr_end=0x02000000 + len(arm9_bin),
    )
    arm9_toml = PROMOTED_INPUTS_DIR / "dosprom_arm9_main.toml"
    write_program_with_seeds(
        arm9_toml,
        name="DoS ARM9 main (promoted)",
        program_id="dosprom_arm9_main",
        cpu="arm9",
        isa="armv5te",
        load_address=0x02000000,
        entry_pc=0x02000800,
        binary=arm9_bin,
        seeds=merged_arm9,
    )
    results.append(
        run_recompiler(
            arm9_toml,
            INPUTS_DIR / "arm9.bin",
            PROMOTED_DIR,
            "dosprom_arm9_main",
            shards_for(len(merged_arm9), len(arm9_bin)),
            no_reloc_scan=False,
        )
    )

    # 2) ITCM promovido (0x01FF8000, tamanho 0x63C0 dentro de arm9.bin)
    itcm_bin = arm9_bin[ITCM_OFFSET_IN_ARM9 : ITCM_OFFSET_IN_ARM9 + ITCM_SIZE]
    itcm_bin_path = PROMOTED_INPUTS_DIR / "itcm.bin"
    itcm_bin_path.write_bytes(itcm_bin)
    rt_itcm_seeds: list[tuple[int, str, str, str]] = []
    for p in sorted((runtime_dir / "seeds").glob("arm9_arm9_*.toml")) if (runtime_dir / "seeds").is_dir() else []:
        if p.name != "arm9_arm9_02000000.toml":
            rt_itcm_seeds.extend(parse_seed_toml_entries(p))
    dsd_itcm_seeds = [
        (addr, mode, "dsd", name)
        for addr, mode, name in parse_dsd_symbols(DSD_PROJECT_ARM9 / "itcm" / "symbols.txt")
    ]
    merged_itcm = deduplicate_seeds(
        [rt_itcm_seeds, dsd_itcm_seeds],
        addr_start=ITCM_LOAD,
        addr_end=ITCM_LOAD + len(itcm_bin),
    )
    if merged_itcm:
        itcm_toml = PROMOTED_INPUTS_DIR / "dosprom_arm9_itcm.toml"
        write_program_with_seeds(
            itcm_toml,
            name="DoS ARM9 ITCM (promoted)",
            program_id="dosprom_arm9_itcm",
            cpu="arm9",
            isa="armv5te",
            load_address=ITCM_LOAD,
            entry_pc=merged_itcm[0][0],
            binary=itcm_bin,
            seeds=merged_itcm,
        )
        results.append(
            run_recompiler(
                itcm_toml,
                itcm_bin_path,
                PROMOTED_DIR,
                "dosprom_arm9_itcm",
                shards_for(len(merged_itcm), len(itcm_bin)),
            )
        )

    # 3) Overlays ARM9 (dsd + runtime seeds)
    overlays = json.loads((INPUTS_DIR / "overlays.json").read_text(encoding="utf-8"))
    rt_overlay_by_id: dict[int, list[Path]] = {}
    if (runtime_dir / "seeds").is_dir():
        for toml in sorted((runtime_dir / "seeds").glob("arm9_ov9_*.toml")):
            m = re.match(r"arm9_ov9_(\d+)_[0-9a-f]+", toml.stem)
            if m:
                rt_overlay_by_id.setdefault(int(m.group(1)), []).append(toml)

    for rec in overlays:
        ov_id = int(rec["id"])
        ov_load = int(str(rec["load_address"]), 16)
        ov_bin_path = INPUTS_DIR / "overlays" / str(rec["file"])
        ov_bin = ov_bin_path.read_bytes()
        if sha1_bytes(ov_bin) != rec["sha1"]:
            raise RuntimeError(f"SHA-1 mismatch no overlay {ov_id}")
        rt_lists = [parse_seed_toml_entries(p) for p in rt_overlay_by_id.get(ov_id, [])]
        dsd_sym = DSD_PROJECT_ARM9 / "overlays" / f"ov{ov_id:03d}" / "symbols.txt"
        dsd_ov = [(addr, mode, "dsd", name) for addr, mode, name in parse_dsd_symbols(dsd_sym)]
        merged_ov = deduplicate_seeds(
            [*rt_lists, dsd_ov],
            addr_start=ov_load,
            addr_end=ov_load + len(ov_bin),
        )
        if not merged_ov:
            continue
        bank_name = f"dosprom_arm9_ov{ov_id:03d}"
        ov_toml = PROMOTED_INPUTS_DIR / f"{bank_name}.toml"
        write_program_with_seeds(
            ov_toml,
            name=f"DoS ARM9 overlay {ov_id:03d} (promoted)",
            program_id=bank_name,
            cpu="arm9",
            isa="armv5te",
            load_address=ov_load,
            entry_pc=merged_ov[0][0],
            binary=ov_bin,
            seeds=merged_ov,
        )
        results.append(
            run_recompiler(
                ov_toml,
                ov_bin_path,
                PROMOTED_DIR,
                bank_name,
                shards_for(len(merged_ov), len(ov_bin)),
            )
        )

    # 4) ARM7 aliases (ex.: 0x037F7E90 -> WRAM 0x037F8000, 0x027B0608 -> 0x027C0000)
    if (runtime_dir / "seeds").is_dir():
        for toml in sorted((runtime_dir / "seeds").glob("arm7_arm7_*.toml")):
            base_hex = toml.stem.rsplit("_", 1)[1]
            base_addr = int(base_hex, 16)
            seeds = deduplicate_seeds(
                [parse_seed_toml_entries(toml)],
                addr_start=base_addr,
                addr_end=base_addr + len(arm7_bin),
            )
            if not seeds:
                continue
            bank_name = f"dosprom_arm7_alias_{base_hex}"
            alias_toml = PROMOTED_INPUTS_DIR / f"{bank_name}.toml"
            write_program_with_seeds(
                alias_toml,
                name=f"DoS ARM7 alias @ 0x{base_addr:08X}",
                program_id=bank_name,
                cpu="arm7",
                isa="armv4t",
                load_address=base_addr,
                entry_pc=seeds[0][0],
                binary=arm7_bin,
                seeds=seeds,
            )
            results.append(
                run_recompiler(
                    alias_toml,
                    INPUTS_DIR / "arm7.bin",
                    PROMOTED_DIR,
                    bank_name,
                    shards_for(len(seeds), len(arm7_bin)),
                )
            )

    # 5) Bancos de páginas em RAM (runtime-materialized, ex.: código auto-modificado / 0x03807000)
    if (runtime_dir / "images").is_dir():
        for page_toml in sorted((runtime_dir / "images").glob("*.toml")):
            page_bin = page_toml.with_suffix(".bin")
            if not page_bin.is_file():
                continue
            bank_name = page_toml.stem
            if "_arm9_" not in bank_name and "_arm7_" not in bank_name:
                continue
            results.append(
                run_recompiler(
                    page_toml,
                    page_bin,
                    PROMOTED_DIR,
                    bank_name,
                    shards=2,
                )
            )

    summary = {
        "manifests_ingested": len(manifests),
        "banks_promoted": len(results),
        "total_functions": sum(int(r["functions"]) for r in results),
        "banks": results,
    }
    (ROOT / "generated" / "promoted_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(
        f"[promote] OK: {summary['banks_promoted']} bancos promovidos "
        f"({summary['total_functions']} funções) em {PROMOTED_DIR}"
    )
    return summary


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.parse_args()
    promote_all()
    return 0


if __name__ == "__main__":
    sys.exit(main())

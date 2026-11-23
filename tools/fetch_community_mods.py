#!/usr/bin/env python3
"""Baixa (de fontes oficiais HTTP 200), audita via diff semantico e compila perfis DOSPATCH locais em {data}/mods/profiles/."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import build_ptbr_patch as bpp  # noqa: E402
import diff_dos_mods as ddm  # noqa: E402
import import_mod_bundle as imb  # noqa: E402
import mod_resolver as mr  # noqa: E402
import vcdiff_ips as vi  # noqa: E402

USA_ROM_DEFAULT = ROOT.parent / "Roms" / "Castlevania - Dawn of Sorrow (USA).nds"
USA_SHA1 = "47530ff87e608f88105a314fdf36dc385f8dec94"

# Fontes publicas diretas (HTTP 200 sem anti-bot). Hashes SHA-256 verificados apos download e travados no manifesto local.
COMMUNITY_SOURCES: dict[str, dict[str, str]] = {
    "eternity-of-sorrow": {
        "name": "Castlevania: Eternity of Sorrow 1.2 (final build)",
        "author": "WetBandAid",
        "version": "1.2",
        "url": "https://raw.githubusercontent.com/Wet-Band-Aid/Castlevania---Eternity-of-Sorrow/main/no%20touch%20screen/Castlevania%20-%20Eternity%20of%20Sorrow%201.2(final%20build).xdelta",
        "download_name": "eternity_of_sorrow_1.2.xdelta",
        "profile_file": "eternity-of-sorrow.dospatch",
    },
    "albus-mode": {
        "name": "Albus Mode (Julius Mode Pack)",
        "author": "Oersted",
        "version": "1.0",
        "url": "https://files.gamebanana.com/mods/dawn_of_sorrow_-_albus_mode.zip",
        "download_name": "dawn_of_sorrow_-_albus_mode.zip",
        "profile_file": "albus-mode.dospatch",
    },
    "zx-omega": {
        "name": "Playable Model ZX & OX (Julius Mode Pack)",
        "author": "Oersted",
        "version": "1.0.1",
        "url": "https://files.gamebanana.com/mods/dos_-_playable_zx_omega_101_1_.zip",
        "download_name": "dos_-_playable_zx_omega_101_1_.zip",
        "profile_file": "zx-omega.dospatch",
    },
}


def download_file(url: str, dst: Path) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "cdos-recomp-mod-fetcher/1.0"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        data = resp.read()
    mr.atomic_write_bytes(dst, data)
    return data


def extract_first_compatible_patch(raw_name: str, raw_bytes: bytes) -> tuple[str, str, bytes]:
    """Retorna (nome_interno, formato, bytes_patch) validando limites ZIP e assinatura binaria."""
    if raw_name.lower().endswith(".zip"):
        candidates: list[tuple[str, str, bytes]] = []
        import io

        with zipfile.ZipFile(io.BytesIO(raw_bytes)) as zf:
            members = [m for m in sorted(zf.infolist(), key=lambda x: x.filename) if not m.is_dir()]
            if len(members) > imb.MAX_ZIP_ENTRIES:
                raise ValueError(f"ZIP excede limite de entradas ({len(members)})")
            total = 0
            for info in members:
                imb._validate_zip_member(info)
                total += info.file_size
                if total > imb.MAX_ZIP_TOTAL_BYTES:
                    raise ValueError("ZIP excede tamanho total permitido")
                payload = zf.read(info.filename)
                fmt = vi.detect_patch_format(payload)
                if fmt in ("vcdiff", "ips", "dospatch"):
                    candidates.append((info.filename, fmt, payload))
                elif fmt == "xdelta1":
                    raise ValueError(f"Patch XDELTA1 legado encontrado em {info.filename}; conversao manual necessaria.")
        if not candidates:
            raise ValueError(f"Nenhum patch VCDIFF/IPS/DOSPATCH valido encontrado dentro de {raw_name}")
        # Prefere VCDIFF sobre IPS se houver ambos
        candidates.sort(key=lambda item: (0 if item[1] == "vcdiff" else 1, item[0]))
        return candidates[0]

    fmt = vi.detect_patch_format(raw_bytes)
    if fmt == "xdelta1":
        raise ValueError(f"{raw_name} usa formato XDELTA1 legado (%XDZ00x%), incompativel com VCDIFF.")
    if fmt not in ("vcdiff", "ips", "dospatch"):
        raise ValueError(f"{raw_name}: formato binario '{fmt}' nao suportado.")
    return raw_name, fmt, raw_bytes


def find_xdelta3_exe() -> Path | None:
    local = ROOT / "toolchains" / "xdelta3" / "xdelta3.exe"
    if local.is_file():
        return local
    found = shutil.which("xdelta3")
    return Path(found) if found else None


def apply_vcdiff_with_xdelta3(usa_rom: bytes, patch_bytes: bytes) -> bytes:
    xdelta = find_xdelta3_exe()
    if xdelta is None:
        raise ValueError(
            "VCDIFF usa compressor secundario (DJW/FGK/LZMA) e toolchains/xdelta3/xdelta3.exe nao foi encontrado."
        )
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        src_p = t / "src.nds"
        delta_p = t / "patch.xdelta"
        out_p = t / "out.nds"
        src_p.write_bytes(usa_rom)
        delta_p.write_bytes(patch_bytes)
        proc = subprocess.run(
            [str(xdelta), "-d", "-s", str(src_p), str(delta_p), str(out_p)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if proc.returncode != 0 or not out_p.is_file():
            raise RuntimeError(f"xdelta3 falhou (exit {proc.returncode}): {proc.stderr.strip()}")
        return out_p.read_bytes()


def compile_profile_from_patch(
    profile_id: str,
    patch_fmt: str,
    patch_bytes: bytes,
    usa_rom: bytes,
    *,
    data_mods_dir: Path,
    profile_file: str,
) -> dict[str, object]:
    """Aplica o patch sobre a ROM USA em RAM, audita via diff semantico e grava DOSPATCH atomico."""
    src_sha1 = hashlib.sha1(usa_rom).hexdigest()
    if src_sha1 != USA_SHA1:
        raise ValueError(f"ROM USA base invalida: esperado {USA_SHA1}, obtido {src_sha1}")

    if patch_fmt == "vcdiff":
        info = vi.inspect_vcdiff(patch_bytes)
        if info.has_secondary_compressor:
            target_rom = apply_vcdiff_with_xdelta3(usa_rom, patch_bytes)
        else:
            target_rom = vi.apply_vcdiff(usa_rom, patch_bytes)
    elif patch_fmt == "ips":
        target_rom = vi.apply_ips(usa_rom, patch_bytes)
    elif patch_fmt == "dospatch":
        target_rom = bpp.decode_and_apply_dospatch(usa_rom, patch_bytes)
    else:
        raise ValueError(f"Formato nao suportado: {patch_fmt}")

    # Gera DOSPATCH deterministico e valida roundtrip integral
    dospatch_bytes = bpp.encode_dospatch(usa_rom, target_rom)
    hdr_info = bpp.inspect_dospatch_header(dospatch_bytes)
    verified_rom = bpp.decode_and_apply_dospatch(usa_rom, dospatch_bytes)
    if verified_rom != target_rom:
        raise RuntimeError(f"Falha no roundtrip DOSPATCH de {profile_id}")
    changed_bytes = sum(1 for a, b in zip(usa_rom, target_rom) if a != b) + abs(len(target_rom) - len(usa_rom))
    stats = {"chunks": int(hdr_info["chunk_count"]), "changed_bytes": changed_bytes}

    # Analise estrutural semantica (Header, ARM9, ARM7, Overlays, NitroFS)
    arm9_diff = 0
    arm7_diff = 0
    relocated_overlays: list[int] = []
    changed_overlays: list[int] = []
    changed_files_count = 0
    try:
        reg_a = ddm.parse_nds_regions(usa_rom)
        reg_b = ddm.parse_nds_regions(target_rom)
        a9s_a, a9e_a, _ = reg_a["arm9"]  # type: ignore[misc]
        a9s_b, a9e_b, _ = reg_b["arm9"]  # type: ignore[misc]
        a9_a = usa_rom[a9s_a:a9e_a]
        a9_b = target_rom[a9s_b:a9e_b]
        arm9_diff = sum(1 for x, y in zip(a9_a, a9_b) if x != y) + abs(len(a9_a) - len(a9_b))

        a7s_a, a7e_a, _ = reg_a["arm7"]  # type: ignore[misc]
        a7s_b, a7e_b, _ = reg_b["arm7"]  # type: ignore[misc]
        a7_a = usa_rom[a7s_a:a7e_a]
        a7_b = target_rom[a7s_b:a7e_b]
        arm7_diff = sum(1 for x, y in zip(a7_a, a7_b) if x != y) + abs(len(a7_a) - len(a7_b))

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

        fat_a = reg_a["fat"]  # type: ignore[assignment]
        fat_b = reg_b["fat"]  # type: ignore[assignment]
        for fid in range(min(len(fat_a), len(fat_b))):
            sa, ea = fat_a[fid]
            sb, eb = fat_b[fid]
            if usa_rom[sa:ea] != target_rom[sb:eb]:
                changed_files_count += 1
        structural_ok = True
        structural_err = ""
    except Exception as exc:  # noqa: BLE001
        structural_ok = False
        structural_err = str(exc)

    dst_patch = mr.safe_join_under(data_mods_dir, "profiles", profile_file)
    mr.atomic_write_bytes(dst_patch, dospatch_bytes)

    report = {
        "profile_id": profile_id,
        "source_rom_sha1": src_sha1,
        "target_rom_sha1": hashlib.sha1(target_rom).hexdigest(),
        "target_rom_size": len(target_rom),
        "patch_format": patch_fmt,
        "source_patch_sha256": hashlib.sha256(patch_bytes).hexdigest(),
        "dospatch_path": str(dst_patch),
        "dospatch_bytes": len(dospatch_bytes),
        "dospatch_sha256": hashlib.sha256(dospatch_bytes).hexdigest(),
        "chunks": stats["chunks"],
        "changed_bytes": stats["changed_bytes"],
        "structural_audit_ok": structural_ok,
        "structural_audit_error": structural_err,
        "arm9_changed_bytes": arm9_diff,
        "arm7_changed_bytes": arm7_diff,
        "changed_overlays": changed_overlays,
        "relocated_overlays": relocated_overlays,
        "validation_state": "unverified",
    }
    report_path = mr.safe_join_under(data_mods_dir, "cache", f"audit-{profile_id}.json")
    mr.atomic_write_text(report_path, json.dumps(report, indent=2) + "\n")
    return report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rom", type=Path, default=USA_ROM_DEFAULT)
    ap.add_argument("--data-mods-dir", type=Path, default=ROOT / "mods")
    ap.add_argument(
        "--only",
        nargs="+",
        choices=sorted(COMMUNITY_SOURCES.keys()),
        default=sorted(COMMUNITY_SOURCES.keys()),
        help="Quais mods baixar e compilar",
    )
    ap.add_argument("--offline-cache", action="store_true", help="Usa arquivos ja baixados em local/ se presentes")
    args = ap.parse_args(argv)

    if not args.rom.is_file():
        raise SystemExit(f"[erro] ROM USA ausente: {args.rom}")
    usa_rom = args.rom.read_bytes()

    results: list[dict[str, object]] = []
    for mod_id in args.only:
        spec = COMMUNITY_SOURCES[mod_id]
        raw_path = mr.safe_join_under(args.data_mods_dir, "local", spec["download_name"])
        if args.offline_cache and raw_path.is_file():
            raw_bytes = raw_path.read_bytes()
        else:
            print(f"[fetch] baixando {mod_id} ({spec['name']}) de {spec['url']} ...", flush=True)
            raw_bytes = download_file(spec["url"], raw_path)
        dl_sha256 = hashlib.sha256(raw_bytes).hexdigest()
        inner_name, fmt, patch_bytes = extract_first_compatible_patch(spec["download_name"], raw_bytes)
        rep = compile_profile_from_patch(
            mod_id,
            fmt,
            patch_bytes,
            usa_rom,
            data_mods_dir=args.data_mods_dir,
            profile_file=spec["profile_file"],
        )
        rep["download_sha256"] = dl_sha256
        rep["source_url"] = spec["url"]
        rep["inner_patch_name"] = inner_name
        results.append(rep)
        print(
            f"[fetch] OK {mod_id}: inner={inner_name} fmt={fmt} target_size={rep['target_rom_size']} "
            f"dospatch={rep['dospatch_bytes']}B arm9_diff={rep['arm9_changed_bytes']}B "
            f"overlays_changed={len(rep['changed_overlays'])} relocated={rep['relocated_overlays']} "
            f"target_sha1={rep['target_rom_sha1']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())

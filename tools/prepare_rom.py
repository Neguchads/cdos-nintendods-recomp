#!/usr/bin/env python3
"""Extrai e valida ARM9, ARM7 e os 41 overlays de Castlevania: Dawn of Sorrow (ACVE).

Usa apenas a biblioteca padrão do Python (sem dependência externa), pois ARM9
e os 41 overlays da ROM USA rev 0 são armazenados descomprimidos.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ROM = ROOT.parent / "Roms" / "Castlevania - Dawn of Sorrow (USA).nds"
DEFAULT_OUT = ROOT / "generated" / "inputs"

EXPECTED_ROM_SIZE = 0x04000000
EXPECTED_ROM_SHA1 = "47530ff87e608f88105a314fdf36dc385f8dec94"
EXPECTED_ROM_SHA256 = "3ddc8b0eac841b6005ff4c38a184b517fa8225ac905aad951b0572850358d8b0"
EXPECTED_TITLE = b"CASTLEVANIA1"
EXPECTED_GAME_CODE = b"ACVE"
EXPECTED_REVISION = 0

MODULE_PARAMS_MAGIC = struct.pack("<II", 0xDEC00621, 0x2106C0DE)

# Mapeamento conhecido (DSVEdit constants/dos_constants.rb) para facilitar análise da Fase 2.
OVERLAY_ROLES: dict[int, str] = {
    0: "constant_core_0",
    1: "constant_core_1",
    2: "constant_core_2",
    3: "constant_core_3",
    4: "constant_core_4",
    5: "constant_core_5",
    6: "area_wizardry_lab",
    7: "area_condemned_tower_and_mine",
    8: "area_dark_chapel",
    9: "area_clock_tower",
    10: "area_pinnacle",
    11: "area_demon_guest_house",
    12: "area_menace_room",
    13: "area_the_abyss",
    14: "area_lost_village",
    15: "area_silenced_ruins",
    16: "area_garden_of_madness",
    17: "area_subterranean_hell",
    18: "area_prologue",
    19: "area_epilogue",
    20: "area_boss_rush",
    21: "area_enemy_set_mode",
    22: "area_julius_throne_room",
}


@dataclass(frozen=True)
class NdsHeader:
    title: bytes
    game_code: bytes
    maker_code: bytes
    unit_code: int
    revision: int
    arm9_offset: int
    arm9_entry: int
    arm9_ram: int
    arm9_size: int
    arm7_offset: int
    arm7_entry: int
    arm7_ram: int
    arm7_size: int
    fnt_offset: int
    fnt_size: int
    fat_offset: int
    fat_size: int
    ov9_offset: int
    ov9_size: int
    ov7_offset: int
    ov7_size: int


@dataclass(frozen=True)
class OverlayEntry:
    overlay_id: int
    ram_address: int
    ram_size: int
    bss_size: int
    static_init_start: int
    static_init_end: int
    file_id: int
    compressed: bool
    compressed_size: int
    rom_offset: int
    rom_end: int
    sha1: str
    role: str


def sha1_hex(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_nds_header(rom: bytes) -> NdsHeader:
    if len(rom) < 0x200:
        raise ValueError(f"ROM truncada: {len(rom)} bytes (< 512)")
    arm9_offset, arm9_entry, arm9_ram, arm9_size = struct.unpack_from("<IIII", rom, 0x20)
    arm7_offset, arm7_entry, arm7_ram, arm7_size = struct.unpack_from("<IIII", rom, 0x30)
    fnt_offset, fnt_size, fat_offset, fat_size = struct.unpack_from("<IIII", rom, 0x40)
    ov9_offset, ov9_size, ov7_offset, ov7_size = struct.unpack_from("<IIII", rom, 0x50)
    return NdsHeader(
        title=rom[0x00:0x0C],
        game_code=rom[0x0C:0x10],
        maker_code=rom[0x10:0x12],
        unit_code=rom[0x12],
        revision=rom[0x1E],
        arm9_offset=arm9_offset,
        arm9_entry=arm9_entry,
        arm9_ram=arm9_ram,
        arm9_size=arm9_size,
        arm7_offset=arm7_offset,
        arm7_entry=arm7_entry,
        arm7_ram=arm7_ram,
        arm7_size=arm7_size,
        fnt_offset=fnt_offset,
        fnt_size=fnt_size,
        fat_offset=fat_offset,
        fat_size=fat_size,
        ov9_offset=ov9_offset,
        ov9_size=ov9_size,
        ov7_offset=ov7_offset,
        ov7_size=ov7_size,
    )


def validate_retail_rom(rom: bytes) -> NdsHeader:
    if len(rom) != EXPECTED_ROM_SIZE:
        raise ValueError(
            f"tamanho inesperado da ROM: {len(rom)} bytes (esperado {EXPECTED_ROM_SIZE})"
        )
    got_sha1 = sha1_hex(rom)
    if got_sha1 != EXPECTED_ROM_SHA1:
        raise ValueError(f"SHA-1 inválido: {got_sha1} (esperado {EXPECTED_ROM_SHA1})")
    got_sha256 = sha256_hex(rom)
    if got_sha256 != EXPECTED_ROM_SHA256:
        raise ValueError(
            f"SHA-256 inválido: {got_sha256} (esperado {EXPECTED_ROM_SHA256})"
        )
    hdr = parse_nds_header(rom)
    if hdr.title != EXPECTED_TITLE:
        raise ValueError(f"título inválido no header: {hdr.title!r}")
    if hdr.game_code != EXPECTED_GAME_CODE:
        raise ValueError(f"game code inválido: {hdr.game_code!r}")
    if hdr.revision != EXPECTED_REVISION:
        raise ValueError(f"revisão inválida: {hdr.revision}")
    return hdr


def _slice_checked(rom: bytes, offset: int, size: int, label: str) -> bytes:
    if offset < 0 or size < 0 or offset + size > len(rom):
        raise ValueError(f"{label} fora dos limites da ROM ({offset:#x}+{size:#x})")
    return rom[offset : offset + size]


def _overlay_role(oid: int) -> str:
    if oid in OVERLAY_ROLES:
        return OVERLAY_ROLES[oid]
    if 23 <= oid <= 40:
        return f"slot_23_40_overlay_{oid:02d}"
    return f"overlay_{oid:02d}"


def extract_arm9_overlays(
    rom: bytes, hdr: NdsHeader
) -> list[tuple[OverlayEntry, bytes]]:
    if hdr.ov9_size % 32 != 0:
        raise ValueError(f"tamanho de tabela OV9 inválido: {hdr.ov9_size:#x}")
    count = hdr.ov9_size // 32
    result: list[tuple[OverlayEntry, bytes]] = []
    for i in range(count):
        off = hdr.ov9_offset + i * 32
        oid, ram, rsize, bss, sinit, einit, fid, flags = struct.unpack_from(
            "<IIIIIIII", rom, off
        )
        compressed = bool((flags >> 24) & 1)
        csize = flags & 0x00FFFFFF
        if compressed:
            raise ValueError(
                f"overlay ARM9 {oid} comprimido (csize={csize:#x}); "
                "este extrator suporta apenas overlays descomprimidos"
            )
        fat_off = hdr.fat_offset + fid * 8
        if fat_off + 8 > hdr.fat_offset + hdr.fat_size:
            raise ValueError(f"file_id {fid} do overlay {oid} fora da tabela FAT")
        start, end = struct.unpack_from("<II", rom, fat_off)
        if end < start or end > len(rom):
            raise ValueError(
                f"intervalo FAT inválido para overlay {oid}: {start:#x}..{end:#x}"
            )
        blob = rom[start:end]
        if len(blob) < rsize:
            raise ValueError(
                f"overlay {oid} menor que ram_size ({len(blob)} < {rsize})"
            )
        entry = OverlayEntry(
            overlay_id=oid,
            ram_address=ram,
            ram_size=rsize,
            bss_size=bss,
            static_init_start=sinit,
            static_init_end=einit,
            file_id=fid,
            compressed=compressed,
            compressed_size=csize,
            rom_offset=start,
            rom_end=end,
            sha1=sha1_hex(blob),
            role=_overlay_role(oid),
        )
        result.append((entry, blob))
    return result


def detect_arm9_compressed(arm9: bytes) -> bool:
    idx = arm9.find(MODULE_PARAMS_MAGIC)
    if idx != -1 and idx >= 28:
        compressed_static_end = struct.unpack_from("<I", arm9, idx - 8)[0]
        return compressed_static_end != 0
    return False


def format_program_toml(
    *,
    name: str,
    program_id: str,
    cpu: str,
    isa: str,
    load_address: int,
    entry_pc: int,
    binary: bytes,
) -> str:
    lines = [
        "# AUTO-GERADO por tools/prepare_rom.py",
        "[program]",
        f"name = {json.dumps(name, ensure_ascii=True)}",
        f"id = {json.dumps(program_id, ensure_ascii=True)}",
        f"cpu = {json.dumps(cpu, ensure_ascii=True)}",
        f"isa = {json.dumps(isa, ensure_ascii=True)}",
        f"load_address = 0x{load_address:08x}",
        f"size = 0x{len(binary):08x}",
        f"entry_pc = 0x{entry_pc:08x}",
        "authoritative_entry_points = false",
        "",
        "[identity]",
        f"sha1 = {json.dumps(sha1_hex(binary), ensure_ascii=True)}",
        "",
        "[[entry_point]]",
        f"addr = 0x{entry_pc:08x}",
        'mode = "arm"',
        'name = "entry"',
        'kind = "rom_header"',
        "",
    ]
    return "\n".join(lines)


def prepare_rom(rom_path: Path, out_dir: Path) -> dict[str, object]:
    rom = rom_path.read_bytes()
    hdr = validate_retail_rom(rom)

    arm9 = _slice_checked(rom, hdr.arm9_offset, hdr.arm9_size, "ARM9")
    if detect_arm9_compressed(arm9):
        raise ValueError("ARM9 comprimido não suportado por este extrator sem BLZ")
    arm7 = _slice_checked(rom, hdr.arm7_offset, hdr.arm7_size, "ARM7")
    overlays = extract_arm9_overlays(rom, hdr)

    out_dir.mkdir(parents=True, exist_ok=True)
    overlays_dir = out_dir / "overlays"
    overlays_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "arm9.bin").write_bytes(arm9)
    (out_dir / "arm7.bin").write_bytes(arm7)

    (out_dir / "arm9.toml").write_text(
        format_program_toml(
            name="Castlevania: Dawn of Sorrow (USA rev 0) ARM9 main",
            program_id="dos_arm9",
            cpu="arm9",
            isa="armv5te",
            load_address=hdr.arm9_ram,
            entry_pc=hdr.arm9_entry,
            binary=arm9,
        ),
        encoding="utf-8",
        newline="\n",
    )
    (out_dir / "arm7.toml").write_text(
        format_program_toml(
            name="Castlevania: Dawn of Sorrow (USA rev 0) ARM7",
            program_id="dos_arm7",
            cpu="arm7",
            isa="armv4t",
            load_address=hdr.arm7_ram,
            entry_pc=hdr.arm7_entry,
            binary=arm7,
        ),
        encoding="utf-8",
        newline="\n",
    )

    manifest_entries: list[dict[str, object]] = []
    rom_alias_overlays: list[dict[str, object]] = []
    for entry, blob in overlays:
        ov_name = f"ov9_{entry.overlay_id:02d}.bin"
        (overlays_dir / ov_name).write_bytes(blob)
        row = asdict(entry)
        row["file"] = f"overlays/{ov_name}"
        manifest_entries.append(row)
        rom_alias_overlays.append(
            {
                "id": entry.overlay_id,
                "file": ov_name,
                "load_address": f"0x{entry.ram_address:08X}",
                "size": entry.ram_size,
                "bss_size": entry.bss_size,
                "static_init_start": f"0x{entry.static_init_start:08X}",
                "static_init_end": f"0x{entry.static_init_end:08X}",
                "sha1": entry.sha1,
            }
        )

    (out_dir / "overlays.json").write_text(
        json.dumps(rom_alias_overlays, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    manifest: dict[str, object] = {
        "rom": {
            "name": rom_path.name,
            "size": len(rom),
            "sha1": EXPECTED_ROM_SHA1,
            "sha256": EXPECTED_ROM_SHA256,
            "title": hdr.title.decode("ascii"),
            "game_code": hdr.game_code.decode("ascii"),
            "revision": hdr.revision,
        },
        "arm9": {
            "load_address": hdr.arm9_ram,
            "entry_pc": hdr.arm9_entry,
            "size": len(arm9),
            "sha1": sha1_hex(arm9),
        },
        "arm7": {
            "load_address": hdr.arm7_ram,
            "entry_pc": hdr.arm7_entry,
            "size": len(arm7),
            "sha1": sha1_hex(arm7),
        },
        "overlays_arm9": manifest_entries,
    }
    (out_dir / "overlays_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    return manifest


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rom", type=Path, default=DEFAULT_ROM)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    if not args.rom.is_file():
        print(f"ERRO: ROM não encontrada: {args.rom}", file=sys.stderr)
        return 1

    manifest = prepare_rom(args.rom, args.out)
    print(
        f"[prepare] ARM9 {manifest['arm9']['size']} B (sha1={manifest['arm9']['sha1']})"
    )
    print(
        f"[prepare] ARM7 {manifest['arm7']['size']} B (sha1={manifest['arm7']['sha1']})"
    )
    print(f"[prepare] {len(manifest['overlays_arm9'])} overlays ARM9 extraídos para {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""ModRegistry, ConflictEngine (3 estados) e sanitizacao segura de perfis/saves para CDOS Recomp."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

CompatState = Literal["verified", "unverified", "incompatible"]

SAFE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,47}$")
SAFE_VERSION_RE = re.compile(r"^[a-zA-Z0-9._-]{1,24}$")
SAFE_SEED_RE = re.compile(r"^[A-Za-z0-9_-]{1,32}$")
RESERVED_PROFILE_IDS = frozenset({"original", "definitive", "default", "dawn-of-sorrow"})


def slugify_profile_stem(value: str) -> str:
    """Converte nomes reais de patches (ex: 'DoS Definitive+ (v2.0)') em ID seguro compativel com C++."""
    slug = re.sub(r"[^a-z0-9_]+", "-", value.lower())
    slug = slug[:48].strip("-_")
    if not slug or not slug[0].isalnum():
        return ""
    return slug


def sanitize_safe_id(value: str, *, fallback: str = "") -> str:
    """Valida/normaliza um identificador para impedir path traversal."""
    cleaned = value.strip().lower()
    if not cleaned or ".." in cleaned or "/" in cleaned or "\\" in cleaned or ":" in cleaned:
        return fallback
    if not SAFE_ID_RE.match(cleaned):
        return fallback
    return cleaned


def sanitize_seed(value: str) -> str:
    """Normaliza seed de randomizer para caracteres seguros [A-Za-z0-9_-]."""
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "", value.strip())
    return cleaned[:32]


def safe_join_under(base_dir: Path, *parts: str) -> Path:
    """Garante que o caminho final permanece estritamente dentro de base_dir."""
    root = base_dir.resolve()
    target = root.joinpath(*parts).resolve()
    if target != root and root not in target.parents:
        raise ValueError(f"Path traversal detectado: {parts!r} escapou de {root}")
    return target


def atomic_write_bytes(path: Path, data: bytes) -> None:
    """Escreve arquivo de forma atomica (arquivo temporario no mesmo diretorio + os.replace)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    try:
        with tmp.open("wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass


def atomic_write_text(path: Path, text: str) -> None:
    atomic_write_bytes(path, text.encode("utf-8"))


def profile_save_namespace(profile_id: str, version: str, modset_hash: str) -> str:
    """Constroi namespace deterministico <profile_id>-v<version>-<hash8> para saves/savestates."""
    sid = sanitize_safe_id(profile_id)
    if not sid:
        raise ValueError(f"profile_id invalido: {profile_id!r}")
    ver = re.sub(r"[^a-zA-Z0-9._-]+", "", version.strip()) or "1.0"
    if not SAFE_VERSION_RE.match(ver) or ".." in ver:
        ver = "1.0"
    h8 = re.sub(r"[^a-f0-9]+", "", modset_hash.strip().lower())[:8] or "00000000"
    return f"{sid}-v{ver}-{h8}"


@dataclass(frozen=True)
class SelectionRequest:
    campaign_id: str = "dawn-of-sorrow"
    character_pack_id: str = "default"
    baseline_id: str = "original"
    language: str = "en"
    allow_unverified: bool = False
    base_rom_sha1: str = "47530ff87e608f88105a314fdf36dc385f8dec94"
    runtime_compat: str = "cdos-recomp-v1"
    randomizer_seed: str = ""
    randomizer_preset: str = "standard"


@dataclass(frozen=True)
class ConflictDecision:
    state: CompatState
    allowed: bool
    reason: str
    active_profile_id: str
    active_version: str
    patch_file: str | None
    validation_level: str


class ModRegistry:
    def __init__(self, data: dict[str, object], *, data_mods_dir: Path | None = None) -> None:
        self.raw = data
        self.base_rom_sha1 = str(data.get("base_rom_sha1", "")).lower()
        self.runtime_compat = str(data.get("runtime_compat", ""))
        self.data_mods_dir = data_mods_dir
        self.baselines = {str(x["id"]): x for x in data.get("baselines", [])}  # type: ignore[index]
        self.campaigns = {str(x["id"]): x for x in data.get("campaigns", [])}  # type: ignore[index]
        self.character_packs = {str(x["id"]): x for x in data.get("character_packs", [])}  # type: ignore[index]
        self.verified_combinations = list(data.get("verified_combinations", []))  # type: ignore[arg-type]
        self.rescan_external_randomizers()

    def rescan_local_profiles(self) -> None:
        """Descobre automaticamente patches *.dospatch colocados pelo usuario em {data}/mods/profiles/."""
        for cid in [
            k
            for k, v in self.campaigns.items()
            if v.get("validation_level") in ("external_randomizer", "local_user_mod")
        ]:
            self.campaigns.pop(cid, None)
        if self.data_mods_dir is None:
            return
        prof_dir = self.data_mods_dir / "profiles"
        if not prof_dir.is_dir():
            return
        registered_files = {
            str(entry.get("profile_file", "")).lower()
            for group in (self.baselines, self.campaigns, self.character_packs)
            for entry in group.values()
            if entry.get("profile_file")
        }
        ext_priority = {".dospatch": 0, ".xdelta": 1, ".vcdiff": 2, ".xdelta3": 3, ".ips": 4}
        candidates = [
            p for p in prof_dir.iterdir() if p.is_file() and p.suffix.lower() in ext_priority
        ]
        candidates.sort(key=lambda p: (ext_priority[p.suffix.lower()], p.name.lower()))
        for p in candidates:
            if p.name.lower() in registered_files:
                continue
            cid = slugify_profile_stem(p.stem)
            if not cid or cid in RESERVED_PROFILE_IDS or cid in self.campaigns:
                continue
            ext_lc = p.suffix.lower()
            if cid.startswith("dsvrandom-") and len(cid) > len("dsvrandom-"):
                seed_lbl = cid[len("dsvrandom-") :]
                self.campaigns[cid] = {
                    "id": cid,
                    "name": f"DSVania Randomizer ({seed_lbl})",
                    "version": "1.0",
                    "builtin": False,
                    "manual_import": True,
                    "state": "unverified",
                    "validation_level": "external_randomizer",
                    "profile_file": p.name,
                    "supports_ptbr": False,
                    "definitive_compatible": False,
                    "allowed_character_packs": ["default"],
                    "author": "Local randomizer output",
                }
            else:
                suffix_lbl = "" if ext_lc == ".dospatch" else f" ({ext_lc})"
                self.campaigns[cid] = {
                    "id": cid,
                    "name": f"Local Mod: {p.stem}{suffix_lbl}",
                    "version": "1.0",
                    "builtin": False,
                    "manual_import": True,
                    "state": "unverified",
                    "validation_level": "local_user_mod",
                    "profile_file": p.name,
                    "supports_ptbr": False,
                    "definitive_compatible": False,
                    "allowed_character_packs": ["default"],
                    "author": "User local patch",
                }

    def rescan_external_randomizers(self) -> None:
        """Alias retrocompativel para rescan_local_profiles()."""
        self.rescan_local_profiles()

    @classmethod
    def load(cls, registry_path: Path, *, data_mods_dir: Path | None = None) -> "ModRegistry":
        data = json.loads(registry_path.read_text(encoding="utf-8"))
        if data.get("schema") != "cdos.mod-registry.v1":
            raise ValueError(f"Schema de registry inesperado: {data.get('schema')!r}")
        return cls(data, data_mods_dir=data_mods_dir)

    def _profile_installed(self, entry: dict[str, object]) -> tuple[bool, Path | None]:
        if entry.get("builtin"):
            return True, None
        if self.data_mods_dir is None:
            return False, None
        rel = str(entry.get("profile_file", "")).strip()
        if rel and "/" not in rel and "\\" not in rel and ".." not in rel:
            candidate = safe_join_under(self.data_mods_dir, "profiles", rel)
            if candidate.is_file():
                return True, candidate
        entry_id = str(entry.get("id", "")).strip().lower()
        prof_dir = self.data_mods_dir / "profiles"
        if entry_id and prof_dir.is_dir():
            ext_priority = {".dospatch": 0, ".xdelta": 1, ".vcdiff": 2, ".xdelta3": 3, ".ips": 4}
            matches = [
                p
                for p in prof_dir.iterdir()
                if p.is_file()
                and p.suffix.lower() in ext_priority
                and slugify_profile_stem(p.stem) == entry_id
            ]
            if matches:
                matches.sort(key=lambda p: (ext_priority[p.suffix.lower()], p.name.lower()))
                return True, matches[0]
        return False, None

    def is_verified_combination(self, req: SelectionRequest) -> tuple[bool, str]:
        if req.base_rom_sha1.lower() != self.base_rom_sha1:
            return False, "none"
        if req.runtime_compat != self.runtime_compat:
            return False, "none"
        for combo in self.verified_combinations:
            if (
                combo.get("campaign") == req.campaign_id
                and combo.get("character_pack") == req.character_pack_id
                and combo.get("baseline") == req.baseline_id
                and combo.get("language") == req.language
            ):
                level = str(combo.get("validation_level", "none"))
                return level == "full", level
        return False, "none"

    def resolve(self, req: SelectionRequest) -> ConflictDecision:
        """Aplica as regras do ConflictEngine (verified / unverified / incompatible)."""
        if req.base_rom_sha1.lower() != self.base_rom_sha1:
            return ConflictDecision(
                state="incompatible",
                allowed=False,
                reason="ROM base SHA-1 nao confere com o registro verificado (USA ACVE).",
                active_profile_id="invalid",
                active_version="0",
                patch_file=None,
                validation_level="none",
            )
        if req.runtime_compat != self.runtime_compat:
            return ConflictDecision(
                state="incompatible",
                allowed=False,
                reason=f"Runtime '{req.runtime_compat}' incompativel com '{self.runtime_compat}'.",
                active_profile_id="invalid",
                active_version="0",
                patch_file=None,
                validation_level="none",
            )

        camp = self.campaigns.get(req.campaign_id)
        if camp is None:
            return ConflictDecision("incompatible", False, f"Campanha desconhecida: {req.campaign_id}", "invalid", "0", None, "none")
        pack = self.character_packs.get(req.character_pack_id)
        if pack is None:
            return ConflictDecision("incompatible", False, f"Pack de personagem desconhecido: {req.character_pack_id}", "invalid", "0", None, "none")
        base = self.baselines.get(req.baseline_id)
        if base is None:
            return ConflictDecision("incompatible", False, f"Base QoL desconhecida: {req.baseline_id}", "invalid", "0", None, "none")

        # 1. Exclusividade e compatibilidade de campanha vs pack de personagem
        allowed_packs = list(camp.get("allowed_character_packs", []))
        compat_camps = list(pack.get("compatible_campaigns", []))
        pack_compat = bool(pack.get("builtin") and req.character_pack_id == "default") or (
            req.campaign_id in compat_camps
        )
        if req.character_pack_id not in allowed_packs or not pack_compat:
            return ConflictDecision(
                state="incompatible",
                allowed=False,
                reason=(
                    f"Pack '{pack['name']}' nao e compativel com a campanha '{camp['name']}' "
                    "(packs de Julius Mode modificam overlays e slots especificos)."
                ),
                active_profile_id=req.campaign_id,
                active_version=str(camp.get("version", "1.0")),
                patch_file=None,
                validation_level="none",
            )

        # 2. Campanha overhaul nao pode ser empilhada cegamente com Definitive/Definitive+
        if not camp.get("definitive_compatible", False) and req.baseline_id != "original":
            return ConflictDecision(
                state="incompatible",
                allowed=False,
                reason=(
                    f"A campanha '{camp['name']}' e independente e altera overlays proprios; "
                    "nao empilhe com Definitive Edition sem composicao verificada."
                ),
                active_profile_id=req.campaign_id,
                active_version=str(camp.get("version", "1.0")),
                patch_file=None,
                validation_level="none",
            )

        # 3. Pack de personagem custom nao pode empilhar com Definitive+ nao composto
        if not pack.get("builtin", False) and req.baseline_id != "original":
            return ConflictDecision(
                state="incompatible",
                allowed=False,
                reason=(
                    f"O pack '{pack['name']}' foi gerado sobre a ROM USA limpa; "
                    "selecione base Original USA ou gere uma composicao auditada."
                ),
                active_profile_id=req.character_pack_id,
                active_version=str(pack.get("version", "1.0")),
                patch_file=None,
                validation_level="none",
            )

        # 4. Compatibilidade de idioma PT-BR
        if req.language == "ptbr":
            if not camp.get("supports_ptbr", False) or not pack.get("supports_ptbr", False) or not base.get("supports_ptbr", False):
                return ConflictDecision(
                    state="incompatible",
                    allowed=False,
                    reason="A combinacao selecionada nao possui traducao PT-BR validada; use English (en).",
                    active_profile_id=req.campaign_id,
                    active_version=str(camp.get("version", "1.0")),
                    patch_file=None,
                    validation_level="none",
                )

        # 5. Determinar o perfil ativo e verificar presenca fisica em {data}/mods/profiles/
        active_entry: dict[str, object]
        if not camp.get("builtin", False):
            active_entry = camp
        elif not pack.get("builtin", False):
            active_entry = pack
        elif not base.get("builtin", False):
            active_entry = base
        else:
            active_entry = base

        installed, patch_path = self._profile_installed(active_entry)
        if not installed:
            return ConflictDecision(
                state="incompatible",
                allowed=False,
                reason=(
                    f"Mod '{active_entry['name']}' ainda nao esta instalado em "
                    "{data}/mods/profiles/ (use tools/import_local_mod.py)."
                ),
                active_profile_id=str(active_entry["id"]),
                active_version=str(active_entry.get("version", "1.0")),
                patch_file=None,
                validation_level="none",
            )

        # 5.5. Seed Mutator nativo (somente sobre bases USA Original/Definitive verificadas)
        clean_seed = sanitize_seed(req.randomizer_seed)
        if clean_seed:
            if not (camp.get("builtin") and pack.get("builtin") and base.get("builtin")):
                return ConflictDecision(
                    state="incompatible",
                    allowed=False,
                    reason=(
                        "Seed Mutator nativo so opera sobre Dawn of Sorrow Original/Definitive verificados; "
                        "limpe a seed para jogar campanhas overhaul ou packs de personagem."
                    ),
                    active_profile_id=f"seed-{clean_seed.lower()}",
                    active_version=req.randomizer_preset or "standard",
                    patch_file=None,
                    validation_level="none",
                )
            preset = req.randomizer_preset if req.randomizer_preset in ("casual", "standard", "hard") else "standard"
            return ConflictDecision(
                state="unverified",
                allowed=req.allow_unverified,
                reason="Seed Mutator nativo (tabelas nao-progressao de inimigos/drops). Ative opt-in para jogar.",
                active_profile_id=f"seed-{clean_seed.lower()}",
                active_version=preset,
                patch_file=None,
                validation_level="seed_mutator_non_progression",
            )

        # 6. Estado final: verified SOMENTE se estiver na allowlist com validation_level == "full"
        is_ver, val_level = self.is_verified_combination(req)
        entry_state = str(active_entry.get("state", "unverified"))
        if is_ver and entry_state == "verified":
            return ConflictDecision(
                state="verified",
                allowed=True,
                reason="Combinacao verificada para esta ROM base e runtime.",
                active_profile_id=str(active_entry["id"]),
                active_version=str(active_entry.get("version", "1.0")),
                patch_file=str(patch_path) if patch_path else None,
                validation_level=val_level,
            )

        return ConflictDecision(
            state="unverified",
            allowed=req.allow_unverified,
            reason=(
                f"Perfil '{active_entry['name']}' esta em estado 'unverified' "
                f"(validacao='{active_entry.get('validation_level', 'none')}'). "
                "Habilite modo Dev/Audit para testar."
            ),
            active_profile_id=str(active_entry["id"]),
            active_version=str(active_entry.get("version", "1.0")),
            patch_file=str(patch_path) if patch_path else None,
            validation_level=str(active_entry.get("validation_level", "none")),
        )

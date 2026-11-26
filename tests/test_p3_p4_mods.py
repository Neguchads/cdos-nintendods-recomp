"""Testes da Etapa 16A (e futuras 16B-16D): ModRegistry, ConflictEngine 3 estados, XDELTA1, seguranca ZIP e {install}/{data}."""

from __future__ import annotations

import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import import_dsvrandom as idsv  # noqa: E402
import import_local_mod as ilm  # noqa: E402
import import_mod_bundle as imb  # noqa: E402
import mod_resolver as mr  # noqa: E402
import vcdiff_ips as vi  # noqa: E402


class TestFoundation16A(unittest.TestCase):
    def test_detect_patch_format_distinguishes_xdelta1_vcdiff_ips_bps(self) -> None:
        self.assertEqual(vi.detect_patch_format(b"\xd6\xc3\xc4\x00\x00"), "vcdiff")
        self.assertEqual(vi.detect_patch_format(b"%XDZ004%rest"), "xdelta1")
        self.assertEqual(vi.detect_patch_format(b"PATCHEOF"), "ips")
        self.assertEqual(vi.detect_patch_format(b"BPS1xxxx"), "bps")
        self.assertEqual(vi.detect_patch_format(b"DOSPATCHxxxx"), "dospatch")
        self.assertEqual(vi.detect_patch_format(b"randomdata"), "unknown")

        with self.assertRaises(ValueError):
            vi.inspect_vcdiff(b"%XDZ004%legacy_payload")
        with self.assertRaises(ValueError):
            vi.apply_vcdiff(b"src", b"%XDZ004%legacy_payload")

    def test_import_rejects_xdelta1_zip_traversal_and_writes_only_to_data_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp)
            install_dir = t / "install"
            data_dir = t / "data"
            install_dir.mkdir()
            data_dir.mkdir()

            # 1. ZIP with path traversal must raise ValueError
            evil_zip = t / "evil.zip"
            with zipfile.ZipFile(evil_zip, "w") as zf:
                zf.writestr("../../outside.ips", b"PATCHEOF")
            with self.assertRaises(ValueError):
                imb.import_bundle(evil_zip, repo_root=install_dir, data_dir=data_dir)

            # 2. ZIP with XDELTA1 + valid IPS must reject XDELTA1, accept IPS, and never touch install_dir
            mixed_zip = t / "mixed.zip"
            with zipfile.ZipFile(mixed_zip, "w") as zf:
                zf.writestr("defplus/DefinitivePlus.xdelta", b"%XDZ004%fake_xdelta1_body")
                zf.writestr("notouch/dos_notouch.ips", b"PATCH\x00\x00\x10\x00\x02ABEOF")
            cat = imb.import_bundle(mixed_zip, repo_root=install_dir, data_dir=data_dir)
            self.assertEqual(cat["summary"]["accepted"], 1)
            self.assertEqual(cat["summary"]["rejected"], 1)
            self.assertEqual(list(install_dir.rglob("*")), [])
            self.assertTrue((data_dir / "mods" / "local" / "dos_notouch.ips").is_file())
            self.assertTrue((data_dir / "mods" / "catalog.json").is_file())

    def test_conflict_engine_three_states_and_save_namespaces(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data_mods = Path(tmp) / "mods"
            (data_mods / "profiles").mkdir(parents=True)
            (data_mods / "profiles" / "sample-local-mod.dospatch").write_bytes(b"DOSPATCH")
            (data_mods / "profiles" / "DoS Definitive+ (v2.0).xdelta").write_bytes(b"\xd6\xc3\xc4\x00\x00")
            (data_mods / "profiles" / "No Required Touch v1.1.ips").write_bytes(b"PATCHEOF")
            (data_mods / "profiles" / "original.xdelta").write_bytes(b"\xd6\xc3\xc4\x00\x00")
            (data_mods / "profiles" / "definitive.dospatch").write_bytes(b"DOSPATCH")

            reg = mr.ModRegistry.load(ROOT / "mods" / "registry.json", data_mods_dir=data_mods)

            # Repo registry must ship zero third-party mods; reserved IDs never auto-register as campaigns
            self.assertEqual(set(reg.baselines), {"original", "definitive"})
            self.assertEqual(set(reg.character_packs), {"default"})
            self.assertIn("dawn-of-sorrow", reg.campaigns)
            self.assertIn("sample-local-mod", reg.campaigns)
            self.assertIn("dos-definitive-v2-0", reg.campaigns)
            self.assertIn("no-required-touch-v1-1", reg.campaigns)
            self.assertEqual(reg.campaigns["dos-definitive-v2-0"]["profile_file"], "DoS Definitive+ (v2.0).xdelta")
            self.assertEqual(reg.campaigns["no-required-touch-v1-1"]["profile_file"], "No Required Touch v1.1.ips")
            self.assertNotIn("original", reg.campaigns)
            self.assertNotIn("definitive", reg.campaigns)

            # Verified: Dawn of Sorrow + Original USA + EN
            dec = reg.resolve(mr.SelectionRequest(baseline_id="original", language="en"))
            self.assertEqual(dec.state, "verified")
            self.assertTrue(dec.allowed)

            # Unverified: generic local user mod discovered in {data}/mods/profiles/
            dec_unv = reg.resolve(
                mr.SelectionRequest(campaign_id="sample-local-mod", baseline_id="original", allow_unverified=False)
            )
            self.assertEqual(dec_unv.state, "unverified")
            self.assertFalse(dec_unv.allowed)
            self.assertEqual(dec_unv.validation_level, "local_user_mod")

            dec_opt = reg.resolve(
                mr.SelectionRequest(campaign_id="sample-local-mod", baseline_id="original", allow_unverified=True)
            )
            self.assertEqual(dec_opt.state, "unverified")
            self.assertTrue(dec_opt.allowed)

            # Incompatible: stacking local mod + PT-BR, or unknown baseline/pack
            self.assertEqual(
                reg.resolve(
                    mr.SelectionRequest(campaign_id="sample-local-mod", baseline_id="original", language="ptbr")
                ).state,
                "incompatible",
            )
            self.assertEqual(
                reg.resolve(mr.SelectionRequest(campaign_id="sample-local-mod", baseline_id="definitive")).state,
                "incompatible",
            )
            self.assertEqual(
                reg.resolve(mr.SelectionRequest(character_pack_id="missing-pack", baseline_id="original")).state,
                "incompatible",
            )

            # Wrong ROM SHA-1 must be incompatible
            self.assertEqual(
                reg.resolve(mr.SelectionRequest(base_rom_sha1="0" * 40)).state,
                "incompatible",
            )

            # Safe namespace & path traversal rejection
            self.assertEqual(mr.sanitize_safe_id("../hack"), "")
            self.assertEqual(
                mr.profile_save_namespace("sample-local-mod", "1.2", "deadbeefcafe"),
                "sample-local-mod-v1.2-deadbeef",
            )


class TestGenericLocalModImport(unittest.TestCase):
    def test_synthetic_registry_character_packs_and_local_patch_importer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp)
            data_mods = t / "mods"
            (data_mods / "profiles").mkdir(parents=True)
            (data_mods / "profiles" / "sample-pack-a.dospatch").write_bytes(b"DOSPATCH")

            synthetic_reg = {
                "schema": "cdos.mod-registry.v1",
                "base_rom_sha1": "47530ff87e608f88105a314fdf36dc385f8dec94",
                "runtime_compat": "cdos-recomp-v1",
                "baselines": [
                    {"id": "original", "name": "Original USA", "version": "1.0", "builtin": True, "state": "verified", "validation_level": "full", "supports_ptbr": True},
                ],
                "campaigns": [
                    {"id": "dawn-of-sorrow", "name": "Dawn of Sorrow", "version": "1.0", "builtin": True, "state": "verified", "validation_level": "full", "supports_ptbr": True, "definitive_compatible": True, "allowed_character_packs": ["default", "sample-pack-a", "sample-pack-missing"]},
                ],
                "character_packs": [
                    {"id": "default", "name": "Native", "version": "1.0", "builtin": True, "state": "verified", "validation_level": "full", "compatible_campaigns": ["dawn-of-sorrow"], "supports_ptbr": True},
                    {"id": "sample-pack-a", "name": "Sample Pack A", "version": "1.0", "builtin": False, "state": "unverified", "validation_level": "none", "exclusive_group": "custom-pack", "profile_file": "sample-pack-a.dospatch", "compatible_campaigns": ["dawn-of-sorrow"], "supports_ptbr": False},
                    {"id": "sample-pack-missing", "name": "Missing Pack", "version": "1.0", "builtin": False, "state": "unverified", "validation_level": "none", "exclusive_group": "custom-pack", "profile_file": "missing.dospatch", "compatible_campaigns": ["dawn-of-sorrow"], "supports_ptbr": False},
                ],
                "verified_combinations": [
                    {"campaign": "dawn-of-sorrow", "character_pack": "default", "baseline": "original", "language": "en", "validation_level": "full"},
                ],
            }
            reg = mr.ModRegistry(synthetic_reg, data_mods_dir=data_mods)

            dec_blocked = reg.resolve(
                mr.SelectionRequest(character_pack_id="sample-pack-a", baseline_id="original", allow_unverified=False)
            )
            self.assertEqual(dec_blocked.state, "unverified")
            self.assertFalse(dec_blocked.allowed)
            dec_ok = reg.resolve(
                mr.SelectionRequest(character_pack_id="sample-pack-a", baseline_id="original", allow_unverified=True)
            )
            self.assertEqual(dec_ok.state, "unverified")
            self.assertTrue(dec_ok.allowed)
            self.assertEqual(
                reg.resolve(
                    mr.SelectionRequest(character_pack_id="sample-pack-a", baseline_id="original", language="ptbr")
                ).state,
                "incompatible",
            )
            self.assertEqual(
                reg.resolve(
                    mr.SelectionRequest(character_pack_id="sample-pack-missing", baseline_id="original", allow_unverified=True)
                ).state,
                "incompatible",
            )

            # Offline local patch importer (IPS -> DOSPATCH) without any network/hardcoded URLs
            import hashlib

            usa_rom = bytearray(4096)
            usa_rom[0x0C:0x10] = b"ACVE"
            ips_file = t / "custom.ips"
            ips_file.write_bytes(b"PATCH\x00\x01\x00\x00\x04TESTEOF")
            orig_sha1 = ilm.USA_SHA1
            try:
                ilm.USA_SHA1 = hashlib.sha1(usa_rom).hexdigest()
                with self.assertRaises(ValueError):
                    ilm.import_local_patch_file(ips_file, "original", bytes(usa_rom), data_mods_dir=data_mods)
                rep = ilm.import_local_patch_file(ips_file, "my-ips-mod", bytes(usa_rom), data_mods_dir=data_mods)
                self.assertEqual(rep["profile_id"], "my-ips-mod")
                self.assertTrue((data_mods / "profiles" / "my-ips-mod.dospatch").is_file())
            finally:
                ilm.USA_SHA1 = orig_sha1


class TestRandomizer16D(unittest.TestCase):
    def test_dsvrandom_importer_rejects_unmodified_and_imports_synthetic_delta(self) -> None:
        # Testa dsvrandom importer com ROM sintetica de 16 MiB (quando nao ha ROM real, ou usando ROM sintetica).
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp)
            data_mods = t / "data_mods"
            usa_rom = bytearray(16 * 1024 * 1024)
            usa_rom[0x0C:0x10] = b"ACVE"
            # Ajusta sha1 esperado temporariamente para teste sintetico puro (sem precisar de ROM comercial em CI)
            import hashlib

            fake_sha1 = hashlib.sha1(usa_rom).hexdigest()
            orig_sha1 = idsv.USA_SHA1
            try:
                idsv.USA_SHA1 = fake_sha1

                # 1. ROM identica a limpa deve ser rejeitada
                same_rom = t / "same.nds"
                same_rom.write_bytes(usa_rom)
                with self.assertRaises(ValueError):
                    idsv.import_dsvrandom_output(same_rom, "DEMO2026", bytes(usa_rom), data_mods_dir=data_mods)

                # 2. ROM com game code errado deve ser rejeitada
                bad_gc = bytearray(usa_rom)
                bad_gc[0x0C:0x10] = b"XXXX"
                bad_rom = t / "bad.nds"
                bad_rom.write_bytes(bad_gc)
                with self.assertRaises(ValueError):
                    idsv.import_dsvrandom_output(bad_rom, "DEMO2026", bytes(usa_rom), data_mods_dir=data_mods)

                # 3. ROM randomizada valida vira DOSPATCH + JSON atomico e e descoberta pelo ModRegistry
                rand_rom = bytearray(usa_rom)
                rand_rom[0x1000:0x1010] = b"DSVRANDOM_DEMO!!"
                rand_path = t / "randomized.nds"
                rand_path.write_bytes(rand_rom)

                rep = idsv.import_dsvrandom_output(
                    rand_path,
                    "DEMO-2026",
                    bytes(usa_rom),
                    data_mods_dir=data_mods,
                    preset="standard",
                )
                self.assertEqual(rep["profile_id"], "dsvrandom-demo-2026")
                self.assertEqual(rep["validation_state"], "unverified")
                self.assertEqual(rep["validation_level"], "external_randomizer")
                self.assertTrue((data_mods / "profiles" / "dsvrandom-demo-2026.dospatch").is_file())
                self.assertTrue((data_mods / "cache" / "dsvrandom-demo-2026.json").is_file())
                # Nunca copia .nds para dentro de {data}/mods
                self.assertEqual(list(data_mods.rglob("*.nds")), [])

                # Descoberta automatica no ModRegistry Python
                reg = mr.ModRegistry.load(ROOT / "mods" / "registry.json", data_mods_dir=data_mods)
                self.assertIn("dsvrandom-demo-2026", reg.campaigns)
                dec = reg.resolve(
                    mr.SelectionRequest(
                        campaign_id="dsvrandom-demo-2026",
                        baseline_id="original",
                        allow_unverified=True,
                    )
                )
                self.assertEqual(dec.state, "unverified")
                self.assertTrue(dec.allowed)
                self.assertEqual(dec.validation_level, "external_randomizer")

                # Rejeita empilhar dsvrandom com Definitive ou com Seed Mutator nativo
                self.assertEqual(
                    reg.resolve(
                        mr.SelectionRequest(
                            campaign_id="dsvrandom-demo-2026",
                            baseline_id="definitive",
                            allow_unverified=True,
                        )
                    ).state,
                    "incompatible",
                )
                self.assertEqual(
                    reg.resolve(
                        mr.SelectionRequest(
                            campaign_id="dsvrandom-demo-2026",
                            baseline_id="original",
                            allow_unverified=True,
                            randomizer_seed="CASTLE2026",
                        )
                    ).state,
                    "incompatible",
                )

                # Seed Mutator nativo sobre Definitive: Unverified, exige opt-in
                dec_seed_off = reg.resolve(
                    mr.SelectionRequest(randomizer_seed="CASTLE2026", randomizer_preset="hard", allow_unverified=False)
                )
                self.assertEqual(dec_seed_off.state, "unverified")
                self.assertFalse(dec_seed_off.allowed)
                dec_seed_on = reg.resolve(
                    mr.SelectionRequest(randomizer_seed="CASTLE2026", randomizer_preset="hard", allow_unverified=True)
                )
                self.assertEqual(dec_seed_on.state, "unverified")
                self.assertTrue(dec_seed_on.allowed)
                self.assertEqual(dec_seed_on.active_profile_id, "seed-castle2026")
                self.assertEqual(dec_seed_on.active_version, "hard")
            finally:
                idsv.USA_SHA1 = orig_sha1


if __name__ == "__main__":
    unittest.main()

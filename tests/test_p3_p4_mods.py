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
            (data_mods / "profiles" / "eternity-of-sorrow.dospatch").write_bytes(b"DOSPATCH")

            reg = mr.ModRegistry.load(ROOT / "mods" / "registry.json", data_mods_dir=data_mods)

            # Verified: Dawn of Sorrow + Definitive + EN and PT-BR
            for lang in ("en", "ptbr"):
                for base in ("definitive", "original"):
                    dec = reg.resolve(mr.SelectionRequest(baseline_id=base, language=lang))
                    self.assertEqual(dec.state, "verified")
                    self.assertTrue(dec.allowed)

            # Unverified: Eternity installed, blocked without opt-in, allowed with opt-in, never promoted
            dec_unv = reg.resolve(
                mr.SelectionRequest(campaign_id="eternity-of-sorrow", baseline_id="original", allow_unverified=False)
            )
            self.assertEqual(dec_unv.state, "unverified")
            self.assertFalse(dec_unv.allowed)

            dec_opt = reg.resolve(
                mr.SelectionRequest(campaign_id="eternity-of-sorrow", baseline_id="original", allow_unverified=True)
            )
            self.assertEqual(dec_opt.state, "unverified")
            self.assertTrue(dec_opt.allowed)

            # Incompatible: stacking Eternity + Definitive, Eternity + Albus, Eternity + PT-BR, missing Albus
            self.assertEqual(
                reg.resolve(mr.SelectionRequest(campaign_id="eternity-of-sorrow", baseline_id="definitive")).state,
                "incompatible",
            )
            self.assertEqual(
                reg.resolve(
                    mr.SelectionRequest(
                        campaign_id="eternity-of-sorrow", character_pack_id="albus-mode", baseline_id="original"
                    )
                ).state,
                "incompatible",
            )
            self.assertEqual(
                reg.resolve(
                    mr.SelectionRequest(campaign_id="eternity-of-sorrow", baseline_id="original", language="ptbr")
                ).state,
                "incompatible",
            )
            self.assertEqual(
                reg.resolve(mr.SelectionRequest(character_pack_id="albus-mode", baseline_id="original")).state,
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
                mr.profile_save_namespace("eternity-of-sorrow", "1.2", "deadbeefcafe"),
                "eternity-of-sorrow-v1.2-deadbeef",
            )


class TestCampaignsAndCharacterPacks16BC(unittest.TestCase):
    def test_character_packs_exclusive_group_and_manual_slots_uninstalled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data_mods = Path(tmp) / "mods"
            (data_mods / "profiles").mkdir(parents=True)
            for fname in ("albus-mode.dospatch", "model-zx.dospatch", "model-omega.dospatch"):
                (data_mods / "profiles" / fname).write_bytes(b"DOSPATCH")

            reg = mr.ModRegistry.load(ROOT / "mods" / "registry.json", data_mods_dir=data_mods)

            # All three Julius Mode packs share exclusive_group "julius-pack" and remain unverified
            for pack_id in ("albus-mode", "model-zx", "model-omega"):
                pack = reg.character_packs[pack_id]
                self.assertEqual(pack["exclusive_group"], "julius-pack")
                self.assertEqual(pack["state"], "unverified")
                self.assertTrue(reg._profile_installed(pack)[0])
                dec_blocked = reg.resolve(
                    mr.SelectionRequest(character_pack_id=pack_id, baseline_id="original", allow_unverified=False)
                )
                self.assertEqual(dec_blocked.state, "unverified")
                self.assertFalse(dec_blocked.allowed)
                dec_ok = reg.resolve(
                    mr.SelectionRequest(character_pack_id=pack_id, baseline_id="original", allow_unverified=True)
                )
                self.assertEqual(dec_ok.state, "unverified")
                self.assertTrue(dec_ok.allowed)
                # Cannot stack Julius Mode pack over PT-BR or Eternity
                self.assertEqual(
                    reg.resolve(
                        mr.SelectionRequest(character_pack_id=pack_id, baseline_id="original", language="ptbr")
                    ).state,
                    "incompatible",
                )
                self.assertEqual(
                    reg.resolve(
                        mr.SelectionRequest(
                            campaign_id="eternity-of-sorrow", character_pack_id=pack_id, baseline_id="original"
                        )
                    ).state,
                    "incompatible",
                )

            # Manual-import slots must report installed=False and be incompatible when absent
            for manual_cid in ("alucards-requiem-sotn", "alucards-requiem-cv3", "draculas-curse"):
                self.assertFalse(reg._profile_installed(reg.campaigns[manual_cid])[0])
                dec = reg.resolve(
                    mr.SelectionRequest(campaign_id=manual_cid, baseline_id="original", allow_unverified=True)
                )
                self.assertEqual(dec.state, "incompatible")
                self.assertFalse(dec.allowed)

            self.assertFalse(reg._profile_installed(reg.baselines["definitive-plus"])[0])
            self.assertEqual(
                reg.resolve(mr.SelectionRequest(baseline_id="definitive-plus", allow_unverified=True)).state,
                "incompatible",
            )


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

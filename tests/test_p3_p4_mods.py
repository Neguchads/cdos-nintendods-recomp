"""Testes da Etapa 16A (e futuras 16B-16D): ModRegistry, ConflictEngine 3 estados, XDELTA1, seguranca ZIP e {install}/{data}."""

from __future__ import annotations

import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

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


if __name__ == "__main__":
    unittest.main()

"""Tests for opt-in compiler caching without accessing a ROM or a compiler."""
from __future__ import annotations

import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build as build_tool  # noqa: E402


class CMakeCacheLauncherTests(unittest.TestCase):
    def setUp(self):
        self.toolchain = {
            "ninja": Path("ninja"),
            "cc": Path("clang"),
            "cxx": Path("clang++"),
            "rc": Path("llvm-rc"),
        }

    def test_normal_build_never_requires_sccache(self):
        with patch.dict(os.environ, {"NDS_SCCACHE": "0"}):
            with patch.object(build_tool.shutil, "which", side_effect=AssertionError("not expected")):
                args = build_tool.cmake_common_args(self.toolchain, static_exe=False)
        self.assertFalse(any("COMPILER_LAUNCHER" in item for item in args))

    def test_opt_in_configures_both_compilers(self):
        with patch.dict(os.environ, {"NDS_SCCACHE": "1"}):
            with patch.object(build_tool.shutil, "which", return_value="sccache"):
                args = build_tool.cmake_common_args(self.toolchain, static_exe=True)
        expected = build_tool.posix(Path("sccache"))
        self.assertIn(f"-DCMAKE_C_COMPILER_LAUNCHER={expected}", args)
        self.assertIn(f"-DCMAKE_CXX_COMPILER_LAUNCHER={expected}", args)
        self.assertIn("-DCMAKE_EXE_LINKER_FLAGS=-static", args)

    def test_explicit_opt_in_fails_if_launcher_is_missing(self):
        with patch.dict(os.environ, {"NDS_SCCACHE": "1"}):
            with patch.object(build_tool.shutil, "which", return_value=None):
                with self.assertRaisesRegex(SystemExit, "sccache"):
                    build_tool.cmake_common_args(self.toolchain, static_exe=False)


if __name__ == "__main__":
    unittest.main()

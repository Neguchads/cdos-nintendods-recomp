#!/usr/bin/env python3
"""Build PR #15 locally on Windows; no upload, release, or ROM redistribution."""
from pathlib import Path
import hashlib
import os
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parent.parent
ROM = ROOT.parent / "Roms" / "Castlevania - Dawn of Sorrow (USA).nds"
NAME = "CastlevaniaDawnOfSorrowRecomp-v1.0.2-test.1-Windows-x64"
EXPECTED = "47530ff87e608f88105a314fdf36dc385f8dec94"


def run(*args, cwd=ROOT):
    subprocess.run([str(x) for x in args], cwd=cwd, check=True)


def py(*args):
    run(sys.executable, *args)


def git_output(cwd, *args):
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def main():
    if os.name != "nt":
        raise SystemExit("Run on a Windows x64 development PC.")
    if git_output(ROOT, "branch", "--show-current") != "test/v1.0.2-pr15":
        raise SystemExit("Use the isolated test/v1.0.2-pr15 branch.")
    if git_output(ROOT, "status", "--porcelain", "--untracked-files=no"):
        raise SystemExit("Tracked files have local changes; use a clean test checkout.")
    if not ROM.is_file() or ROM.stat().st_size != 67108864:
        raise SystemExit(f"Place your own exact USA ROM locally at: {ROM}")
    with ROM.open("rb") as f:
        if hashlib.file_digest(f, "sha1").hexdigest() != EXPECTED:
            raise SystemExit("ROM SHA-1 mismatch.")
    for name, revision in (("ndsrecomp", "e4a7f419"), ("recomp-ui", "f3f99a96")):
        dep = ROOT.parent / name
        if not dep.is_dir():
            dep = ROOT / "framework" / name
        if not dep.is_dir() or not git_output(dep, "rev-parse", "HEAD").startswith(revision):
            raise SystemExit(f"Prepare {name} at {revision} in a dedicated workspace.")
        if name == "ndsrecomp":
            run("git", "apply", "--reverse", "--check", ROOT / "patches/ndsrecomp-local.patch", cwd=dep)
            if not (dep / "runner/third_party/imgui/imgui.cpp").is_file():
                raise SystemExit("Install Dear ImGui v1.92.9b in ndsrecomp/runner/third_party/imgui.")
    if (ROOT / "mods/intro/opening.mp4").exists():
        raise SystemExit("Remove optional opening.mp4 from this dedicated checkout before packaging.")
    py("tools/setup_toolchains.py")
    py("-m", "unittest", "discover", "-s", "tests", "-v")
    py("tools/package_recomplauncher.py", "--validate-only")
    py("tools/prepare_media_assets.py", "--check-only")
    py("tools/build.py", "prepare")
    py("tools/build.py", "recompiler", "--clean")
    py("tools/build.py", "banks")
    py("tools/build.py", "promote")
    py("tools/build.py", "build", "--clean")
    py("tools/build.py", "smoke")
    dest = ROOT / "dist" / NAME
    py("tools/package_recomplauncher.py", "--out", dest)
    archive = dest.with_suffix(".zip") if "." not in dest.name else dest.parent / (dest.name + ".zip")
    try:
        with zipfile.ZipFile(archive) as z:
            names = set(z.namelist())
            required = {"recomplauncher.json", "game.toml", "CastlevaniaDawnOfSorrow.exe",
                        "runtime/nds_runner.exe", "runtime/SDL3.dll",
                        "mods/ptbr/dos-ptbr.dospatch", "mods/definitive/dos-definitive-en.dospatch",
                        "mods/definitive/dos-definitive-ptbr.dospatch", "SHA256SUMS.txt"}
            if not required <= names or z.testzip() is not None:
                raise RuntimeError("Invalid or incomplete ZIP")
            allowed_runtime = {"runtime/nds_runner.exe", "runtime/SDL3.dll", "runtime/libc++.dll", "runtime/libunwind.dll"}
            for name in names:
                p = Path(name)
                if p.suffix.lower() in {".nds", ".rom", ".gba", ".sav", ".state", ".bin", ".mp4", ".ndshp"} or any(x.lower() in {"recompdata", "saves", "savestates", "bios"} for x in p.parts):
                    raise RuntimeError(f"Unexpected private/game data: {name}")
                if name.startswith("runtime/") and name not in allowed_runtime:
                    raise RuntimeError(f"Unexpected runtime file: {name}; inspect the clean staging tree")
        with archive.open("rb") as f:
            digest = hashlib.file_digest(f, "sha256").hexdigest()
        (archive.parent / (archive.name + ".sha256")).write_text(f"{digest}  {archive.name}\n", encoding="ascii")
    except Exception:
        archive.unlink(missing_ok=True)
        raise
    print(f"Local test ZIP: {archive}\nSHA-256: {digest}")
    print("Experimental build; verify on other CPUs before distribution. No release was published.")


if __name__ == "__main__":
    main()

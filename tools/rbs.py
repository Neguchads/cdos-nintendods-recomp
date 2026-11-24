#!/usr/bin/env python3
"""Windows local build orchestrator. ROM/AOT/cache stay local."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

from rbs_cache import PhaseCache, key
import build
import prepare_rom
import promote_banks

ROOT = Path(__file__).resolve().parent.parent
G = ROOT / "generated"
ROM = ROOT / "Roms" / "Castlevania - Dawn of Sorrow (USA).nds"
FW = ROOT / "framework" / "ndsrecomp"
UI = ROOT / "framework" / "recomp-ui"
CACHE = G / "rbs-cache"


def run(*args, cwd=ROOT):
    subprocess.run(list(map(str, args)), cwd=cwd, check=True)


def py(*args):
    run(sys.executable, *args)


def git(*args, cwd=ROOT):
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def digest(path, algorithm="sha256"):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, algorithm).hexdigest()


def configure_local(profile):
    # Keep upstream scripts usable; do not discover unrelated sibling workspaces.
    build.ROM_PATH = prepare_rom.DEFAULT_ROM = ROM
    build.FRAMEWORK_DIR = promote_banks.NDSRECOMP_DIR = FW
    build.RECOMP_UI_DIR = UI
    promote_banks.INGEST_SCRIPT = FW / "tools" / "ingest_coverage_manifests.py"
    build.ARSENAL_ROOT = ROOT
    os.environ["PATH"] = str(ROOT / ".venv" / "Scripts") + os.pathsep + os.environ["PATH"]
    portable = profile in {"test", "release"}
    original_args = build.cmake_common_args
    sccache = shutil.which("sccache")
    if sccache:
        os.environ["SCCACHE_DIR"] = str(G / "sccache")
        os.environ.pop("SCCACHE_BUCKET", None)
        os.environ.pop("SCCACHE_REDIS", None)
        os.environ.pop("SCCACHE_ENDPOINT", None)
        os.environ["SCCACHE_CACHE_SIZE"] = "10G"
    def args(tc, *, static_exe):
        values = original_args(tc, static_exe=static_exe)
        # Explicit launcher also resets stale CMake values when unavailable.
        for lang in ("C", "CXX"):
            values.append(f"-DCMAKE_{lang}_COMPILER_LAUNCHER={sccache or ''}")
        return values
    build.cmake_common_args = args
    original_log = build.run_logged
    def log(label, cmd, **kw):
        if label == "configure-runner":
            cmd = [str(x).replace("-march=native", "-march=x86-64") if portable else x for x in cmd]
            if profile == "dev":
                cmd = [str(x) + " -g" if str(x).startswith(("-DCMAKE_C_FLAGS_RELEASE=", "-DCMAKE_CXX_FLAGS_RELEASE=")) else x for x in cmd]
        # Stream the long Ninja steps, including to disk.
        if label in {"build-runner", "build-recompiler"}:
            path = build.LOGS_DIR / (label + ".log")
            path.parent.mkdir(parents=True, exist_ok=True)
            print(f"[{label}] {' '.join(map(str, cmd))}", flush=True)
            with path.open("w", encoding="utf-8") as f:
                with subprocess.Popen(list(map(str, cmd)), cwd=kw.get("cwd", ROOT),
                        env=kw.get("env") or build.make_env(), stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace") as p:
                    for line in p.stdout:
                        print(line, end="", flush=True)
                        f.write(line)
                        f.flush()
                    rc = p.wait()
            if rc and kw.get("check", True):
                raise RuntimeError(f"{label} failed: {path}")
            return rc, ""
        return original_log(label, cmd, **kw)
    build.run_logged = log
    # Do not force the linker to run again merely by regenerating an unchanged icon.
    original_icon = build.compile_app_icon_resource
    def icon(tc):
        c = PhaseCache(CACHE)
        c.run("icon", key([build.APP_ICON_ICO, build.APP_ICON_RC, tc["windres"], Path(build.__file__)]),
              [build.APP_ICON_OBJ], lambda: original_icon(tc))
        return build.APP_ICON_OBJ
    build.compile_app_icon_resource = icon


def check_workspace():
    if os.name != "nt":
        raise SystemExit("Use a dedicated Windows x64 checkout.")
    if not ROM.is_file() or digest(ROM, "sha1") != build.ROM_SHA1:
        raise SystemExit(f"Place your own verified USA ROM at {ROM}")
    for directory, revision in ((FW, "e4a7f419"), (UI, "f3f99a96")):
        if not directory.is_dir() or not git("rev-parse", "HEAD", cwd=directory).startswith(revision):
            raise SystemExit(f"Missing or incorrect pinned framework: {directory} ({revision})")
    run("git", "apply", "--reverse", "--check", ROOT / "patches/ndsrecomp-local.patch", cwd=FW)
    if not (FW / "runner/third_party/imgui/imgui.cpp").is_file():
        raise SystemExit("Dear ImGui v1.92.9b missing.")
    for directory in (FW, UI):
        print(f"[RBS] dependency {directory.name}: {git('rev-parse', 'HEAD', cwd=directory)}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--profile", choices=["fast", "dev", "test", "release", "rebuild"], default="fast")
    p.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 4)-2))
    p.add_argument("--version", help="Required for release: e.g. v1.1.0 or v1.0.2-test.1")
    a = p.parse_args()
    if a.jobs < 1:
        p.error("--jobs must be positive")
    if a.profile == "release":
        if not a.version or not re.fullmatch(r"v\d+\.\d+\.\d+(?:-(?:test|beta|rc)\.\d+)?", a.version):
            p.error("release requires a valid --version")
        if git("status", "--porcelain", "--untracked-files=no"):
            p.error("release requires a clean tracked checkout")
        if (ROOT / "mods/intro/opening.mp4").exists():
            p.error("remove optional private video before packaging")
    check_workspace()
    configure_local(a.profile)
    cache = PhaseCache(CACHE)
    force = a.profile == "rebuild"
    tc = build.ensure_toolchains()
    sources = [Path(__file__), Path(build.__file__), Path(prepare_rom.__file__), Path(promote_banks.__file__)]
    tools_key = key([tc["cc"], tc["cxx"], tc["cmake"], build.DSD_EXE, ROOT / "toolchains/manifest.json"])
    rom_key = key([ROM, Path(prepare_rom.__file__)])
    def command(name, **kwargs):
        ns = argparse.Namespace(jobs=a.jobs, clean=force, software_3d=False, frames=600,
                                checkpoint_every=150, port=19962, **kwargs)
        rc = getattr(build, "cmd_" + name)(ns)
        if rc:
            raise RuntimeError(f"{name} returned {rc}")
    def clean_phase(name, dirs):
        for d in dirs:
            if d.exists():
                shutil.rmtree(d)
        command(name)
    cache.run("prepare", rom_key, [G/"inputs"], lambda: clean_phase("prepare", [G/"inputs"]), force)
    analysis = ROOT / "analysis/dsd"
    cache.run("analysis", key([ROM, build.DSD_EXE, Path(build.__file__)]),
              [analysis/"project/arm9/module.yaml"], lambda: clean_phase("analyze", [analysis]), force)
    # CMake/Ninja already tracks dependency changes. Preserve its object tree.
    command("recompiler")
    bank_key = key([G/"inputs", build.RECOMPILER_EXE, FW/"bios",
                    FW/"third_party/freebios/drastic_bios_arm9.bin",
                    FW/"third_party/freebios/drastic_bios_arm7.bin", *sources], tools_key)
    cache.run("banks", bank_key, [G/"banks", G/"system", G/"banks_summary.json"],
              lambda: clean_phase("banks", [G/"banks", G/"system"]), force)
    coverage = promote_banks.find_coverage_manifests()
    symbols = list((analysis/"project/arm9").rglob("symbols.txt"))
    promote_key = key([G/"inputs", build.RECOMPILER_EXE, promote_banks.INGEST_SCRIPT,
                       *sources, *coverage, *symbols], bank_key)
    cache.run("promote", promote_key, [G/"banks-promoted", G/"inputs-promoted", G/"promoted_summary.json"],
              lambda: clean_phase("promote", [G/"seeds/runtime"]), force)
    command("build")
    py("tools/package_recomplauncher.py", "--validate-only")
    if a.profile != "fast":
        # Existing test modules may still use legacy ROM paths; test_prepare_rom
        # receives the local path in this process.
        import unittest
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.discover(str(ROOT/"tests")))
        if not result.wasSuccessful():
            raise SystemExit("Python tests failed")
        run(tc["cmake"], "--build", G/"build-runner", "--target", "dos_enhancements_test",
            "frontend_config_test", "screen_layout_test", "--parallel", a.jobs)
        run(tc["cmake"].parent/"ctest.exe", "--test-dir", G/"build-runner",
            "-R", "^(dos_enhancements_test|frontend_config_test|screen_layout_test)$",
            "--output-on-failure", "--no-tests=error")
    if a.profile in {"test", "release", "rebuild"}:
        command("smoke")
    if a.profile == "release":
        # Package only after successful local build and tests.
        name = f"CastlevaniaDawnOfSorrowRecomp-{a.version}-Windows-x64"
        target = ROOT/"dist"/name
        archive = target.parent/(name+".zip")
        py("tools/package_recomplauncher.py", "--out", target)
        try:
            py("tools/rbs_artifact.py", str(archive))
        except Exception:
            archive.unlink(missing_ok=True)
            raise
        receipt = {"commit": git("rev-parse", "HEAD"), "version": a.version,
                   "archive": archive.name, "sha256": digest(archive), "profile": "release"}
        archive.with_name(archive.name+".build.json").write_text(json.dumps(receipt, indent=2)+"\n", encoding="utf-8")
        print(f"[RBS] validated {archive}; review before uploading.")
    if shutil.which("sccache"):
        run("sccache", "--show-stats")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Pipeline de build e verificação de Castlevania: Dawn of Sorrow Recomp (ACVE)."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARSENAL_ROOT = (ROOT.parents[2] / "_Arsenal") if len(ROOT.parents) > 2 else (ROOT / ".venv")

ROM_PATH = ROOT.parent / "Roms" / "Castlevania - Dawn of Sorrow (USA).nds"
ROM_SHA1 = "47530ff87e608f88105a314fdf36dc385f8dec94"
GAME_TOML = ROOT / "game.toml"

def _resolve_tool_dir(name: str) -> Path:
    sibling = ROOT.parent / name
    if sibling.is_dir():
        return sibling
    return ROOT / "framework" / name


def _reset_stale_cmake_cache(build_dir: Path, expected_src: Path) -> None:
    cache_path = build_dir / "CMakeCache.txt"
    if not cache_path.is_file():
        return
    expected_resolved = str(expected_src.resolve()).replace("\\", "/").lower()
    for line in cache_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("CMAKE_HOME_DIRECTORY:INTERNAL="):
            cached = line.split("=", 1)[1].strip().replace("\\", "/").lower()
            if cached != expected_resolved:
                cache_path.unlink(missing_ok=True)
                cmake_files = build_dir / "CMakeFiles"
                if cmake_files.is_dir():
                    shutil.rmtree(cmake_files)
            return


FRAMEWORK_DIR = _resolve_tool_dir("ndsrecomp")
RECOMP_UI_DIR = _resolve_tool_dir("recomp-ui")

TOOLCHAINS_DIR = ROOT / "toolchains"
LLVM_BIN_DIR = TOOLCHAINS_DIR / "llvm-mingw" / "bin"
LLVM_TARGET_BIN_DIR = TOOLCHAINS_DIR / "llvm-mingw" / "x86_64-w64-mingw32" / "bin"
SDL3_PREFIX_DIR = TOOLCHAINS_DIR / "sdl3" / "x86_64-w64-mingw32"
DSD_EXE = TOOLCHAINS_DIR / "dsd" / "dsd.exe"

GENERATED_DIR = ROOT / "generated"
INPUTS_DIR = GENERATED_DIR / "inputs"
BANKS_DIR = GENERATED_DIR / "banks"
PROMOTED_BANKS_DIR = GENERATED_DIR / "banks-promoted"
SYSTEM_DIR = GENERATED_DIR / "system"
RECOMPILER_BUILD_DIR = GENERATED_DIR / "build-recompiler"
RUNNER_BUILD_DIR = GENERATED_DIR / "build-runner"

RUNTIME_DIR = ROOT / "runtime"
RUN_DIR = ROOT / "run"
LOGS_DIR = RUN_DIR / "logs"
SMOKE_DIR = RUN_DIR / "smoke"
BIOS_EMPTY_DIR = RUN_DIR / "bios"
SAVES_DIR = ROOT / "saves"
ANALYSIS_DIR = ROOT / "analysis" / "dsd"

RECOMPILER_EXE = RECOMPILER_BUILD_DIR / "nds_recompile.exe"
BUILT_RUNNER_EXE = RUNNER_BUILD_DIR / "nds_runner.exe"
RUNTIME_RUNNER_EXE = RUNTIME_DIR / "nds_runner.exe"

LAUNCHER_DIR = ROOT / "launcher"
APP_ICON_ICO = ROOT / "assets" / "recomplauncher" / "icon.ico"
APP_ICON_RC = LAUNCHER_DIR / "app_icon.rc"
APP_ICON_OBJ = GENERATED_DIR / "app_icon.o"
LAUNCHER_SRC = LAUNCHER_DIR / "launcher_win32.cpp"
LAUNCHER_EXE = ROOT / "CastlevaniaDawnOfSorrow.exe"

sys.path.insert(0, str(ROOT / "tools"))
import prepare_rom  # noqa: E402
import promote_banks  # noqa: E402


def die(msg: str) -> None:
    raise SystemExit(f"[erro] {msg}")


def posix(path: Path) -> str:
    return path.resolve().as_posix()


def find_cmake() -> Path:
    candidates = [
        ARSENAL_ROOT / ".venv" / "Lib" / "site-packages" / "cmake" / "data" / "bin" / "cmake.exe",
        Path(shutil.which("cmake") or ""),
    ]
    for p in candidates:
        if p and p.is_file():
            return p
    die("cmake.exe não encontrado no _Arsenal/.venv nem no PATH")


def find_ninja() -> Path:
    candidates = [
        ARSENAL_ROOT / ".venv" / "Scripts" / "ninja.exe",
        Path(shutil.which("ninja") or ""),
    ]
    for p in candidates:
        if p and p.is_file():
            return p
    die("ninja.exe não encontrado no _Arsenal/.venv nem no PATH")


def ensure_toolchains() -> dict[str, Path]:
    paths = {
        "cmake": find_cmake(),
        "ninja": find_ninja(),
        "cc": LLVM_BIN_DIR / "x86_64-w64-mingw32-clang.exe",
        "cxx": LLVM_BIN_DIR / "x86_64-w64-mingw32-clang++.exe",
        "rc": LLVM_BIN_DIR / "llvm-rc.exe",
        "windres": LLVM_BIN_DIR / "x86_64-w64-mingw32-windres.exe",
        "sdl3_config": SDL3_PREFIX_DIR / "lib" / "cmake" / "SDL3" / "SDL3Config.cmake",
        "sdl3_dll": SDL3_PREFIX_DIR / "bin" / "SDL3.dll",
        "libcxx_dll": LLVM_TARGET_BIN_DIR / "libc++.dll",
        "libunwind_dll": LLVM_TARGET_BIN_DIR / "libunwind.dll",
    }
    missing = [k for k, p in paths.items() if not p.is_file()]
    if missing:
        die(
            f"componentes de toolchain ausentes ({', '.join(missing)}). "
            "Rode: python tools/setup_toolchains.py"
        )
    return paths


def make_env() -> dict[str, str]:
    env = os.environ.copy()
    path_parts = [
        str(LLVM_BIN_DIR),
        str(LLVM_TARGET_BIN_DIR),
        str(find_ninja().parent),
        str(find_cmake().parent),
        env.get("PATH", ""),
    ]
    env["PATH"] = os.pathsep.join(path_parts)
    env["NDS_FREEBIOS"] = "on"
    return env


def run_logged(
    label: str,
    cmd: list[object],
    *,
    cwd: Path = ROOT,
    env: dict[str, str] | None = None,
    check: bool = True,
) -> tuple[int, str]:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / f"{label}.log"
    str_cmd = [str(c) for c in cmd]
    print(f"[{label}] {' '.join(str_cmd)}", flush=True)
    proc = subprocess.run(
        str_cmd,
        cwd=str(cwd),
        env=env or make_env(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    log_path.write_text(proc.stdout, encoding="utf-8", newline="\n")
    if proc.returncode != 0 and check:
        tail = "\n".join(proc.stdout.splitlines()[-30:])
        die(f"{label} falhou (exit {proc.returncode}). Log: {log_path}\n{tail}")
    return proc.returncode, proc.stdout


def cmake_common_args(tc: dict[str, Path], *, static_exe: bool) -> list[str]:
    args = [
        "-G",
        "Ninja",
        "-DCMAKE_BUILD_TYPE=Release",
        f"-DCMAKE_MAKE_PROGRAM={posix(tc['ninja'])}",
        f"-DCMAKE_C_COMPILER={posix(tc['cc'])}",
        f"-DCMAKE_CXX_COMPILER={posix(tc['cxx'])}",
        f"-DCMAKE_RC_COMPILER={posix(tc['rc'])}",
        "-DNDSRECOMP_COMPILER_CACHE=OFF",
    ]
    # Opt-in: do not require sccache for users running the normal build.
    if os.environ.get("NDS_SCCACHE") == "1":
        launcher = shutil.which("sccache")
        if not launcher:
            die("NDS_SCCACHE=1 exige sccache instalado no PATH.")
        args.extend([
            f"-DCMAKE_C_COMPILER_LAUNCHER={posix(Path(launcher))}",
            f"-DCMAKE_CXX_COMPILER_LAUNCHER={posix(Path(launcher))}",
        ])
    if static_exe:
        args.append("-DCMAKE_EXE_LINKER_FLAGS=-static")
    return args


def cmd_status(_args: argparse.Namespace) -> int:
    print("Castlevania: Dawn of Sorrow (ACVE) — Status\n")
    for label, path in (
        ("ROM", ROM_PATH),
        ("ndsrecomp", FRAMEWORK_DIR / "runner" / "CMakeLists.txt"),
        ("recomp-ui", RECOMP_UI_DIR / "src" / "recomp_runtime_ui.h"),
        ("llvm-mingw", LLVM_BIN_DIR / "x86_64-w64-mingw32-clang.exe"),
        ("SDL3", SDL3_PREFIX_DIR / "lib" / "cmake" / "SDL3" / "SDL3Config.cmake"),
        ("dsd", DSD_EXE),
        ("arm9.bin", INPUTS_DIR / "arm9.bin"),
        ("nds_recompile", RECOMPILER_EXE),
        ("dos_arm9_dispatch", BANKS_DIR / "dos_arm9_dispatch.c"),
        ("freebios_arm9", SYSTEM_DIR / "freebios_arm9_dispatch.c"),
        ("nds_runner", RUNTIME_RUNNER_EXE),
        ("launcher_exe", LAUNCHER_EXE),
    ):
        state = "OK" if path.is_file() else "MISSING"
        print(f"  {label:<18} [{state}] {path}")
    return 0


def cmd_prepare(_args: argparse.Namespace) -> int:
    if not ROM_PATH.is_file():
        die(f"ROM não encontrada: {ROM_PATH}")
    manifest = prepare_rom.prepare_rom(ROM_PATH, INPUTS_DIR)
    print(
        f"[prepare] OK: ARM9 {manifest['arm9']['size']} B, "
        f"ARM7 {manifest['arm7']['size']} B, "
        f"{len(manifest['overlays_arm9'])} overlays"
    )
    return 0


def cmd_recompiler(args: argparse.Namespace) -> int:
    tc = ensure_toolchains()
    recomp_src = FRAMEWORK_DIR / "recompiler"
    if not recomp_src.is_dir():
        die(f"fonte do recompiler ausente: {recomp_src}")
    if args.clean and RECOMPILER_BUILD_DIR.exists():
        shutil.rmtree(RECOMPILER_BUILD_DIR)
    RECOMPILER_BUILD_DIR.mkdir(parents=True, exist_ok=True)
    _reset_stale_cmake_cache(RECOMPILER_BUILD_DIR, recomp_src)
    run_logged(
        "configure-recompiler",
        [
            tc["cmake"],
            "-S",
            posix(recomp_src),
            "-B",
            posix(RECOMPILER_BUILD_DIR),
            *cmake_common_args(tc, static_exe=True),
        ],
    )
    build_cmd: list[object] = [
        tc["cmake"],
        "--build",
        posix(RECOMPILER_BUILD_DIR),
        "--parallel",
        str(args.jobs),
    ]
    run_logged("build-recompiler", build_cmd)
    if not RECOMPILER_EXE.is_file():
        die(f"nds_recompile.exe não gerado em {RECOMPILER_EXE}")
    ctest = tc["cmake"].parent / "ctest.exe"
    run_logged(
        "test-recompiler",
        [ctest, "--test-dir", posix(RECOMPILER_BUILD_DIR), "--output-on-failure"],
    )
    print(f"[recompiler] OK: {RECOMPILER_EXE} + CTest verde")
    return 0


def emit_bank(
    config: Path,
    binary: Path,
    out_dir: Path,
    bank: str,
    shards: int | None,
    *,
    validate_live_bytes: bool = False,
) -> dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    dispatch = out_dir / f"{bank}_dispatch.c"
    if dispatch.exists():
        dispatch.unlink()
    cmd: list[object] = [
        RECOMPILER_EXE,
        "--config",
        config,
        "--bin",
        binary,
        "--out",
        out_dir,
        "--bank",
        bank,
    ]
    if shards is not None:
        cmd += ["--shards", str(shards)]
    if validate_live_bytes:
        cmd.append("--validate-live-bytes")
    _, output = run_logged(f"bank-{bank}", cmd)
    if not dispatch.is_file() or dispatch.stat().st_size == 0:
        die(f"dispatch não gerado: {dispatch}")
    summary = {"bank": bank}
    for line in output.splitlines():
        if "[finder] functions=" in line or "[emit] bank " in line or "[reloc-scan]" in line:
            print(f"  {line.strip()}")
            if "[finder] functions=" in line:
                summary["finder"] = line.strip()
            if "[emit] bank " in line:
                summary["emit"] = line.strip()
    return summary


def cmd_banks(_args: argparse.Namespace) -> int:
    if not RECOMPILER_EXE.is_file():
        die("nds_recompile.exe não compilado. Rode: python tools/build.py recompiler")
    for req in (INPUTS_DIR / "arm9.toml", INPUTS_DIR / "arm9.bin", INPUTS_DIR / "arm7.toml", INPUTS_DIR / "arm7.bin"):
        if not req.is_file():
            die(f"arquivo de entrada ausente: {req}. Rode: python tools/build.py prepare")

    summaries = [
        emit_bank(
            INPUTS_DIR / "arm9.toml",
            INPUTS_DIR / "arm9.bin",
            BANKS_DIR,
            "dos_arm9",
            8,
            validate_live_bytes=True,
        ),
        emit_bank(
            INPUTS_DIR / "arm7.toml",
            INPUTS_DIR / "arm7.bin",
            BANKS_DIR,
            "dos_arm7",
            4,
            validate_live_bytes=True,
        ),
        # Bancos de sistema DEVEM ser single-shard (runner/CMakeLists.txt referencia freebios_arm9.c literalmente).
        emit_bank(
            FRAMEWORK_DIR / "bios" / "freebios9.toml",
            FRAMEWORK_DIR / "third_party" / "freebios" / "drastic_bios_arm9.bin",
            SYSTEM_DIR,
            "freebios_arm9",
            None,
        ),
        emit_bank(
            FRAMEWORK_DIR / "bios" / "freebios7.toml",
            FRAMEWORK_DIR / "third_party" / "freebios" / "drastic_bios_arm7.bin",
            SYSTEM_DIR,
            "freebios_arm7",
            None,
        ),
    ]
    (GENERATED_DIR / "banks_summary.json").write_text(
        json.dumps(summaries, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"[banks] OK: {len(list(BANKS_DIR.glob('*.c')))} C em {BANKS_DIR}, {len(list(SYSTEM_DIR.glob('*.c')))} C em {SYSTEM_DIR}")
    return 0


def cmd_promote(_args: argparse.Namespace) -> int:
    promote_banks.promote_all()
    return 0


def compile_app_icon_resource(tc: dict[str, Path]) -> Path:
    if not APP_ICON_RC.is_file():
        die(f"script de recurso ausente: {APP_ICON_RC}")
    if not APP_ICON_ICO.is_file():
        die(f"icone .ico ausente: {APP_ICON_ICO}. Rode: python tools/prepare_media_assets.py")
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    run_logged(
        "build-app-icon",
        [
            tc["windres"],
            "-I",
            posix(LAUNCHER_DIR),
            "-i",
            posix(APP_ICON_RC),
            "-O",
            "coff",
            "-o",
            posix(APP_ICON_OBJ),
        ],
    )
    if not APP_ICON_OBJ.is_file():
        die(f"objeto de recurso nao gerado: {APP_ICON_OBJ}")
    return APP_ICON_OBJ


def build_launcher_exe(tc: dict[str, Path], icon_obj: Path) -> Path:
    if not LAUNCHER_SRC.is_file():
        die(f"fonte do launcher ausente: {LAUNCHER_SRC}")
    run_logged(
        "build-launcher",
        [
            tc["cxx"],
            "-std=c++20",
            "-O2",
            "-Wall",
            "-Wextra",
            "-mwindows",
            "-municode",
            "-static",
            posix(LAUNCHER_SRC),
            posix(icon_obj),
            "-lcomdlg32",
            "-lole32",
            "-lshell32",
            "-luser32",
            "-luuid",
            "-o",
            posix(LAUNCHER_EXE),
        ],
    )
    if not LAUNCHER_EXE.is_file():
        die(f"executavel launcher nao gerado em {LAUNCHER_EXE}")
    return LAUNCHER_EXE


def cmd_launcher(_args: argparse.Namespace) -> int:
    tc = ensure_toolchains()
    icon_obj = compile_app_icon_resource(tc)
    out = build_launcher_exe(tc, icon_obj)
    print(f"[launcher] OK: {out} ({out.stat().st_size} bytes)")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    tc = ensure_toolchains()
    runner_src = FRAMEWORK_DIR / "runner"
    if not (BANKS_DIR / "dos_arm9_dispatch.c").is_file():
        die("bancos não gerados. Rode: python tools/build.py banks")
    if args.clean and RUNNER_BUILD_DIR.exists():
        shutil.rmtree(RUNNER_BUILD_DIR)
    RUNNER_BUILD_DIR.mkdir(parents=True, exist_ok=True)
    _reset_stale_cmake_cache(RUNNER_BUILD_DIR, runner_src)
    icon_obj = compile_app_icon_resource(tc)
    has_promoted = any(PROMOTED_BANKS_DIR.glob("*_[0-9][0-9].c"))
    if has_promoted:
        bank_flags = [
            "-DNDS_TITLE_BANK_DIR=",
            "-DNDS_TITLE_ROM_SHA1=",
            f"-DNDS_TITLE_BANK_DIRS={posix(BANKS_DIR)};{posix(PROMOTED_BANKS_DIR)}",
            f"-DNDS_TITLE_ROM_SHA1S={ROM_SHA1};{ROM_SHA1}",
        ]
    else:
        bank_flags = [
            f"-DNDS_TITLE_BANK_DIR={posix(BANKS_DIR)}",
            f"-DNDS_TITLE_ROM_SHA1={ROM_SHA1}",
            "-DNDS_TITLE_BANK_DIRS=",
            "-DNDS_TITLE_ROM_SHA1S=",
        ]
    run_logged(
        "configure-runner",
        [
            tc["cmake"],
            "-S",
            posix(runner_src),
            "-B",
            posix(RUNNER_BUILD_DIR),
            *cmake_common_args(tc, static_exe=False),
            f"-DCMAKE_EXE_LINKER_FLAGS=\"{posix(icon_obj)}\"",
            "-DNDS_SDL_BACKEND=SDL3",
            f"-DSDL3_DIR={posix(SDL3_PREFIX_DIR / 'lib' / 'cmake' / 'SDL3')}",
            f"-DCMAKE_PREFIX_PATH={posix(SDL3_PREFIX_DIR)}",
            f"-DNDS_GENERATED_DIR={posix(SYSTEM_DIR)}",
            f"-DNDS_RECOMP_UI_ROOT={posix(RECOMP_UI_DIR)}",
            "-DNDS_BOOTSTRAP_FIRMWARE=ON",
            "-DNDS_LEAN_DIAGNOSTICS=ON",
            "-DNDS_GX_COMMAND_CACHE=ON",
            "-DNDS_CAPTURE_VIEW_REUSE=ON",
            "-DNDS_3D_GEOMETRY=NATIVE",
            "-DCMAKE_C_FLAGS_RELEASE=-O2 -DNDEBUG -march=native",
            "-DCMAKE_CXX_FLAGS_RELEASE=-O3 -DNDEBUG -march=native",
            f"-DNDS_ENABLE_COMPUTE_RENDERER={'OFF' if args.software_3d else 'ON'}",
            *bank_flags,
        ],
    )
    run_logged(
        "build-runner",
        [
            tc["cmake"],
            "--build",
            posix(RUNNER_BUILD_DIR),
            "--target",
            "nds_runner",
            "--parallel",
            str(args.jobs),
        ],
    )
    if not BUILT_RUNNER_EXE.is_file():
        die(f"nds_runner.exe não gerado em {BUILT_RUNNER_EXE}")

    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    for src in (BUILT_RUNNER_EXE, tc["sdl3_dll"], tc["libcxx_dll"], tc["libunwind_dll"]):
        dst = RUNTIME_DIR / src.name
        if not dst.is_file() or dst.stat().st_mtime < src.stat().st_mtime or dst.stat().st_size != src.stat().st_size:
            shutil.copy2(src, dst)
    launcher_out = build_launcher_exe(tc, icon_obj)
    print(f"[build] OK: {RUNTIME_RUNNER_EXE} + {launcher_out}")
    return 0


class DebugClient:
    def __init__(self, port: int, timeout: float = 120.0) -> None:
        self.sock = socket.create_connection(("127.0.0.1", port), timeout=timeout)
        self.buf = b""

    def close(self) -> None:
        self.sock.close()

    def cmd(self, name: str, **args: object) -> dict:
        args["cmd"] = name
        self.sock.sendall((json.dumps(args) + "\n").encode("utf-8"))
        while b"\n" not in self.buf:
            chunk = self.sock.recv(1 << 16)
            if not chunk:
                raise RuntimeError("debug server encerrou a conexão")
            self.buf += chunk
        line, self.buf = self.buf.split(b"\n", 1)
        reply = json.loads(line.decode("utf-8"))
        if isinstance(reply, dict) and "error" in reply:
            raise RuntimeError(f"{name}: {reply['error']}")
        return reply

    def vblank(self) -> int:
        return int(self.cmd("event_counts")["vblank9"])

    def advance_to(self, target: int) -> None:
        for _ in range(400):
            reply = self.cmd(
                "run_to_event",
                event="vblank9",
                count=target,
                max_rounds=50_000_000,
            )
            if reply.get("terminal"):
                raise RuntimeError(
                    f"HALTED: arm9={reply.get('reason9')!r} arm7={reply.get('reason7')!r}"
                )
            if reply.get("stalled"):
                raise RuntimeError(f"stalled antes de vblank9 {target}")
            if self.vblank() >= target:
                return
        raise RuntimeError(f"não alcançou vblank9 {target}")

    def capture_png(self, path: Path) -> float:
        from PIL import Image, ImageStat

        frames = []
        for engine in ("A", "B"):
            fb = self.cmd("framebuffer", engine=engine)
            raw = bytes.fromhex(fb["rgb"])
            frames.append(Image.frombytes("RGB", (fb["w"], fb["h"]), raw))
        combined = Image.new("RGB", (frames[0].width, frames[0].height + frames[1].height))
        combined.paste(frames[0], (0, 0))
        combined.paste(frames[1], (0, frames[0].height))
        combined.save(path)
        grey = combined.convert("L")
        return float(ImageStat.Stat(grey).mean[0])


def _snapshot_dispatch_misses(directory: Path) -> dict[str, int]:
    snap: dict[str, int] = {}
    for p in directory.glob("dispatch_misses*.log"):
        try:
            snap[p.name] = p.stat().st_size
        except OSError:
            snap[p.name] = -1
    return snap


def cmd_smoke(args: argparse.Namespace) -> int:
    if not RUNTIME_RUNNER_EXE.is_file():
        die("nds_runner.exe não encontrado em runtime/. Rode: python tools/build.py build")
    if not ROM_PATH.is_file():
        die(f"ROM não encontrada: {ROM_PATH}")

    SMOKE_DIR.mkdir(parents=True, exist_ok=True)
    BIOS_EMPTY_DIR.mkdir(parents=True, exist_ok=True)
    misses_before = _snapshot_dispatch_misses(RUNTIME_DIR)

    stdout_path = SMOKE_DIR / "runner.stdout.log"
    stderr_path = SMOKE_DIR / "runner.stderr.log"
    cmd = [
        str(RUNTIME_RUNNER_EXE),
        str(BIOS_EMPTY_DIR),
        "--serve",
        "--port",
        str(args.port),
        "--rom",
        str(ROM_PATH),
        "--config",
        str(GAME_TOML),
        "--freebios",
        "--generated-firmware",
        "--boot",
        "direct",
        "--startup-mode",
        "automatic",
        "--no-save",
    ]
    print(f"[smoke] iniciando runner na porta {args.port} ({args.frames} vblanks)...", flush=True)
    proc = subprocess.Popen(
        cmd,
        cwd=str(RUNTIME_DIR),
        env=make_env(),
        stdout=stdout_path.open("wb"),
        stderr=stderr_path.open("wb"),
    )

    report: dict[str, object] = {
        "rom": ROM_PATH.name,
        "frames_target": args.frames,
        "checkpoints": [],
        "failures": [],
    }
    luminances: list[float] = []
    client: DebugClient | None = None
    try:
        for _ in range(120):
            if proc.poll() is not None:
                raise RuntimeError(f"runner encerrou cedo (rc={proc.returncode})")
            try:
                client = DebugClient(args.port)
                break
            except OSError:
                time.sleep(0.25)
        if client is None:
            raise RuntimeError("debug server não respondeu")

        client.cmd("reset")
        target = 0
        while target < args.frames:
            target = min(target + args.checkpoint_every, args.frames)
            client.advance_to(target)
            shot_path = SMOKE_DIR / f"frame-{target:06d}.png"
            lum = client.capture_png(shot_path)
            luminances.append(lum)
            report["checkpoints"].append(
                {"phase": "boot", "vblank": client.vblank(), "luminance": round(lum, 2), "file": shot_path.name}
            )
            print(f"  vblank {client.vblank():>5} -> {shot_path.name} (luma={lum:.2f})", flush=True)

        # Pulso de Start para avançar intro/logo e capturar mais 120 frames
        client.cmd("keys", mask=0x0FFF & ~(1 << 3))
        client.advance_to(client.vblank() + 4)
        client.cmd("keys", mask=0x0FFF)
        client.advance_to(client.vblank() + 120)
        shot_post = SMOKE_DIR / "frame-after-start.png"
        lum_post = client.capture_png(shot_post)
        luminances.append(lum_post)
        report["checkpoints"].append(
            {"phase": "after_start", "vblank": client.vblank(), "luminance": round(lum_post, 2), "file": shot_post.name}
        )
        print(f"  vblank {client.vblank():>5} -> {shot_post.name} (luma={lum_post:.2f})", flush=True)

        report["static_coverage"] = client.cmd("static_coverage")
        report["dispatch_stats"] = client.cmd("dispatch_stats")
        report["final_vblank"] = client.vblank()
    except Exception as exc:  # noqa: BLE001
        report["failures"].append(str(exc))
    finally:
        if client is not None:
            try:
                client.close()
            except OSError:
                pass
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()

    stderr_text = stderr_path.read_text(encoding="utf-8", errors="replace")
    banks_registered = f"registered configured title banks for {ROM_SHA1}" in stderr_text
    report["title_banks_registered"] = banks_registered
    if not banks_registered:
        report["failures"].append("bancos nativos do título não foram registrados no log stderr")

    misses_after = _snapshot_dispatch_misses(RUNTIME_DIR)
    grown = [
        name for name, sz in sorted(misses_after.items()) if sz > 0 and sz > misses_before.get(name, 0)
    ]
    report["dispatch_miss_logs_grown"] = grown
    if grown:
        report["failures"].append(f"dispatch misses em {', '.join(grown)}")

    lit = [x for x in luminances if x > 2.0]
    report["frames_captured"] = len(luminances)
    report["frames_non_black"] = len(lit)
    if not lit:
        report["failures"].append("todos os frames capturados ficaram pretos (luma <= 2.0)")

    report["passed"] = not report["failures"]
    report_path = SMOKE_DIR / "report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"[smoke] {'PASS' if report['passed'] else 'FAIL'} — relatório em {report_path}")
    for err in report["failures"]:
        print(f"  ! {err}")
    return 0 if report["passed"] else 1


def cmd_analyze(_args: argparse.Namespace) -> int:
    if not DSD_EXE.is_file():
        die(f"dsd.exe ausente: {DSD_EXE}. Rode: python tools/setup_toolchains.py")
    if not ROM_PATH.is_file():
        die(f"ROM não encontrada: {ROM_PATH}")
    extract_dir = ANALYSIS_DIR / "extracted"
    project_dir = ANALYSIS_DIR / "project"
    build_dir = ANALYSIS_DIR / "build"
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    if not (extract_dir / "config.yaml").is_file():
        run_logged(
            "dsd-extract",
            [DSD_EXE, "rom", "extract", "--rom", ROM_PATH, "--output-path", extract_dir],
        )
    if not (project_dir / "arm9" / "module.yaml").is_file():
        rc, out = run_logged(
            "dsd-init",
            [
                DSD_EXE,
                "init",
                "--rom-config",
                extract_dir / "config.yaml",
                "--output-path",
                project_dir,
                "--build-path",
                build_dir,
            ],
            check=False,
        )
        if rc != 0:
            print(f"[analyze] aviso: dsd init retornou {rc}; veja run/logs/dsd-init.log")
    print(f"[analyze] arquivos em {ANALYSIS_DIR}")
    return 0


def cmd_ptbr_patch(_args: argparse.Namespace) -> int:
    import build_ptbr_patch  # noqa: E402

    return build_ptbr_patch.main([])


def cmd_play(_args: argparse.Namespace) -> int:
    if not RUNTIME_RUNNER_EXE.is_file():
        die("nds_runner.exe não encontrado em runtime/. Rode: python tools/build.py build")
    BIOS_EMPTY_DIR.mkdir(parents=True, exist_ok=True)
    SAVES_DIR.mkdir(parents=True, exist_ok=True)
    savestates_dir = RUN_DIR / "savestates"
    savestates_dir.mkdir(parents=True, exist_ok=True)
    ptbr_patch = ROOT / "mods" / "ptbr" / "dos-ptbr.dospatch"
    cmd = [
        str(RUNTIME_RUNNER_EXE),
        str(BIOS_EMPTY_DIR),
        "--interactive",
        "--rom",
        str(ROM_PATH),
    ]
    if ptbr_patch.is_file():
        cmd += ["--ptbr-patch", str(ptbr_patch)]
    cmd += [
        "--config",
        str(GAME_TOML),
        "--freebios",
        "--generated-firmware",
        "--boot",
        "direct",
        "--startup-mode",
        "automatic",
        "--diagnostics",
        "off",
        "--no-coverage-manifest",
        "--runtime-settings-path",
        str(SAVES_DIR / "dos-settings.ini"),
        "--savestate-dir",
        str(savestates_dir),
        "--save-path",
        str(SAVES_DIR / "dos.sav"),
        "--firmware-state-path",
        str(RUN_DIR / "firmware_state.bin"),
    ]
    env = make_env()
    env["NDS_HOSTPROF"] = "off"
    return subprocess.call(cmd, cwd=str(RUNTIME_DIR), env=env)


def cmd_all(args: argparse.Namespace) -> int:
    for fn in (cmd_prepare, cmd_recompiler, cmd_banks, cmd_build, cmd_smoke):
        rc = fn(args)
        if rc != 0:
            return rc
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)
    jobs_default = max(1, (os.cpu_count() or 4) - 1)

    sub.add_parser("status", help="Mostra estado das ferramentas e artefatos")
    sub.add_parser("prepare", help="Valida ROM e extrai ARM9/ARM7/overlays")

    p_rec = sub.add_parser("recompiler", help="Compila e testa nds_recompile.exe")
    p_rec.add_argument("--jobs", type=int, default=jobs_default)
    p_rec.add_argument("--clean", action="store_true")

    sub.add_parser("banks", help="Gera bancos C estáticos (título + FreeBIOS)")
    sub.add_parser("promote", help="Promove overlays, ARM7 alias e cobertura para bancos C nativos")
    sub.add_parser("ptbr-patch", help="Gera e valida o patch delta PT-BR (dos-ptbr.dospatch)")

    p_bld = sub.add_parser("build", help="Compila nds_runner.exe (com icone), runtime/ e CastlevaniaDawnOfSorrow.exe")
    p_bld.add_argument("--jobs", type=int, default=jobs_default)
    p_bld.add_argument("--clean", action="store_true")
    p_bld.add_argument("--software-3d", action="store_true")

    sub.add_parser("launcher", help="Compila apenas CastlevaniaDawnOfSorrow.exe com icone embutido")

    p_smk = sub.add_parser("smoke", help="Executa boot headless via debug server e captura PNG")
    p_smk.add_argument("--frames", type=int, default=600)
    p_smk.add_argument("--checkpoint-every", type=int, default=150)
    p_smk.add_argument("--port", type=int, default=19962)

    sub.add_parser("analyze", help="Extrai e analisa ROM com ds-decomp (dsd)")
    sub.add_parser("play", help="Abre o jogo interativo")

    p_all = sub.add_parser("all", help="Executa prepare -> recompiler -> banks -> build -> smoke")
    p_all.add_argument("--jobs", type=int, default=jobs_default)
    p_all.add_argument("--clean", action="store_true")
    p_all.add_argument("--software-3d", action="store_true")
    p_all.add_argument("--frames", type=int, default=600)
    p_all.add_argument("--checkpoint-every", type=int, default=150)
    p_all.add_argument("--port", type=int, default=19962)
    return ap


def main() -> int:
    ap = build_parser()
    args = ap.parse_args()
    handlers = {
        "status": cmd_status,
        "prepare": cmd_prepare,
        "recompiler": cmd_recompiler,
        "banks": cmd_banks,
        "promote": cmd_promote,
        "ptbr-patch": cmd_ptbr_patch,
        "build": cmd_build,
        "launcher": cmd_launcher,
        "smoke": cmd_smoke,
        "analyze": cmd_analyze,
        "play": cmd_play,
        "all": cmd_all,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())

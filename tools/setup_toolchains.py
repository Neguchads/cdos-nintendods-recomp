#!/usr/bin/env python3
"""Baixa e valida o toolchain portável Windows em toolchains/."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import tarfile
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLCHAINS_DIR = ROOT / "toolchains"
DOWNLOADS_DIR = TOOLCHAINS_DIR / "_downloads"


@dataclass(frozen=True)
class ToolComponent:
    name: str
    version: str
    url: str
    sha256: str | None
    archive: str
    kind: str  # "zip" | "tar.gz" | "exe"
    target_rel: str
    probe_rel: str
    strip_top: bool = True


COMPONENTS: tuple[ToolComponent, ...] = (
    ToolComponent(
        name="llvm-mingw",
        version="20261020",
        url=(
            "https://github.com/mstorsjo/llvm-mingw/releases/download/"
            "20261020/llvm-mingw-20261020-ucrt-x86_64.zip"
        ),
        sha256="fd5462b7f5d93b2ff981fcd3f9c7e427e47f3203c64ea91c27bcc444eebd74cd",
        archive="llvm-mingw-20261020-ucrt-x86_64.zip",
        kind="zip",
        target_rel="llvm-mingw",
        probe_rel="bin/x86_64-w64-mingw32-clang.exe",
        strip_top=True,
    ),
    ToolComponent(
        name="sdl3",
        version="3.4.18",
        url=(
            "https://github.com/libsdl-org/SDL/releases/download/"
            "release-3.4.18/SDL3-devel-3.4.18-mingw.tar.gz"
        ),
        sha256="049b9dd711e3fb3f8d84feb998dfec54a75e17cf539c4a80ff4d058d839771cf",
        archive="SDL3-devel-3.4.18-mingw.tar.gz",
        kind="tar.gz",
        target_rel="sdl3",
        probe_rel="x86_64-w64-mingw32/lib/cmake/SDL3/SDL3Config.cmake",
        strip_top=True,
    ),
    ToolComponent(
        name="dsd",
        version="0.12.1",
        url=(
            "https://github.com/AetiasHax/ds-decomp/releases/download/"
            "v0.12.1/dsd-windows-x86_64.exe"
        ),
        sha256=None,
        archive="dsd-windows-x86_64.exe",
        kind="exe",
        target_rel="dsd",
        probe_rel="dsd.exe",
        strip_top=False,
    ),
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download_file(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    req = urllib.request.Request(url, headers={"User-Agent": "castlevania-dos-recomp-setup"})
    with urllib.request.urlopen(req, timeout=120) as resp, tmp.open("wb") as out:
        total = int(resp.headers.get("Content-Length") or 0)
        done = 0
        last_pct = -1
        while True:
            chunk = resp.read(1 << 16)
            if not chunk:
                break
            out.write(chunk)
            done += len(chunk)
            if total > 0:
                pct = int(done * 100 / total)
                if pct >= last_pct + 10 or pct == 100:
                    print(f"    {pct}% ({done // (1024 * 1024)}/{total // (1024 * 1024)} MiB)", flush=True)
                    last_pct = pct
    tmp.replace(dest)


def safe_rel_parts(member_name: str, strip_top: bool) -> Path | None:
    parts = [p for p in Path(member_name).parts if p not in ("", ".")]
    if strip_top:
        parts = parts[1:]
    if not parts:
        return None
    if any(p == ".." or p.endswith(":") for p in parts):
        raise ValueError(f"unsafe archive path: {member_name!r}")
    return Path(*parts)


def extract_zip(archive: Path, target_dir: Path, strip_top: bool) -> None:
    resolved_root = target_dir.resolve()
    with zipfile.ZipFile(archive, "r") as zf:
        for info in zf.infolist():
            rel = safe_rel_parts(info.filename, strip_top)
            if rel is None:
                continue
            out_path = (resolved_root / rel).resolve()
            if not out_path.is_relative_to(resolved_root):
                raise ValueError(f"zip path escape: {info.filename!r}")
            if info.is_dir():
                out_path.mkdir(parents=True, exist_ok=True)
                continue
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info, "r") as src, out_path.open("wb") as dst:
                shutil.copyfileobj(src, dst)


def extract_targz(archive: Path, target_dir: Path, strip_top: bool) -> None:
    resolved_root = target_dir.resolve()
    with tarfile.open(archive, "r:gz") as tf:
        for member in tf.getmembers():
            rel = safe_rel_parts(member.name, strip_top)
            if rel is None:
                continue
            out_path = (resolved_root / rel).resolve()
            if not out_path.is_relative_to(resolved_root):
                raise ValueError(f"tar path escape: {member.name!r}")
            if member.isdir():
                out_path.mkdir(parents=True, exist_ok=True)
            elif member.issym() or member.islnk():
                # No Windows, symlinks em tarballs MinGW são geralmente duplicatas ou dispensáveis;
                # resolve link alvo dentro do mesmo diretório quando possível.
                if member.issym():
                    link_target = (out_path.parent / member.linkname).resolve()
                    if link_target.is_relative_to(resolved_root) and link_target.exists():
                        out_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(link_target, out_path)
                continue
            elif member.isfile():
                src = tf.extractfile(member)
                if src is None:
                    continue
                out_path.parent.mkdir(parents=True, exist_ok=True)
                with src, out_path.open("wb") as dst:
                    shutil.copyfileobj(src, dst)


def install_component(comp: ToolComponent) -> dict[str, str]:
    target_dir = TOOLCHAINS_DIR / comp.target_rel
    probe = target_dir / comp.probe_rel
    manifest_path = target_dir / ".installed.json"

    if probe.is_file() and manifest_path.is_file():
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        if data.get("version") == comp.version:
            print(f"[ok] {comp.name} {comp.version} já presente em {target_dir}")
            return data

    archive_path = DOWNLOADS_DIR / comp.archive
    if archive_path.is_file() and comp.sha256:
        actual = sha256_file(archive_path)
        if actual != comp.sha256:
            print(f"[warn] {comp.archive} SHA-256 inválido ({actual}); baixando novamente")
            archive_path.unlink()

    if not archive_path.is_file():
        print(f"[download] {comp.name} {comp.version} <- {comp.url}")
        download_file(comp.url, archive_path)

    actual_sha = sha256_file(archive_path)
    if comp.sha256 and actual_sha != comp.sha256:
        raise RuntimeError(
            f"SHA-256 mismatch para {comp.archive}: obtido {actual_sha}, esperado {comp.sha256}"
        )

    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    print(f"[extract] {comp.name} -> {target_dir}")
    if comp.kind == "zip":
        extract_zip(archive_path, target_dir, comp.strip_top)
    elif comp.kind == "tar.gz":
        extract_targz(archive_path, target_dir, comp.strip_top)
    elif comp.kind == "exe":
        shutil.copy2(archive_path, target_dir / comp.probe_rel)
    else:
        raise ValueError(f"tipo desconhecido: {comp.kind}")

    if not probe.is_file():
        raise RuntimeError(f"probe ausente após extração: {probe}")

    record = {
        "name": comp.name,
        "version": comp.version,
        "url": comp.url,
        "archive_sha256": actual_sha,
        "probe": str(probe),
    }
    manifest_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"[done] {comp.name} {comp.version} (sha256={actual_sha})")
    return record


def main() -> int:
    TOOLCHAINS_DIR.mkdir(parents=True, exist_ok=True)
    records = {}
    for comp in COMPONENTS:
        records[comp.name] = install_component(comp)
    summary_path = TOOLCHAINS_DIR / "manifest.json"
    summary_path.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(f"Manifesto gravado em {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

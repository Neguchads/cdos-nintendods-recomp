#!/usr/bin/env python3
"""Validate Windows distribution archive, reject unexpected entries, hash every payload."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import zipfile

REQUIRED = {"CastlevaniaDawnOfSorrow.exe", "runtime/nds_runner.exe", "runtime/SDL3.dll",
            "runtime/libc++.dll", "runtime/libunwind.dll", "game.toml", "recomplauncher.json",
            "mods/ptbr/dos-ptbr.dospatch", "SHA256SUMS.txt"}
EXACT = REQUIRED | {
    "README.md",
    "play.bat",
    "LICENSE",
    "mods/catalog.json",
    "mods/registry.json",
    "mods/music/README.md",
    "mods/music/configurar_musica.py",
    "mods/music/Configurar_Musica.bat",
}


def allowed(name):
    p = PurePosixPath(name)
    return (name in EXACT or
            (p.parent.as_posix() == "docs" and p.suffix == ".md") or
            (p.parent.as_posix() == "assets/recomplauncher" and p.suffix in {".png",".jpg",".ico",".json"}) or
            (len(p.parts) == 3 and p.parts[0] == "mods" and p.suffix == ".dospatch"))


def validate(path):
    with zipfile.ZipFile(path) as z:
        entries = z.infolist()
        names = set()
        folded = set()
        if len(entries) > 1000 or sum(i.file_size for i in entries) > 1024**3:
            raise ValueError("archive exceeds limits")
        for info in entries:
            n = info.filename
            p = PurePosixPath(n)
            if (p.is_absolute() or "\\" in n or ":" in n or
                    any(x in ("", ".", "..") for x in n.split("/")) or
                    n.casefold() in folded or stat.S_ISLNK(info.external_attr >> 16)
                    or info.flag_bits & 1 or not allowed(n)):
                raise ValueError(f"unsafe/unexpected archive entry: {n}")
            folded.add(n.casefold())
            names.add(n)
        if not REQUIRED <= names:
            raise ValueError(f"missing files: {sorted(REQUIRED-names)}")
        if z.testzip() is not None:
            raise ValueError("ZIP CRC failure")
        manifest = json.loads(z.read("recomplauncher.json"))
        if manifest.get("repo") != "Neguchads/cdos-nintendods-recomp" or manifest.get("format") != 1:
            raise ValueError("invalid manifest identity")
        args = manifest["start"]["args"]
        if args[0] != "{data}/run/bios" or args[args.index("--config")+1] != "{install}/game.toml":
            raise ValueError("invalid launcher startup paths")
        for value in args:
            if value.startswith("{install}/") and not value.endswith("opening.mp4"):
                if value[len("{install}/"):] not in names:
                    raise ValueError(f"missing launcher dependency: {value}")
        checks = {}
        for line in z.read("SHA256SUMS.txt").decode().splitlines():
            digest, name = line.split("  ", 1)
            if name in checks or not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise ValueError("invalid checksum entry")
            checks[name] = digest
        if set(checks) != names-{"SHA256SUMS.txt"}:
            raise ValueError("checksum coverage mismatch")
        for name, digest in checks.items():
            with z.open(name) as f:
                if hashlib.file_digest(f, "sha256").hexdigest() != digest:
                    raise ValueError(f"checksum mismatch: {name}")
            if name.endswith((".exe", ".dll")):
                with z.open(name) as f:
                    if f.read(2) != b"MZ":
                        raise ValueError(f"invalid Windows binary: {name}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("archive", type=Path)
    a = p.parse_args()
    validate(a.archive)
    with a.archive.open("rb") as f:
        digest = hashlib.file_digest(f, "sha256").hexdigest()
    a.archive.with_name(a.archive.name+".sha256").write_text(f"{digest}  {a.archive.name}\n", encoding="ascii")
    print(f"Validated {a.archive.name}: {digest}")


if __name__ == "__main__":
    main()

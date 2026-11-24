"""Create a GitHub draft only, after validating a locally built archive."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from rbs_artifact import validate

ROOT = Path(__file__).resolve().parent.parent
REPO = "Neguchads/cdos-nintendods-recomp"


def out(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("archive", type=Path)
    p.add_argument("--confirm-draft", action="store_true", required=True)
    a = p.parse_args()
    archive = a.archive.resolve()
    validate(archive)
    receipt = json.loads(archive.with_name(archive.name+".build.json").read_text())
    tag, commit = receipt["version"], receipt["commit"]
    if not re.fullmatch(r"v\d+\.\d+\.\d+(?:-(?:test|beta|rc)\.\d+)?", tag):
        p.error("invalid version")
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        p.error("invalid commit")
    if receipt["profile"] != "release" or receipt["archive"] != archive.name:
        p.error("invalid receipt")
    if archive.name != f"CastlevaniaDawnOfSorrowRecomp-{tag}-Windows-x64.zip":
        p.error("incorrect asset name")
    with archive.open("rb") as f:
        actual = hashlib.file_digest(f, "sha256").hexdigest()
    if actual != receipt["sha256"]:
        p.error("archive differs from build receipt")
    if commit != out("git","rev-parse","HEAD") or out("git","status","--porcelain","--untracked-files=no"):
        p.error("check out the clean source commit used for this build")
    # Explicitly fetch reviewed source from the official public repository.
    subprocess.run(["git","fetch","https://github.com/"+REPO+".git","main"],cwd=ROOT,check=True)
    main_commit = out("git","rev-parse","FETCH_HEAD")
    beta = "-" in tag
    if not beta:
        if commit != main_commit:
            p.error("stable draft requires current official main")
        if json.loads((ROOT/".release-please-manifest.json").read_text())["."] != tag[1:]:
            p.error("stable version must match the merged Release Please manifest")
    # GitHub verifies the target SHA when publishing the draft.
    checksum = archive.with_name(archive.name+".sha256")
    checksum.write_text(f"{actual}  {archive.name}\n",encoding="ascii")
    existing = subprocess.run(["gh","release","view",tag,"--repo",REPO],capture_output=True,text=True)
    if existing.returncode == 0:
        p.error("release already exists; never overwrite an existing release")
    cmd = ["gh","release","create",tag,str(archive),str(checksum),
           "--repo",REPO,"--target",commit,"--draft","--title",tag,"--generate-notes"]
    if beta:
        cmd += ["--prerelease"]
    subprocess.run(cmd,cwd=ROOT,check=True)
    print("Draft uploaded. Inspect assets and release notes; publish manually on GitHub.")


if __name__ == "__main__":
    main()

"""Create a GitHub draft only, after validating a locally built archive."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from rbs_artifact import validate

ROOT = Path(__file__).resolve().parent.parent
REPO = "Neguchads/cdos-nintendods-recomp"
AUTOVERIFY_CORE_SHA = "c6037185830f24770f856d4cd69791c686095bc5"


def out(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def verify_final_archive(core_checkout, archive, actual):
    core = core_checkout.resolve(strict=True)
    script = core / "navi_core/autoverify.py"
    revision = subprocess.check_output(["git", "-C", str(core), "rev-parse", "HEAD"], text=True).strip()
    if revision != AUTOVERIFY_CORE_SHA or not script.is_file() or script.is_symlink():
        raise ValueError("AutoVerify requires the reviewed pinned Core revision")
    committed = subprocess.check_output(["git", "-C", str(core), "show", revision + ":navi_core/autoverify.py"])
    if script.read_bytes().replace(b"\r\n", b"\n") != committed.replace(b"\r\n", b"\n"):
        raise ValueError("AutoVerify script differs from reviewed Git contents")
    result = subprocess.run([sys.executable, "-I", str(script), str(archive),
                             "--expected-sha256", actual, "--lookup-public-noncommercial"],
                            capture_output=True, text=True, timeout=120, check=False)
    try:
        report = json.loads(result.stdout)
    except ValueError:
        raise ValueError("AutoVerify did not produce a valid report") from None
    if not isinstance(report, dict):
        raise ValueError("AutoVerify did not produce an object report")
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=archive.parent,
                                    prefix=archive.name + ".autoverify-", suffix=".json", delete=False) as log:
        json.dump(report, log, sort_keys=True)
        print("AutoVerify report:", log.name)
    if result.returncode != 0 or report.get("sha256") != actual or report.get("status") != "no-detections-reported":
        raise ValueError("AutoVerify requires review; draft was not created")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("archive", type=Path)
    p.add_argument("--confirm-draft", action="store_true", required=True)
    p.add_argument("--autoverify-core", type=Path, help="Reviewed NAVI Core checkout for optional final stable package lookup")
    p.add_argument("--confirm-public-noncommercial", action="store_true", help="Authorize public non-commercial hash lookup only")
    a = p.parse_args()
    if bool(a.autoverify_core) != a.confirm_public_noncommercial:
        p.error("Both AutoVerify opt-in flags are required together")
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
    if a.autoverify_core:
        if beta:
            p.error("AutoVerify is restricted to final stable delivery packages")
        try:
            verify_final_archive(a.autoverify_core, archive, actual)
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            p.error("AutoVerify failed; draft was not created (" + type(exc).__name__ + ")")
    cmd = ["gh","release","create",tag,str(archive),str(checksum),
           "--repo",REPO,"--target",commit,"--draft","--title",tag,"--generate-notes"]
    if beta:
        cmd += ["--prerelease"]
    subprocess.run(cmd,cwd=ROOT,check=True)
    print("Draft uploaded. Inspect assets and release notes; publish manually on GitHub.")


if __name__ == "__main__":
    main()

"""Local-only content-addressed phase cache; no network or cloud upload."""
import hashlib
import json
from pathlib import Path


def snapshot(paths):
    result = {}
    for path in sorted(set(map(Path, paths)), key=str):
        if path.is_symlink():
            raise ValueError(f"Unexpected symlink: {path}")
        if path.is_file():
            with path.open("rb") as f:
                result[str(path)] = hashlib.file_digest(f, "sha256").hexdigest()
        elif path.is_dir():
            result[str(path)] = snapshot(p for p in path.rglob("*") if p.is_file())
        else:
            result[str(path)] = None
    return result


def key(paths, extra=None):
    return hashlib.sha256(json.dumps([snapshot(paths), extra], sort_keys=True).encode()).hexdigest()


class PhaseCache:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def run(self, name, fingerprint, outputs, action, force=False):
        stamp = self.directory / (name + ".json")
        outputs = list(map(Path, outputs))
        try:
            previous = json.loads(stamp.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            previous = None
        if not force and previous and all(p.exists() for p in outputs):
            if previous == {"key": fingerprint, "outputs": snapshot(outputs)}:
                print(f"[RBS] HIT {name}", flush=True)
                return False
        print(f"[RBS] MISS {name}", flush=True)
        stamp.unlink(missing_ok=True)
        action()
        if not all(p.exists() for p in outputs):
            raise RuntimeError(f"{name}: missing expected output")
        temp = stamp.with_suffix(".tmp")
        temp.write_text(json.dumps({"key": fingerprint, "outputs": snapshot(outputs)}), encoding="utf-8")
        temp.replace(stamp)
        return True

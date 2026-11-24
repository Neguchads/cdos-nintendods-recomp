"""Hypothesis fuzzing of paths, IDs and patch headers; no ROM bytes involved."""
from pathlib import Path
import re
from hypothesis import given, settings, strategies as st
from tools import mod_resolver as mod
from tools import vcdiff_ips as patch

CI = settings(max_examples=180, deadline=None, derandomize=True)

@CI
@given(st.text(max_size=128))
def fuzz_safe_id(value):
    result = mod.sanitize_safe_id(value)
    assert not result or re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,47}", result)
    if result:
        assert mod.sanitize_safe_id(result) == result

@CI
@given(st.text(max_size=128))
def fuzz_randomizer_seed(value):
    result = mod.sanitize_seed(value)
    assert len(result) <= 32
    assert re.fullmatch(r"[A-Za-z0-9_-]*", result)

@CI
@given(st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126), max_size=64))
def fuzz_path_containment(part):
    root = Path("/tmp/cdos-stage3-synthetic").resolve()
    try:
        result = mod.safe_join_under(root, part)
    except ValueError:
        return
    assert result == root or root in result.parents, (part, result)

@CI
@given(st.binary(max_size=128))
def fuzz_vcdiff_header(data):
    try:
        info = patch.inspect_vcdiff(patch.VCDIFF_MAGIC + b"\x00" + data)
    except ValueError:
        return
    assert info.window_count >= 0
    assert info.target_size >= 0

if __name__ == "__main__":
    fuzz_safe_id()
    fuzz_randomizer_seed()
    fuzz_path_containment()
    fuzz_vcdiff_header()
    print("PASS: CDOS synthetic Hypothesis properties")

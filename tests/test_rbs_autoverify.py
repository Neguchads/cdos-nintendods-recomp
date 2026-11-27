import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import rbs_publish


class FinalArchiveAutoVerifyTests(unittest.TestCase):
    def test_pinned_archive_verification(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            script = root / "navi_core" / "autoverify.py"
            script.parent.mkdir()
            script.write_bytes(b"# reviewed\n")
            archive = root / "final.zip"
            archive.write_bytes(b"sample")
            digest = "a" * 64
            good = {"sha256": digest, "status": "no-detections-reported"}
            for code, report, succeeds in [
                (0, good, True),
                (2, {"sha256": digest, "status": "unknown-hash"}, False),
                (0, {"sha256": "b" * 64, "status": "no-detections-reported"}, False),
                (0, [], False),
            ]:
                with self.subTest(code=code, report=report):
                    with patch.object(rbs_publish.subprocess, "check_output",
                                      side_effect=[rbs_publish.AUTOVERIFY_CORE_SHA, b"# reviewed\n"]), \
                         patch.object(rbs_publish.subprocess, "run",
                                      return_value=subprocess.CompletedProcess([], code, json.dumps(report), "")) as run:
                        if succeeds:
                            rbs_publish.verify_final_archive(root, archive, digest)
                        else:
                            with self.assertRaises(ValueError):
                                rbs_publish.verify_final_archive(root, archive, digest)
                        self.assertEqual(run.call_args.args[0][-3:], ["--expected-sha256", digest, "--lookup-public-noncommercial"])
            with patch.object(rbs_publish.subprocess, "check_output", return_value="b" * 40), \
                 patch.object(rbs_publish.subprocess, "run") as run:
                with self.assertRaises(ValueError):
                    rbs_publish.verify_final_archive(root, archive, digest)
                run.assert_not_called()
            with patch.object(rbs_publish.subprocess, "check_output",
                              side_effect=[rbs_publish.AUTOVERIFY_CORE_SHA, b"# different\n"]), \
                 patch.object(rbs_publish.subprocess, "run") as run:
                with self.assertRaises(ValueError):
                    rbs_publish.verify_final_archive(root, archive, digest)
                run.assert_not_called()


if __name__ == "__main__":
    unittest.main()

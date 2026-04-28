from pathlib import Path

from sed.transpiler.transpile_to_python import transpile
import subprocess
import sys
import os
import filecmp
from matplotlib.testing.compare import compare_images

IMAGE_EXTS = {".png", ".pdf", ".svg", ".jpg", ".jpeg"}
IMAGE_TOL = 2.0  # RMS pixel difference tolerance
root_dir = Path(__file__).resolve().parents[1]

def assert_dirs_equal(actual: Path, expected: Path):
    cmp = filecmp.dircmp(actual, expected)
    if cmp.left_only:
        assert False, f"Unexpected file(s) in {actual}: {cmp.left_only}"
    if cmp.right_only:
        assert False, f"Unexpected file(s) in {actual}: {cmp.right_only}"

    image_files = []
    other_files = []
    for f in cmp.common_files:
        if Path(f).suffix.lower() in IMAGE_EXTS:
            image_files.append(f)
        else:
            other_files.append(f)

    # Non-image files: byte-exact
    _, mismatch, errors = filecmp.cmpfiles(actual, expected, other_files, shallow=False)
    if mismatch:
        diffs = []
        for name in mismatch:
            actual_path = Path(actual) / name
            expected_path = Path(expected) / name
            actual_lines = actual_path.read_text().splitlines(keepends=True)
            expected_lines = expected_path.read_text().splitlines(keepends=True)
            diff = difflib.unified_diff(
                expected_lines,
                actual_lines,
                fromfile=str(expected_path),
                tofile=str(actual_path),
            )
            diffs.append("".join(diff))
        assert False, f"These files differ: {mismatch}\n\n" + "\n".join(diffs)
    assert not errors,   f"These files are unreadable: {errors}"

    # Image files: tolerance-based
    for name in image_files:
        result = compare_images(
            str(expected / name), str(actual / name), tol=IMAGE_TOL,
        )
        assert result is None, f"image diff in {name}: {result}"

def python_transpile_test(tmp_path, testdir, filename, expected, context={}):
    pyout = transpile(testdir, filename, context)
    script = tmp_path / "exported_python.py"
    script.write_text(pyout, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True, text=True, timeout=500, cwd=tmp_path,
        env={**os.environ, "MPLBACKEND": "Agg"},
    )
    assert result.returncode == 0, result.stderr
    assert_dirs_equal(expected, tmp_path)

# Examples:
def test_python_transpile_ex_1(tmp_path):
    testdir = root_dir / "examples" / "one"
    expected = root_dir / "tests" / "expected test results" / "examples" / "one"
    context = {"tasks": {"sim2": "Copasi"}}
    python_transpile_test(tmp_path, testdir, "sed.json", expected, context)


def test_python_transpile_ex_2(tmp_path):
    testdir = root_dir / "examples" / "two"
    expected = root_dir / "tests" / "expected test results" / "examples" / "two"
    # python_transpile_test(tmp_path, testdir, "sed.json", expected)


# Unit tests

def test_py_constant_value(tmp_path):
    testdir = root_dir / "tests" / "unit test files"
    filename = "constant_value.json"
    expected = root_dir / "tests" / "expected test results" / "unit tests" / "constant_value"
    python_transpile_test(tmp_path, testdir, filename, expected)

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
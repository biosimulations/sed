from pathlib import Path

from sed.transpiler.transpile_to_python import transpile
import subprocess
import sys
import os
import filecmp
import difflib
import tempfile
from matplotlib.testing.compare import compare_images

IMAGE_EXTS = {".png", ".pdf", ".svg", ".jpg", ".jpeg"}
IMAGE_TOL = 2.0  # RMS pixel difference tolerance
root_dir = Path(__file__).resolve().parents[1]

def filter_directories(input_lines, filenames):
    kept = []
    for line in input_lines:
        keep = True
        for filename in filenames:
            if filename in line:
                keep = False;
                continue
        if keep:
            kept.append(line)
    return kept

def assert_dirs_equal(actual: Path, expected: Path, filenames):
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
        for filename in mismatch:
            actual_path = Path(actual) / filename
            expected_path = Path(expected) / filename
            actual_lines = actual_path.read_text().splitlines(keepends=True)
            expected_lines = expected_path.read_text().splitlines(keepends=True)
            actual_lines = filter_directories(actual_lines, filenames)
            expected_lines = filter_directories(expected_lines, filenames)
            diff = list(difflib.unified_diff(
                expected_lines,
                actual_lines,
                fromfile=str(expected_path),
                tofile=str(actual_path),
            ))
            if len(diff):
                assert False, f"These files differ: {filename}\n\n" + "\n".join(diff)
    assert not errors,   f"These files are unreadable: {errors}"

    # Image files: tolerance-based
    for name in image_files:
        result = compare_images(
            str(expected / name), str(actual / name), tol=IMAGE_TOL,
        )
        assert result is None, f"image diff in {name}: {result}"

def python_transpile_test(tmp_path, testdir, filename, expected, filenames=[], context={}):
    pyout = transpile(testdir, filename, context)
    script = tmp_path / "exported_python.py"
    script.write_text(pyout, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True, text=True, timeout=500, cwd=tmp_path,
        env={**os.environ, "MPLBACKEND": "Agg"},
    )
    assert result.returncode == 0, result.stderr
    assert_dirs_equal(expected, tmp_path, filenames)

# Examples:
def test_python_transpile_ex_1(tmp_path):
    testdir = root_dir / "examples" / "one"
    expected = root_dir / "tests" / "expected test results" / "examples" / "one"
    filenames = ["example1.xml", "experimental_data.csv"]
    context = {"tasks": {"sim2": "Copasi"}}
    python_transpile_test(tmp_path, testdir, "sed.json", expected, filenames, context)


def test_python_transpile_ex_2(tmp_path):
    testdir = root_dir / "examples" / "two"
    expected = root_dir / "tests" / "expected test results" / "examples" / "two"
    # python_transpile_test(tmp_path, testdir, "sed.json", expected)


# Unit tests

def unittest(tmp_path, testname, filenames=[]):
    unittest_dir = root_dir / "tests" / "unit test files"
    expected_dir = root_dir / "tests" / "expected test results" / "unit tests"
    filename = testname + ".json"
    expected = expected_dir / testname
    python_transpile_test(tmp_path, unittest_dir, filename, expected, filenames)

def test_py_empty_doc(tmp_path):
    unittest(tmp_path, "SEDDocument_empty")

def test_py_constant_value(tmp_path):
    unittest(tmp_path, "constant_value")

def test_py_constant_list(tmp_path):
    unittest(tmp_path, "constant_list")

def test_py_constant_dict_list(tmp_path):
    unittest(tmp_path, "constant_dict_list")

def test_py_constant_dict_num(tmp_path):
    unittest(tmp_path, "constant_dict_num")

def test_py_constant_matrix(tmp_path):
    unittest(tmp_path, "constant_matrix")

def test_py_model_import(tmp_path):
    unittest(tmp_path, "model_import", ["three_species_chain.xml"])

def test_py_data_import(tmp_path):
    unittest(tmp_path, "data_import", ["experimental_data.csv"])

if __name__ == "__main__":
    # import pytest
    # pytest.main([__file__, "-v"])
    tmp_path = Path(tempfile.mkdtemp())
    print(f"tmp_path = {tmp_path}")   # so you can inspect afterward
    test_py_data_import(tmp_path)

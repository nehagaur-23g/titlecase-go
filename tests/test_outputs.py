"""Weighted Harbor verifier for the titlecase Go port."""

import atexit
import json
import subprocess
import tempfile
from pathlib import Path

import pytest

REPO = Path("/logs/artifacts/repo")
HIDDEN_INPUTS = Path("/tests/data/hidden_inputs.jsonl")
HIDDEN_EXPECTED = Path("/tests/data/hidden_expected.jsonl")
REWARD_PATH = Path("/logs/verifier/reward.json")
CASE_COUNT = 2000
COMMAND_TIMEOUT_SEC = 180

scores = {"build": 0.0, "no_python": 0.0, "behavior": 0.0}
_build_result = None


def _write_reward():
    """Write the weighted reward. Safe to call more than once."""
    REWARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    reward = (scores["build"] + scores["no_python"] + 4 * scores["behavior"]) / 6
    REWARD_PATH.write_text(
        json.dumps({"reward": reward}) + "\n",
        encoding="utf-8",
    )


# Process exit still writes the file if a test failure skips fixture teardown.
atexit.register(_write_reward)


@pytest.fixture(scope="session", autouse=True)
def _reward_file():
    """Write reward.json after every test, including failures."""
    yield
    _write_reward()


def _run_go_build():
    """Return whether `go build ./...` exits 0. Used by both scored checks."""
    global _build_result
    if _build_result is not None:
        return _build_result
    try:
        proc = subprocess.run(
            ["go", "build", "./..."],
            cwd=REPO,
            capture_output=True,
            timeout=COMMAND_TIMEOUT_SEC,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        _build_result = False
        (REWARD_PATH.parent / "go-build-error.txt").write_text(
            str(exc),
            encoding="utf-8",
        )
        return _build_result

    (REWARD_PATH.parent / "go-build-error.txt").write_text(
        proc.stderr.decode("utf-8", errors="replace")
        + "\n"
        + proc.stdout.decode("utf-8", errors="replace"),
        encoding="utf-8",
    )

    _build_result = proc.returncode == 0
    return _build_result


def _python_files():
    if not REPO.is_dir():
        return None
    return [path for path in REPO.rglob("*") if path.is_file() and path.name.endswith(".py")]


def _load_jsonl_strings(path):
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        raise ValueError("could not read hidden data") from None
    records = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            raise ValueError(f"hidden data line {line_number} is not valid JSON") from None
        if not isinstance(value, str):
            raise ValueError(f"hidden data line {line_number} is not a JSON string")
        records.append(value)
    return records


def _built_binary(directory):
    binary = Path(directory) / "titlecase"
    if binary.is_file():
        return binary
    windows_binary = binary.with_suffix(".exe")
    if windows_binary.is_file():
        return windows_binary
    return None


def test_build():
    """go build ./... must succeed in /workspace/repo."""
    ok = _run_go_build()
    scores["build"] = 1.0 if ok else 0.0
    assert ok, "go build ./... failed; check go-build-error.txt in /logs/verifier"


def test_no_python():
    """Score 1 only when the build passes and no .py files remain."""
    build_ok = _run_go_build()
    py_files = _python_files()
    scores["no_python"] = 1.0 if build_ok and py_files == [] else 0.0
    if not build_ok:
        pytest.fail("go build ./... failed")
    if py_files is None:
        pytest.fail("/workspace/repo is missing")
    if py_files:
        pytest.fail(f"found {len(py_files)} .py file(s) under /workspace/repo")


def test_hidden_behavior():
    """Hidden titlecase outputs must match, without echoing the cases."""
    try:
        failure = _hidden_behavior_failure()
    except Exception:
        scores["behavior"] = 0.0
        pytest.fail("hidden behavior check failed")
    scores["behavior"] = 0.0 if failure else 1.0
    if failure:
        pytest.fail(failure)


def _hidden_behavior_failure():
    try:
        inputs = _load_jsonl_strings(HIDDEN_INPUTS)
        expected = _load_jsonl_strings(HIDDEN_EXPECTED)
    except ValueError as exc:
        return str(exc)

    if len(inputs) != CASE_COUNT or len(expected) != CASE_COUNT:
        return f"expected {CASE_COUNT} hidden cases"

    payload = ("\n".join(inputs) + "\n").encode("utf-8")
    try:
        with tempfile.TemporaryDirectory(prefix="titlecase-") as tmp:
            binary_path = str(Path(tmp) / "titlecase")
            try:
                build = subprocess.run(
                    ["go", "build", "-o", binary_path, "."],
                    cwd=REPO,
                    capture_output=True,
                    timeout=COMMAND_TIMEOUT_SEC,
                )
            except subprocess.TimeoutExpired:
                return "go build -o timed out"
            except OSError:
                return "could not build the Go program"
            if build.returncode != 0:
                return f"go build -o exited with status {build.returncode}"

            binary = _built_binary(tmp)
            if binary is None:
                return "go build -o did not produce a binary"

            try:
                proc = subprocess.run(
                    [str(binary)],
                    cwd=REPO,
                    input=payload,
                    capture_output=True,
                    timeout=COMMAND_TIMEOUT_SEC,
                )
            except subprocess.TimeoutExpired:
                return "Go program timed out"
            except OSError:
                return "could not run the Go program"
    except OSError:
        return "could not create a temporary build directory"

    if proc.returncode != 0:
        return f"Go program exited with status {proc.returncode}"

    try:
        stdout = proc.stdout.decode("utf-8")
    except UnicodeError:
        return "program output was not valid UTF-8"

    got = stdout.splitlines()
    if len(got) != CASE_COUNT:
        return f"expected {CASE_COUNT} output lines, got {len(got)}"

    mismatches = sum(1 for actual, wanted in zip(got, expected) if actual != wanted)
    if mismatches:
        return f"{mismatches} of {CASE_COUNT} output lines did not match"
    return None

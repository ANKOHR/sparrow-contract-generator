import json
import time
from sparrow_contract_generator.cli import main

def test_run_completes_on_fixture(dataset, tmp_path, capsys):
    path, _ = dataset
    start = time.perf_counter()
    assert main(["run", "--input", str(path), "--state", str(tmp_path / "state.json")]) == 0
    assert main(["report", "--state", str(tmp_path / "state.json")]) == 0
    assert time.perf_counter() - start < 5

def test_empty_input_renders_without_traceback(tmp_path, capsys):
    folder = tmp_path / "empty"
    folder.mkdir()
    assert main(["run", "--input", str(folder), "--state", str(tmp_path / "state.json")]) == 0
    assert "Records: 0" in capsys.readouterr().out

def test_malformed_input_named_error(tmp_path, capsys):
    (tmp_path / "bad.jsonl").write_text("# test\n{bad}")
    assert main(["run", "--input", str(tmp_path)]) == 2
    error = capsys.readouterr().err
    assert "bad.jsonl: line 2" in error and "ParseOrSchemaError" in error

def test_determinism_byte_identical(dataset, tmp_path, capsys):
    path, _ = dataset
    state = tmp_path / "state.json"
    args = ["run", "--input", str(path), "--state", str(state)]
    assert main(args) == 0
    first = state.read_bytes()
    assert main(args) == 0
    assert state.read_bytes() == first

def test_cli_smoke_all_subcommands(tmp_path, capsys):
    path = tmp_path / "inputs"
    state = tmp_path / "state.json"
    assert main(["fixtures", "--out", str(path)]) == 0
    for cmd in ("run", "audit"):
        assert main([cmd, "--input", str(path), "--state", str(state)]) == 0
    assert main(["draft", "--input", str(path), "--id", "SOW-001"]) == 0
    for fmt in ("md", "json"):
        assert main(["report", "--state", str(state), "--format", fmt]) == 0

def test_write_failure_no_partial_file(dataset, tmp_path, capsys):
    path, _ = dataset
    state = tmp_path / "state.json"
    assert main(["run", "--input", str(path), "--state", str(state)]) == 0
    before = set(tmp_path.iterdir())
    assert main(["report", "--state", str(state), "--out", str(tmp_path)]) == 2
    assert set(tmp_path.iterdir()) == before
    assert "WriteError" in capsys.readouterr().err

def test_missing_input(tmp_path, capsys):
    assert main(["run", "--input", str(tmp_path / "absent")]) == 2
    assert "MissingInput" in capsys.readouterr().err

def test_schema_drift_names_field(dataset, capsys):
    path, rows = dataset
    rows[0]["unexpected"] = 1
    (path / "contracts.jsonl").write_text(json.dumps(rows[0]))
    assert main(["run", "--input", str(path)]) == 2
    assert "unexpected" in capsys.readouterr().err


def test_help_examples(capsys):
    import pytest
    for command in ("fixtures", "run", "report", "audit", "draft"):
        with pytest.raises(SystemExit) as exc:
            main([command, "--help"])
        assert exc.value.code == 0
        assert "Example:" in capsys.readouterr().out

def test_tiny_handwritten_input():
    from sparrow_contract_generator.cli import read_input
    from sparrow_contract_generator.core import compute
    result = compute(read_input("examples/tiny"), "2026-09-30")
    assert result["record_count"] == 5
    assert result["fee_totals_cents"] == {"GBP": 85000}
    assert result["issues"] == [{"id": "TINY-2", "code": "missing_acceptance"}, {"id": "TINY-3", "code": "unsigned"}]

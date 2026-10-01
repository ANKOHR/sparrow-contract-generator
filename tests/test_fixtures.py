import json
from sparrow_contract_generator.core import compute

def test_fixtures_labelled_synthetic(dataset):
    path, rows = dataset
    assert len(rows) == 200 and all(r["synthetic"] for r in rows)
    assert (path / "contracts.jsonl").read_text().startswith("# SYNTHETIC")
    assert json.loads((path / "expectations.json").read_text())["synthetic"] is True

def test_fixture_ground_truth_matches_hand_computed(dataset):
    path, rows = dataset
    expected = json.loads((path / "expectations.json").read_text())
    result = compute(rows, "2026-09-30")
    assert result["record_count"] == expected["record_count"] == 200
    assert result["fee_totals_cents"] == expected["fee_totals_cents"] == {"GBP": 2000000}
    assert len(result["issues"]) == expected["issue_count"] == 100
    for code, ids in expected["issue_ids"].items():
        assert [i["id"] for i in result["issues"] if i["code"] == code] == ids

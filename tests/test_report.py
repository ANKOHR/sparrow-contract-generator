import json
from sparrow_contract_generator.core import compute
from sparrow_contract_generator.report import render

def test_report_matches_ground_truth_exact(dataset):
    _, rows = dataset
    report = json.loads(render(compute(rows, "2026-09-30"), "json"))
    assert report["record_count"] == 200
    assert report["fee_totals_cents"] == {"GBP": 2000000}
    assert len(report["issues"]) == 100

def test_report_zero_false_positives(dataset):
    _, rows = dataset
    result = compute(rows, "2026-09-30")
    expected = {(f"SOW-{i:03d}", code) for code, stop in (("missing_acceptance", 40), ("unsigned", 50), ("future_start", 10)) for i in range(1, stop+1)}
    assert {(i["id"], i["code"]) for i in result["issues"]} == expected

def test_report_carries_provenance_banner(dataset):
    _, rows = dataset
    for fmt in ("md", "json"):
        assert "Provenance: 200 synthetic fixtures; 0 operator-declared real inputs" in render(compute(rows, "2026-09-30"), fmt)

def test_hypothetical_figures_labelled(dataset):
    _, rows = dataset
    for fmt in ("md", "json"):
        assert "Unmeasured: no baseline supplied" in render(compute(rows, "2026-09-30"), fmt)

def test_no_em_dashes_in_outputs(dataset):
    _, rows = dataset
    rows[0]["title"] = "One" + chr(0x2014) + "two"
    for fmt in ("md", "json"):
        assert chr(0x2014) not in render(compute(rows, "2026-09-30"), fmt)

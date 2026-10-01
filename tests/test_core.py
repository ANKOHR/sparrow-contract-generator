import pytest
from sparrow_contract_generator.core import compute, InputError

def test_rejects_adversarial_values(dataset):
    _, rows = dataset
    for key, value in (("fee_cents", -1), ("fee_cents", True), ("scope", "x" * 10001), ("currency", "gbp"), ("signed", 1), ("end_date", "2026-01-01"), ("start_date", "oops")):
        bad = dict(rows[0], **{key: value})
        with pytest.raises(InputError, match=key):
            compute([bad], "2026-09-30")
    with pytest.raises(InputError, match="duplicate"):
        compute([rows[0], rows[0]], "2026-09-30")

def test_handles_unicode_and_long_inputs(dataset):
    _, rows = dataset
    r = dict(rows[0], client="李 £ café", scope="C:\\Users\\Henry " + "é" * 9000)
    assert compute([r], "2026-09-30")["records"][0] == r

def test_corrupted_fixture_changes_figures(dataset):
    _, rows = dataset
    rows[0]["fee_cents"] += 123
    rows[0]["acceptance"] = "Approved checklist"
    result = compute(rows, "2026-09-30")
    assert result["fee_totals_cents"] == {"GBP": 2000123}
    assert len(result["issues"]) == 99

def test_mixed_currency_and_real_provenance(dataset):
    _, rows = dataset
    rows[0].update(currency="USD", synthetic=False)
    result = compute(rows[:2], "2026-09-30")
    assert result["fee_totals_cents"] == {"GBP": 10000, "USD": 10000}
    assert result["real_count"] == 1

"""Synthetic fixtures, no randomness. Expectations derived independently by arithmetic."""
import json
from pathlib import Path

def generate(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rows = [{"id": f"SOW-{i:03d}", "client": f"Example client {i}", "title": "Operations setup", "scope": "Deliver one documented workflow and a handover session.", "acceptance": "" if i <= 40 else "Client checks the workflow against the agreed checklist.", "fee_cents": 10000, "currency": "GBP", "start_date": "2026-10-01" if i <= 10 else "2026-09-01", "end_date": "2026-10-31", "signed": i > 50, "synthetic": True} for i in range(1, 201)]
    (out / "contracts.jsonl").write_text("# SYNTHETIC fixture data; no real clients\n" + "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows), encoding="utf-8")
    expected = {"synthetic": True, "label": "SYNTHETIC hand-computed expectations: 200 x 10000 cents; ranges 1..40, 1..50, 1..10", "record_count": 200, "fee_totals_cents": {"GBP": 2000000}, "issue_count": 100, "issue_ids": {"missing_acceptance": [f"SOW-{i:03d}" for i in range(1,41)], "unsigned": [f"SOW-{i:03d}" for i in range(1,51)], "future_start": [f"SOW-{i:03d}" for i in range(1,11)]}}
    (out / "expectations.json").write_text(json.dumps(expected, sort_keys=True, indent=2) + "\n", encoding="utf-8")

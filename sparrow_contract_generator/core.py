"""Pure input validation and SOW computation. No savings are estimated."""
from datetime import date
import re

class InputError(ValueError):
    """A named, actionable input failure."""

def clean_text(value, field, empty=False):
    if not isinstance(value, str) or (not empty and not value.strip()) or len(value) > 10000:
        raise InputError(f"SchemaError: {field}: expected text of 1 to 10000 characters")
    if any(ord(c) < 32 and c not in "\n\t" for c in value):
        raise InputError(f"SchemaError: {field}: control characters prohibited")
    return value.replace(chr(0x2014), "-")

def validate(record, as_of):
    fields = {"id", "client", "title", "scope", "acceptance", "fee_cents", "currency", "start_date", "end_date", "signed", "synthetic"}
    if not isinstance(record, dict):
        raise InputError("SchemaError: record: expected object")
    if set(record) != fields:
        raise InputError(f"SchemaError: fields: missing {sorted(fields-set(record))}, unknown {sorted(set(record)-fields)}")
    r = dict(record)
    for field in ("id", "client", "title", "scope", "acceptance"):
        r[field] = clean_text(r[field], field, empty=field == "acceptance")
    if type(r["fee_cents"]) is not int or not 0 <= r["fee_cents"] <= 10**12:
        raise InputError("SchemaError: fee_cents: expected integer between 0 and 1000000000000")
    if not isinstance(r["currency"], str) or not re.fullmatch("[A-Z]{3}", r["currency"]):
        raise InputError("SchemaError: currency: expected three uppercase letters")
    for field in ("signed", "synthetic"):
        if type(r[field]) is not bool:
            raise InputError(f"SchemaError: {field}: expected boolean")
    for field in ("start_date", "end_date"):
        try:
            if not isinstance(r[field], str) or date.fromisoformat(r[field]).isoformat() != r[field]:
                raise ValueError()
        except (ValueError, TypeError):
            raise InputError(f"SchemaError: {field}: expected ISO date") from None
    if r["end_date"] < r["start_date"]:
        raise InputError("SchemaError: end_date: precedes start_date")
    return r

def compute(records, as_of):
    try:
        if date.fromisoformat(as_of).isoformat() != as_of:
            raise ValueError()
    except (ValueError, TypeError):
        raise InputError("SchemaError: as_of: expected ISO date") from None
    rows, seen = [], set()
    for record in records:
        r = validate(record, as_of)
        if r["id"] in seen:
            raise InputError(f"SchemaError: id: duplicate {r['id']}")
        seen.add(r["id"])
        rows.append(r)
    rows.sort(key=lambda r: r["id"])
    issues, totals = [], {}
    for r in rows:
        totals[r["currency"]] = totals.get(r["currency"], 0) + r["fee_cents"]
        for code, condition in (("missing_acceptance", not r["acceptance"].strip()), ("unsigned", not r["signed"]), ("future_start", r["start_date"] > as_of)):
            if condition:
                issues.append({"id": r["id"], "code": code})
    return {"as_of": as_of, "record_count": len(rows), "synthetic_count": sum(r["synthetic"] for r in rows), "real_count": sum(not r["synthetic"] for r in rows), "fee_totals_cents": dict(sorted(totals.items())), "issues": issues, "records": rows, "savings": "Unmeasured: no baseline supplied; no time or money savings claimed."}

def statement(record):
    r = validate(record, "2026-09-30")
    label = "Synthetic fixture" if r["synthetic"] else "Real input declared by the operator (ownership not verified)"
    return f"# {r['title']}\n\nProvenance: {label}\n\nID: {r['id']}\nClient: {r['client']}\nDates: {r['start_date']} to {r['end_date']}\nFee: {r['fee_cents']} cents {r['currency']}\nSigned: {r['signed']}\n\nScope:\n{r['scope']}\n\nAcceptance:\n{r['acceptance'] or 'MISSING: agree acceptance before signing'}\n\nUnmeasured: no savings claimed. Draft SOW; no legal review performed.\n"

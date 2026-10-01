"""Deterministic report renderers."""
import json

def render(result, format="md"):
    banner = f"Provenance: {result['synthetic_count']} synthetic fixtures; {result['real_count']} operator-declared real inputs. Synthetic figures are illustrative. Real ownership and Henry authorship are not verified."
    if format == "json":
        return json.dumps({"provenance": banner, **result}, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    lines = ["# Sparrow Contract Generator report", "", banner, "", f"As of: {result['as_of']}", f"Records: {result['record_count']}", f"Issues: {len(result['issues'])}", "", "Contract fees from inputs (not revenue or savings):"]
    lines += [f"- {currency}: {amount} cents" for currency, amount in result["fee_totals_cents"].items()]
    lines += ["", result["savings"], "", "Issue evidence:"]
    lines += [f"- {i['id']}: {i['code']}" for i in result["issues"]]
    lines += ["", "Record evidence:"]
    lines += [f"- {r['id']}: {r['fee_cents']} cents {r['currency']}; synthetic={r['synthetic']}" for r in result["records"]]
    return "\n".join(lines) + "\n"

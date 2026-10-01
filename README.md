# Sparrow Contract Generator

A local Python CLI for lightweight statements of work. It drafts a scope, acceptance criteria, dates, and an explicit fee, and audits missing acceptance, unsigned contracts, and future starts. It is a draft generator, not a legal review service.

## Quickstart

Python 3.10 or newer and setuptools are required. Runtime uses only the standard library. Install using local tooling without network access:

```powershell
python -m pip install --no-deps --no-build-isolation -e .
scg fixtures --out demo
scg run --input demo
scg report --format md
python -m pytest -q
```

On Windows, if pip warns that the user Scripts directory is not on PATH, add that printed directory to your shell PATH, or use the module invocation below.

The chained demo is `scg fixtures --out demo && scg run --input demo && scg report --format md` in a shell supporting `&&`. Without installation, use `python -m sparrow_contract_generator.cli` in place of `scg`.

## Input reference

Input directories contain UTF-8 `.jsonl` files, one object per line. Blank lines and lines beginning with `#` are allowed. `expectations.json` is reserved fixture metadata and never used to compute results. Other formats are rejected with a named error. The explicitly selected results file is excluded if inside the input directory. No subdirectories are read.

Every object must have exactly these fields:

| Field | Rule |
| --- | --- |
| id | Unique nonempty text |
| client, title, scope | Nonempty text |
| acceptance | Text, may be empty; empty triggers review |
| fee_cents | Integer from 0 through 1000000000000, no floats or booleans |
| currency | Three uppercase letters; totals remain separate per currency |
| start_date, end_date | ISO YYYY-MM-DD; end cannot precede start |
| signed | Boolean; false triggers review |
| synthetic | Boolean; true for any invented or illustrative record |

Text is limited to 10000 characters per field. Unicode and Windows paths are supported. Control characters except newline and tab are rejected. Em dash characters in input text are normalized to hyphens. Duplicate IDs are rejected across files, rather than silently counted twice. Future start dates are valid and flagged relative to the explicit `--as-of` reference date, default `2026-09-30`. End dates may be in the future. The tool does not infer whether work is overdue.

See `examples/tiny/contracts.jsonl` for a hand-written five-record synthetic input. Run `scg run --input examples/tiny`. Henry can copy this schema and enter his own records by hand, setting `synthetic: false` only for real data. Keep real trial files outside the repository and do not ship trial results.

## Commands

- `scg fixtures --out demo`: creates 200 synthetic records and independent expectations. Replaces the two named fixture files in the output directory.
- `scg run --input demo --as-of 2026-09-30`: validates all records, computes fees and issues, and atomically saves `.scg-results.json`. `--state path` selects a different state file.
- `scg audit --input demo --state audit.json`: performs the same review workflow and preserves full evidence.
- `scg draft --input demo --id SOW-001`: renders a lightweight Markdown SOW to stdout. Includes a warning when acceptance is missing.
- `scg report --format json --out report.json`: recomputes from the saved records and explicit reference date, then renders Markdown or JSON. `--state path` selects the source. Output writes are atomic.

Each subcommand has `--help` and an example. Errors return exit code 2. Successful audits return 0 even with issues because these are review findings, not schema failures.

## Architecture

```text
JSONL files -> cli.read_input -> core.validate / core.compute
                                         |          |
                                    core.statement  report.render -> stdout / atomic file
fixtures.generate -> synthetic JSONL + independent expectations.json
```

Core functions do no I/O. Money is integer cents, never floating point. Output ordering is fixed by ID and currency. No clock, randomness, model calls, external network calls, databases, or GPU dependencies are used. There is no random seed because generation uses fixed integer ranges. Same inputs and reference date produce identical UTF-8 result bytes.

## Honesty boundary and fixture policy

The tool computes only from explicit records. Contract fees are not realised revenue or savings. Synthetic fees are illustrative, not measured business outcomes. Every fixture record has `synthetic: true`; JSONL has a SYNTHETIC header comment, and the expectations JSON has a synthetic flag and label. Every report and draft carries provenance. Real status is operator-declared, not verified; the tool cannot assert that records are Henry's own data without external evidence. Mixed datasets report both counts. No time or money savings are reported: without a measured baseline, the output explicitly states they are unmeasured. No predictions or invented acceptance terms are added.

The fixture has 200 contracts at 10000 GBP cents each: 2000000 cents. IDs 1 through 40 lack acceptance, 1 through 50 are unsigned, and 1 through 10 have future starts: 100 issue occurrences, 50 distinct affected contracts. Tests compare the exact issue ID sets, ensuring all planted cases and zero false positives. Changing a fee or an acceptance field changes computed results. Expectations are never consulted by the engine.

## Failure modes

Malformed JSON and record schema failures name the input file and line. Unsupported file formats name the file and line 1. Missing directories or saved state produce MissingInput with a usage hint. Unknown or absent fields produce SchemaError with field names. Negative fees, excessive text, duplicate IDs, or invalid dates fail the entire run before saving results. Empty directories yield zero counts and empty currency totals. Failed report writes produce WriteError and remove temporary files, preserving any prior target. Input read permission and encoding failures are reported without tracebacks. Results are a local snapshot; rerun after changing inputs.

## Evidence and acceptance

`EVIDENCE.md` records the local test result and timed installed-CLI demo. These are synthetic acceptance evidence, not evidence of customer demand or time saved. The fixture results reconcile exactly. The tiny example provides the smallest workflow. The hypothesis is validated only for deterministic computation and review against planted ground truth.

## Two-week improvement hook and verdict

Start a two-week evidence window when Henry first uses this on real work. Hand-check every field and issue on at least five SOWs per week. Metric: incorrect output facts or issue decisions divided by all hand-checked facts and decisions. Also record actual run count, dates, baseline manual duration, CLI plus correction duration, and reasons for corrections in a private trial log. Time saved is measured only from paired baseline and actual timings. If error rate exceeds 10 percent or no actual use occurs, record the top cause, fix it and repeat the sample, or kill the project with the reason.

Verdict: **maintain**, provisionally as portfolio evidence from synthetic acceptance tests. The final two-week verdict is pending real use; no such evidence is invented. After the window, record dated evidence and reason: expand for daily use or revenue; integrate for heavy sibling overlap; commercialise if a buyer will pay as-is; maintain for portfolio evidence otherwise; kill for no use or failed acceptance criteria.

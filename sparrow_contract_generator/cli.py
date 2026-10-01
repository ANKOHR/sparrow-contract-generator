"""Local-only CLI. JSONL records are read with file and line diagnostics."""
import argparse
import json
import os
from pathlib import Path
import tempfile
from .core import InputError, compute, statement
from .fixtures import generate
from .report import render

def read_input(directory, exclude=None):
    path = Path(directory)
    if not path.is_dir():
        raise InputError(f"MissingInput: {path}: use scg fixtures --out demo or provide an input directory")
    records = []
    seen = set()
    for file in sorted(path.iterdir()):
        if file.name == "expectations.json" or (exclude and file.resolve() == Path(exclude).resolve()):
            continue
        if file.suffix != ".jsonl":
            raise InputError(f"SchemaError: {file}: line 1: unsupported file; use JSONL")
        for number, line in enumerate(file.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip() or line.startswith("#"):
                continue
            try:
                record = json.loads(line)
                from .core import validate
                validate(record, "2026-09-30")
                if record["id"] in seen:
                    raise InputError(f"SchemaError: id: duplicate {record['id']}")
                seen.add(record["id"])
            except (json.JSONDecodeError, InputError) as exc:
                raise InputError(f"ParseOrSchemaError: {file}: line {number}: {exc}") from None
            records.append(record)
    return records

def write_atomic(path, text):
    path = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=path.parent, delete=False) as handle:
            temporary = handle.name
            handle.write(text)
        os.replace(temporary, path)
    except OSError as exc:
        raise InputError(f"WriteError: {path}: {exc}") from None
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)

def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate and audit lightweight SOWs from explicit local inputs.")
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("fixtures", help="Generate 200 labelled synthetic SOWs", epilog="Example: scg fixtures --out demo")
    p.add_argument("--out", required=True)
    for name, description in (("run", "Compute contract fees and named review issues"), ("audit", "Audit missing acceptance, signatures and future starts"), ("draft", "Render one lightweight statement of work")):
        p = commands.add_parser(name, help=description, description=description, epilog=f"Example: scg {name} --input demo" + (" --id SOW-001" if name == "draft" else ""))
        p.add_argument("--input", required=True)
        p.add_argument("--as-of", default="2026-09-30", help="Explicit reference date, default 2026-09-30; future starts are flagged, not rejected")
        if name == "draft":
            p.add_argument("--id", required=True)
        else:
            p.add_argument("--state", default=".scg-results.json")
    p = commands.add_parser("report", help="Render saved results with provenance", epilog="Example: scg report --format md")
    p.add_argument("--format", choices=("md", "json"), default="md")
    p.add_argument("--state", default=".scg-results.json")
    p.add_argument("--out")
    args = parser.parse_args(argv)
    try:
        if args.command == "fixtures":
            generate(args.out)
            print("Created 200 SYNTHETIC records. Illustrative fees; no savings measured.")
        elif args.command in ("run", "audit", "draft"):
            result = compute(read_input(args.input, getattr(args, "state", None)), args.as_of)
            if args.command == "draft":
                matches = [r for r in result["records"] if r["id"] == args.id]
                if not matches:
                    raise InputError(f"MissingInput: id {args.id}: choose an existing contract id")
                print(statement(matches[0]), end="")
            else:
                write_atomic(args.state, render(result, "json"))
                print(render(result), end="")
        else:
            state = Path(args.state)
            if not state.is_file():
                raise InputError(f"MissingInput: {state}: run scg run --input <dir> first")
            try:
                saved = json.loads(state.read_text(encoding="utf-8"))
                result = compute(saved["records"], saved["as_of"])
            except (json.JSONDecodeError, KeyError, TypeError) as exc:
                raise InputError(f"SchemaError: {state}: line 1: invalid results: {exc}") from None
            output = render(result, args.format)
            if args.out:
                write_atomic(args.out, output)
            else:
                print(output, end="")
        return 0
    except (InputError, OSError, UnicodeError) as exc:
        print(str(exc).replace(chr(0x2014), "-"), file=__import__("sys").stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())

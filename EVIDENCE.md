# Build evidence

Local Windows CPU-only validation on 2026-10-01:

- Installed scg entry point: fixtures, run, report in sequence completed in 0.730 seconds, below 5 seconds.
- 200 synthetic records, 2000000 GBP cents, 100 planted issue occurrences, exact expected ID sets and zero false positives.
- 21 pytest tests passed. Includes corrupted-record sensitivity, Unicode, long text, determinism, all command help, tiny hand-written input, schema failures and atomic-write failure.
- Synthetic data only. No real-use timings, revenue, savings, or demand measured.

The demo uses fixed as-of date 2026-09-30. Elapsed time is measured wall-clock runtime for three installed CLI processes, not a claim about owner time saved. Future runtimes vary by machine load.

Final two-week verdict is pending Henry's real-use trial. Provisional verdict: maintain as portfolio evidence.

---
name: everything-fast
description: Speed up a slow Python, Node.js/TypeScript, Ruby, Java, Go, PHP, C, C++ or C# app by porting its hottest pure functions to Rust and proving each port gives the same results on real recorded calls. Use when the user wants their Python code faster, asks about hot paths or profiling, or says "rewrite the slow part in Rust".
---

# everything-fast

The `everything-fast` CLI measures, records, builds, checks and swaps. You write the Rust.
(The same steps are MCP tools: `everything_scan`, `everything_port`, `everything_verify`, `everything_enable`, `everything_bench`, `everything_report`.)

## Loop

1. **Scan**: `everything-fast scan -- python app.py`, using the command the user runs their app with
   (a representative workload, not the test suite). Pick the top function marked "port it".
   Skip anything under 2% of the run: porting it can't make a visible difference.
2. **Port**: `everything-fast port <id>`. It re-runs the app, records up to 500 real calls, and creates
   `.fast/ports/<id>/` with a stub `src/lib.rs` and a `TASK.md`. Read TASK.md fully.
3. **Write the Rust** in `src/lib.rs` (Ruby, Java, Go, PHP, C, C++, C#: `src/port.rs`; `src/lib.rs` there is generated glue):
   - Same semantics: Unicode code points (`.chars()`; JavaScript compares UTF-16 units), integer ranges, float operation order, error cases.
   - Fast: borrow, no needless allocation, ASCII fast paths, `with_capacity`.
   - Keep the function and module names. Run `cargo check` in the crate.
4. **Verify**: `everything-fast verify <id>` builds in release mode and replays every recorded call.
   On mismatch, read the failing call, fix, verify again. Never edit the recordings.
5. **Enable**: `everything-fast enable <id>`, then `everything-fast bench` and `everything-fast report`.
6. Tell the user the end-to-end speedup, the per-call speedup, and how to undo
   (`everything-fast disable <id>`, or `EVERYTHING_FAST_DISABLE=1` for a single run).

## Don't

- Don't edit the original Python function: the block appended to its module does the swap.
- Don't enable a port that hasn't passed verify.
- If a function shows ✗ (I/O, randomness, globals, lives in the entry script), say why it can't be ported yet.
  Suggest moving pure logic into its own module when that's the blocker.

#!/usr/bin/env node
// Runs the prebuilt everything-fast binary for this platform (installed as an optional dependency).
"use strict";
const { spawnSync } = require("node:child_process");
const fs = require("node:fs");

const pkg = `everything-fast-${process.platform}-${process.arch}`;
const exe = process.platform === "win32" ? "everything-fast.exe" : "everything-fast";
let bin;
try {
  bin = require.resolve(`${pkg}/bin/${exe}`);
} catch {
  console.error(
    `everything-fast: no prebuilt binary for ${process.platform}-${process.arch} (${pkg} isn't installed).\n` +
      "Reinstall without --omit=optional, or build it: cargo install everything-fast",
  );
  process.exit(1);
}
// Published tarballs have shipped this file as 0644. Set the bit before spawn.
if (process.platform !== "win32") {
  try {
    fs.chmodSync(bin, 0o755);
  } catch {
    // spawnSync reports EACCES if the file still isn't executable
  }
}
const run = spawnSync(bin, process.argv.slice(2), { stdio: "inherit" });
if (run.error) {
  console.error(`everything-fast: ${run.error.message}`);
  process.exit(1);
}
process.exit(run.status ?? 1);

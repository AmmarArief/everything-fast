// Publishes the npm packages from release binaries:
//   node npm/publish.mjs <version> <dir with bin-<rust target>/everything-fast[.exe]> [--dry-run] [--stage]
// --stage: npm stage publish, for tokens that may only stage (each version is then approved with 2FA on npmjs.com).
// One package per platform (everything-fast-<os>-<cpu>) plus the everything-fast launcher.
import { execFileSync } from "node:child_process";
import { chmodSync, copyFileSync, existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const [version, dist, ...flags] = process.argv.slice(2);
if (!version || !dist) throw new Error("usage: node npm/publish.mjs <version> <dist> [--dry-run] [--stage]");
const dry = flags.includes("--dry-run");
const stage = flags.includes("--stage");
const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..");
const out = path.join(root, "target", "npm");
rmSync(out, { recursive: true, force: true });

const TARGETS = {
  "x86_64-pc-windows-msvc": ["win32", "x64"],
  "x86_64-unknown-linux-gnu": ["linux", "x64"],
  "aarch64-unknown-linux-gnu": ["linux", "arm64"],
  "aarch64-apple-darwin": ["darwin", "arm64"],
  "x86_64-apple-darwin": ["darwin", "x64"],
};
const main = JSON.parse(readFileSync(path.join(here, "everything-fast", "package.json"), "utf8"));
const publish = (dir) => {
  const provenance = process.env.GITHUB_ACTIONS ? ["--provenance"] : [];
  const args = [...(stage ? ["stage"] : []), "publish", "--access", "public", ...(dry ? ["--dry-run"] : provenance)];
  execFileSync("npm", args, { cwd: dir, stdio: "inherit", shell: process.platform === "win32" });
};

for (const [target, [os, cpu]] of Object.entries(TARGETS)) {
  const exe = os === "win32" ? "everything-fast.exe" : "everything-fast";
  const src = path.join(dist, `bin-${target}`, exe);
  if (!existsSync(src)) throw new Error(`missing ${src}`);
  const name = `everything-fast-${os}-${cpu}`;
  const dir = path.join(out, `everything-fast-${os}-${cpu}`);
  mkdirSync(path.join(dir, "bin"), { recursive: true });
  copyFileSync(src, path.join(dir, "bin", exe));
  chmodSync(path.join(dir, "bin", exe), 0o755);
  const pkg = {
    name,
    version,
    description: `The ${os}-${cpu} binary for everything-fast.`,
    repository: main.repository,
    license: "MIT",
    os: [os],
    cpu: [cpu],
    ...(os === "linux" ? { libc: ["glibc"] } : {}),
    files: ["bin"],
  };
  writeFileSync(path.join(dir, "package.json"), JSON.stringify(pkg, null, 2) + "\n");
  publish(dir);
}

const dir = path.join(out, "everything-fast");
mkdirSync(path.join(dir, "bin"), { recursive: true });
copyFileSync(path.join(here, "everything-fast", "bin", "everything-fast.js"), path.join(dir, "bin", "everything-fast.js"));
copyFileSync(path.join(root, "README.md"), path.join(dir, "README.md"));
copyFileSync(path.join(root, "LICENSE"), path.join(dir, "LICENSE"));
main.version = version;
for (const dep of Object.keys(main.optionalDependencies)) main.optionalDependencies[dep] = version;
writeFileSync(path.join(dir, "package.json"), JSON.stringify(main, null, 2) + "\n");
publish(dir);

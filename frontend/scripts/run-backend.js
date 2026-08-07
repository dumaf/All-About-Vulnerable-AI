/**
 * Cross-platform script runner.
 * On Windows it runs the .cmd counterpart; on Unix it runs the .sh file via bash.
 *
 * Usage: node scripts/run-backend.js <script-name>
 *   e.g. node scripts/run-backend.js start
 *        node scripts/run-backend.js start_dos
 */

import { spawn } from "child_process";
import { resolve, dirname, join } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const backendDir = resolve(__dirname, "../../backend");

const scriptName = process.argv[2];
if (!scriptName) {
  console.error("Usage: node scripts/run-backend.js <script-name>");
  process.exit(1);
}

const isWindows = process.platform === "win32";
const scriptFile = isWindows
  ? join(backendDir, `${scriptName}.cmd`)
  : join(backendDir, `${scriptName}.sh`);

const child = isWindows
  ? spawn("cmd.exe", ["/c", scriptFile], { stdio: "inherit", shell: false })
  : spawn("bash", [scriptFile], { stdio: "inherit", shell: false });

child.on("exit", (code) => process.exit(code ?? 0));

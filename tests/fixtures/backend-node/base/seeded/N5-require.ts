const fs = require("node:fs");

export function exists(path: string): boolean {
  return fs.existsSync(path) as boolean;
}

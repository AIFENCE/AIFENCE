// SPDX-License-Identifier: AGPL-3.0-or-later
// Fails the build if the generated wiki contains a broken internal link or
// anchor. Cross-page links are the thing most likely to rot when a page is
// renamed, and a 404 in published documentation is worse than a build failure.
import { readdirSync, readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const SITE = join(dirname(fileURLToPath(import.meta.url)), "..", "site");

const files = readdirSync(SITE);
const pages = files.filter((f) => f.endsWith(".html"));
const assets = new Set(files);

const anchors = new Map();
for (const page of pages) {
  const html = readFileSync(join(SITE, page), "utf8");
  anchors.set(page, new Set([...html.matchAll(/\sid="([^"]+)"/g)].map((m) => m[1])));
}

const problems = [];
for (const page of pages) {
  const html = readFileSync(join(SITE, page), "utf8");
  for (const [, href] of html.matchAll(/href="([^"]+)"/g)) {
    if (/^(https?:|mailto:)/.test(href)) continue;
    const [target, fragment] = href.split("#");
    const file = target === "" ? page : target;
    if (!assets.has(file)) {
      problems.push(`${page} → ${href} (missing file)`);
      continue;
    }
    if (fragment && file.endsWith(".html") && !anchors.get(file)?.has(fragment)) {
      problems.push(`${page} → ${href} (missing anchor)`);
    }
  }
}

if (problems.length) {
  console.error(`broken links (${problems.length}):`);
  for (const problem of [...new Set(problems)].sort()) console.error(`  ${problem}`);
  process.exit(1);
}
console.log(`links ok: ${pages.length} pages checked`);

#!/usr/bin/env python3
"""Read a public GitHub project's licence structure and report what is open.

Kortix is open source. This script answers one question a company asks before
it adopts a project it found through an "open source" search result: which
directories are under which licence, and does production use of the parts a
company needs depend on a paid subscription?

    python3 check.py                          # different-ai/openwork
    python3 check.py --repo owner/name
    python3 check.py --repo owner/name --json

It reads only public files (LICENSE, README.md, the top-level tree) over the
GitHub API. No token is needed for public repositories. Standard library only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request

API = "https://api.github.com"
UA = {"User-Agent": "openwork-licence-audit/1.0", "Accept": "application/vnd.github+json"}
# A directory-split repository names its exceptions in the root LICENSE.
EXCEPTION = re.compile(r"(?:under|resides under|within)\s+(?:the\s+)?`?/?([A-Za-z0-9_.\-]+)/`?\s+directions?"
                       r"|under\s+the\s+`?/?([A-Za-z0-9_.\-]+)/`?\s+directory"
                       r"|(/[A-Za-z0-9_.\-]+)\s+director", re.I)
PAID = re.compile(r"(production use requires[^.]*\.|requires an? [A-Za-z ]+subscription[^.]*\.)", re.I)
SPDX = re.compile(r"SPDX-License-Identifier:\s*([A-Za-z0-9.\-+]+)")


def get(url: str) -> str:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=45) as r:
            return r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return ""
        raise


def api(path: str):
    body = get(API + path)
    return json.loads(body) if body.strip().startswith(("{", "[")) else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default="different-ai/openwork")
    ap.add_argument("--branch", default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    meta = api(f"/repos/{a.repo}")
    if not meta:
        print(f"cannot read {a.repo}", file=sys.stderr)
        return 2
    branch = a.branch or meta.get("default_branch") or "main"
    root = api(f"/repos/{a.repo}/contents/?ref={branch}") or []
    dirs = sorted(x["name"] for x in root if x.get("type") == "dir")
    licence = get(f"https://raw.githubusercontent.com/{a.repo}/{branch}/LICENSE")
    readme = get(f"https://raw.githubusercontent.com/{a.repo}/{branch}/README.md")

    detected = [m.group(1) for m in SPDX.finditer(licence)] or []
    text = " ".join(licence.split()) + " " + " ".join(readme.split())
    exceptions = set()
    for m in EXCEPTION.finditer(text):
        name = next(g for g in m.groups() if g)
        exceptions.add(name.strip("/"))
    exceptions &= set(dirs)
    m = PAID.search(text)
    paid = None
    if m:
        tail = text[m.start():m.start() + 400]
        stop = tail.find(". ")
        paid = (tail[:stop + 1] if stop > 20 else tail[:320]).strip()
    mit = re.search(r"\bMIT\b", text) is not None

    out = {
        "repo": a.repo, "branch": branch,
        "github_licence": (meta.get("license") or {}).get("spdx_id"),
        "spdx_in_file": detected, "mit_mentioned": mit,
        "top_level_dirs": dirs,
        "exception_dirs": sorted(exceptions),
        "mit_dirs": [d for d in dirs if d not in exceptions],
        "paid_use_clause": paid,
    }
    if a.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"repo: {a.repo} (branch {branch})")
        print(f"GitHub licence label: {out['github_licence'] or 'none'}")
        print(f"MIT mentioned in LICENSE/README: {'yes' if mit else 'no'}")
        if exceptions:
            print(f"\ndirectories carved OUT of the default licence: {', '.join(sorted(exceptions))}")
            print(f"directories under the default licence: {', '.join(out['mit_dirs']) or '—'}")
        else:
            print("\nno directory-split exceptions detected in the root LICENSE")
        if out["paid_use_clause"]:
            print(f"\npaid-use clause: {out['paid_use_clause']}")
        print("\nRead the files yourself: "
              f"https://github.com/{a.repo}/blob/{branch}/LICENSE")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/bin/bash
# Run every test of the prompt book package.
set -e
cd "$(dirname "$0")"
node test/test_engine.js | tail -3
node test/test_options.js
python3 test/test_book.py
# Distribution gate: the website copy and the zip must carry the current build.
python3 - <<'PY'
import hashlib, os, sys, zipfile
root = os.path.abspath("..")
bad = []
names = ["MIPF_Model_Prompt_Book.html", "MIPF_Model_Prompt_Book.qmd", "mipf_model_builder.html"]
site = os.path.join(root, "website", "materials", "promptbook")
zp = os.path.join(root, "mipf-2026-website.zip")
z = zipfile.ZipFile(zp) if os.path.exists(zp) else None
for n in names:
    cur = hashlib.sha256(open(n, "rb").read()).hexdigest()
    if os.path.isdir(site):
        p = os.path.join(site, n)
        if not os.path.exists(p) or hashlib.sha256(open(p, "rb").read()).hexdigest() != cur: bad.append("website copy stale: " + n)
    if z is not None:
        k = "materials/promptbook/" + n
        if k not in z.namelist() or hashlib.sha256(z.read(k)).hexdigest() != cur: bad.append("zip copy stale: " + n)
if bad:
    print("distribution check FAILED"); [print("  " + b) for b in bad]; sys.exit(1)
print("distribution check: website copy and zip match the current build")
PY

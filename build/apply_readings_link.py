# -*- coding: utf-8 -*-
"""Point every reading link at the shared MIPF-Readings folder.

usage: python3 apply_readings_link.py <folder share URL> <package root> [--dry]

Replaces each owner-only d.docs.live.net link in the website pages and the syllabus with the
folder share link and names the file to open inside the folder.
"""
import sys, re, os, json, glob, zipfile, shutil, urllib.parse as up
URL, ROOT = sys.argv[1], sys.argv[2]
DRY = "--dry" in sys.argv
man = json.load(open(os.path.join(ROOT, "src", "readings_manifest.json"), encoding="utf-8"))
by_old = {e["old_url"]: e["file"] for l in man.values() for e in l}
by_name = {}
for l in man.values():
    for e in l: by_name[up.unquote(e["old_url"].rsplit("/", 1)[-1]).lower()] = e["file"]
OLD = re.compile(r"https://d\.docs\.live\.net/72139f47f6570099/[^\s\"'<>)]+")

def file_for(u):
    if u in by_old: return by_old[u]
    return by_name.get(up.unquote(u.rsplit("/", 1)[-1]).lower())

def fix_html(s, stats):
    def anchor(m):
        u, attrs, label = m.group(1), m.group(2), m.group(3)
        f = file_for(u); stats["anchors"] += 1
        hint = f' <small>(in the folder: <b>{f}</b>)</small>' if f else ""
        if not f: stats["unknown"] += 1
        return f'<a href="{URL}"{attrs}>{label}</a>{hint}'
    s = re.sub(r'<a href="(https://d\.docs\.live\.net/[^"]+)"([^>]*)>(.*?)</a>', anchor, s, flags=re.S)
    left = len(OLD.findall(s)); stats["bare"] += left
    return OLD.sub(URL, s)

def fix_docx_xml(s, stats):
    def bare(m):
        f = file_for(m.group(0)); stats["docx"] += 1
        return URL + (f" (file: {f})" if f else "")
    return OLD.sub(bare, s)

stats = dict(anchors=0, unknown=0, bare=0, docx=0, pages=0)
for p in glob.glob(os.path.join(ROOT, "website", "*.html")):
    s = open(p, encoding="utf-8").read(); t = fix_html(s, stats)
    if t != s:
        stats["pages"] += 1
        if not DRY: open(p, "w", encoding="utf-8").write(t)
d = os.path.join(ROOT, "MIPF_October_2026_Course_Syllabus.docx")
zin = zipfile.ZipFile(d); tmp = d + ".tmp"
with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
    for it in zin.infolist():
        b = zin.read(it.filename)
        if it.filename.endswith((".xml", ".rels")):
            s = b.decode("utf-8"); t = fix_docx_xml(s, stats)
            if t != s: b = t.encode("utf-8")
        zo.writestr(it, b)
zin.close()
if DRY: os.remove(tmp)
else: shutil.move(tmp, d)
print(stats)

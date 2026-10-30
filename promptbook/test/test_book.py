"""Consistency tests for the prompt book and app data: every block complete, no unresolved tokens, every number quoted from the engine, spec rows present."""
import json, re, sys, os
ROOT = os.path.join(os.path.dirname(__file__), "..")
J = lambda f: json.load(open(f"{ROOT}/data/{f}", encoding="utf-8"))
pb, num, inp = J("promptbook.json"), J("numbers.json"), J("inputs.json")
fails = []
def need(c, msg):
    if not c: fails.append(msg)
need(len(pb["blocks"]) == 24, "24 blocks expected")
ids = [b["id"] for b in pb["blocks"]]; need(ids == [f"B{i:02d}" for i in range(24)], "block ids B00..B23 in order")
for b in pb["blocks"]:
    for k in ("title", "day", "purpose", "depends", "produces", "concept", "steps", "checks", "options", "pitfalls"):
        need(b.get(k), f'{b["id"]}: missing {k}')
    need(len(b["steps"]) >= 3, f'{b["id"]}: fewer than 3 steps')
    need(len(b["options"]) >= 2, f'{b["id"]}: fewer than 2 options')
    need(len(b["pitfalls"]) >= 2, f'{b["id"]}: fewer than 2 failure modes')
    if b["sheet"] and b["id"] not in ("B00",): need(len(b["spec"].splitlines()) >= 3, f'{b["id"]}: specification too short')
    for o in b["options"]: need(len(o) == 3 and all(o), f'{b["id"]}: option needs 3 fields')
    for text in [b["purpose"], b["concept"]] + b["steps"] + b["checks"]:
        need("nan" not in text.lower().split() and "None" not in text, f'{b["id"]}: stray None/nan')
src = open(f"{ROOT}/MIPF_Model_Prompt_Book.qmd", encoding="utf-8").read()
for m in re.findall(r"\{\{([A-Za-z0-9_.]+)\}\}", src):
    need(m in ("rate", "dscr", "g", "yDays", "valDate", "upfront", "tenor", "tdep", "tax", "shlRate", "shlPct", "req", "profile", "omSens", "omFixed", "nyrs", "nca0", "mpp", "life", "lifeCapex", "hard", "hFixed", "hVar", "gmax", "gearing", "first", "facility", "eqCommit", "dsraN", "dc", "drawdown", "constrN", "commit", "cpi0", "cpiH", "cpiO", "capD", "capI", "fare", "arDays", "apDays", "acq") or m.startswith(("R.", "S.")), f"unresolved token {{{{{m}}}}} in QMD")
# headline numbers in the QMD match the engine output
b = num["base"]; s = num["start"]["Base"]
need(f'{s["npv"]:,.1f}' in src and f'{b["D"]:,.1f}' in src, "headline numbers present")
need(abs(s["npv"] - 17608.9873) < 0.01 and abs(b["irr"] - 0.4303360) < 1e-6 and abs(b["minDSCR"] - 2.296607) < 1e-5, "reference numbers match the workbook")
need(abs(num["pf"]["Upside"]["U"] - 101402.9843) < 0.01 and abs(num["pf"]["Upside"]["irr"] - 0.669030) < 1e-6, "Upside matches the workbook (facility rule)")
need(abs(num["pf"]["Downside"]["npv"] + 7230.7246) < 0.01, "Downside matches the workbook")
need(num["dated"]["eq1"]["irrDated"] < num["dated"]["pro"]["irrDated"] < num["dated"]["pro"]["irrCOD"], "dated IRR: lower than the COD IRR; equity first worse for the sponsor")
need(num["gridBest"]["irr"] >= max(g["irr"] for g in num["grid"] if g["minDSCR"] >= 2.0) - 1e-12, "grid optimum is the best admissible cell")
need(1.3 < num["frozen"]["Downside"]["minLoss"] < 1.6, "Downside on the Base financing between 1.3x and 1.6x")
# every figure quoted as the grid optimum in the block text is consistent with the grid
need(f'{num["gridBest"]["irr"]*100:.2f}%' in open(f"{ROOT}/src/blocks.py", encoding="utf-8").read(), "B22 quotes the grid optimum")
html = open(f"{ROOT}/MIPF_Model_Prompt_Book.html", encoding="utf-8").read() if os.path.exists(f"{ROOT}/MIPF_Model_Prompt_Book.html") else ""
need('class="math' not in html, "rendered book has no TeX math spans (Excel $ signs intact)")
need("Day Day" not in re.sub(r"<[^>]+>", "", html), 'no "Day Day" duplication')
need(num["opt"]["dsra"]["2"]["irr"] == b["irr"], "DSRA=2 option equals the base case")
need(abs(num["opt"]["shl"]["0.6"]["irr"] - b["irr"]) < 1e-12, "SHL=60% option equals the base case")
need(all(abs(num["opt"]["repay"]["sculpt"][k] - b[k]) < 1e-9 for k in ("irr", "D", "minDSCR")), "sculpt option equals the base case")
for t in num["tornado"]: need(0 < t["irr"] < 1, f'tornado {t["name"]} irr range')
# positive figure gate: checkpoints quoted in the blocks equal the engine values
blk = {b["id"]: " ".join(b["checks"] + [o[2] for o in b["options"]] + [b["concept"]]) for b in pb["blocks"]}
def has(bid, v, fmt): need(fmt.format(v) in blk[bid], f"{bid}: checkpoint {fmt.format(v)} missing or stale")
has("B20", b["minDSCR"], "{:.4f}"); has("B20", b["avgDSCR"], "{:.4f}"); has("B20", b["llcr"], "{:.4f}"); has("B20", b["plcr"], "{:.4f}")
has("B16", b["D"], "{:,.1f}"); has("B16", b["g"] * 100, "{:.2f}%"); has("B14", b["idc"], "{:,.1f}"); has("B14", b["cfee"], "{:,.1f}"); has("B14", b["upfront"], "{:,.1f}")
has("B19", b["shl0"], "{:,.1f}"); has("B19", b["sumDiv"], "{:,.0f}"); has("B18", b["maxDSRA"], "{:,.0f}")
need(f'{num["dated"]["pro"]["irrDated"]*100:.2f}%' in blk["B14"], "B14: dated IRR quoted correctly")
# rendered HTML: formulas must not be eaten by Markdown emphasis
if html:
    em = re.findall(r"<em>([^<]*)</em>", html)
    bad_em = [e for e in em if re.search(r"\$?[A-Z]{1,3}\$?\d|J\d", e) and ("=" in e or "/" in e)]
    need(not bad_em, f"formula text rendered as emphasis: {bad_em[:3]}")
# grep gate: no pre-rebase constant may survive outside original-file / defect-catalogue contexts
STALE = ["2.2958", "2.3966", "2.3979", "4.2031", "34.90%", "32.19%", "43.34%", "72,403", "101,089", "28,686", "28,482", "17,688", "17,687", "33.77%", "442,970", "6,529", "44.50%", "66.55%", "67.04%", "75,816", "54,097", "-7,051", "40,409", "45.97%", "24.93%", "76,434", "101,912", "17,211"]
for fn in ("src/blocks.py", "src/gen_promptbook.py", "src/templates.py", "app/app.js", "README.md", "MIPF_Model_Prompt_Book.qmd"):
    for ln, line in enumerate(open(f"{ROOT}/{fn}", encoding="utf-8"), 1):
        for k in STALE:
            if k in line and not re.search(r"original|Original|D15|D12|original day count|day-count|day count|previous|earlier build|reproduc|daysShort|replica", line):
                fails.append(f"stale pre-rebase figure {k} at {fn}:{ln}")
css = open(f"{ROOT}/app/app.css", encoding="utf-8").read()
for sel in (".pill.ok", ".pill.bad"):
    m = re.search(re.escape(sel) + r"\{([^}]*)\}", css)
    need(m and "background:" in m.group(1) and "color:" in m.group(1), f"app.css: {sel} must set both background and text colour (a later .bad text rule must not make it red on red)")
need(re.search(r"data-theme=dark\] \.pill\{color:#0b1020\}", css) and re.search(r"data-theme=auto\] \.pill\{color:#0b1020\}", css), "app.css: dark-theme pill text must be dark")
app_html = open(f"{ROOT}/mipf_model_builder.html", encoding="utf-8").read()
app_css = re.search(r"<style>(.*?)</style>", app_html, re.S).group(1)  # CSS only: the logos make the rest of the file slow to scan
def theme_sels(h, name):
    return {(a.strip() + "{" + b.strip() + "}").replace("data-theme=" + name, "data-theme=T") for a, b in re.findall(r"([^{}@]*:root\[data-theme=" + name + r"\][^{}]*)\{([^{}]*)\}", h)}
dk, au = theme_sels(app_css, "dark"), theme_sels(app_css, "auto")
need(len(dk) > 20 and dk <= au, "app: every dark-theme rule must have an auto-theme (prefers-color-scheme:dark) twin; missing: " + "; ".join(sorted(dk - au))[:300])
print("book tests:", "PASS" if not fails else "FAIL"); [print(" -", f) for f in fails]
sys.exit(1 if fails else 0)

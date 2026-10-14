# -*- coding: utf-8 -*-
"""Generate the MIPF Model Prompt Book (QMD) and the data files used by the interactive app.
Usage: python3 gen_promptbook.py <promptbook_dir>"""
import json, re, sys, os, datetime as dt
sys.path.insert(0, os.path.dirname(__file__))
from blocks import BLOCKS, CHARTER, PATHS, DEFECTS, DIAG, PATTERNS, CAVEATS, CAVEATS_INTRO, CONTRACT_MAP, CREDIT_QUESTIONS, GLOSSARY_EXTRA, TUTOR_TRANSCRIPT, OBJECTIVES, TIMES, CONCEPT_QA
from templates import TEMPLATES, TOOLS

ROOT = sys.argv[1]
D = lambda f: json.load(open(f"{ROOT}/data/{f}"))
INP, NUM, A_PF, A_ST = D("inputs.json"), D("numbers.json"), D("atlas_pf.json"), D("atlas_start.json")
P = INP["P"]["Base"]; ROWS = INP["rows"]; LAB = INP["labels"]; UNIT = INP["units"]
NB, NS = NUM["base"], NUM["start"]["Base"]

# ------------------------------------------------------------------------------------------------ formatting and tokens
def fnum(v, fmt):
    if v is None or v == "": return ""
    if isinstance(v, str): return v
    if fmt == "pct0": return f"{v*100:.0f}%"
    if fmt == "pct1": return f"{v*100:.1f}%"
    if fmt == "pct2": return f"{v*100:.2f}%"
    if fmt == "n0": return f"{v:,.0f}"
    if fmt == "n1": return f"{v:,.1f}"
    if fmt == "n2": return f"{v:,.2f}"
    if fmt == "n3": return f"{v:,.3f}".rstrip("0").rstrip(".")
    if fmt == "x2": return f"{v:.2f}x"
    if fmt == "x4": return f"{v:.4f}x"
    if fmt == "date":
        d = dt.date.fromisoformat(str(v)[:10]); return f"{d.day} {d.strftime('%b %Y')}"
    return str(v)
KEYFMT = dict(first="date", acq="date", nyrs="n0", mpp="n0", cpi0="n0", cpiH="n0", cpiO="n0", capD="n0", capI="n0", fare="n3", arDays="n0", hFixed="n0", hVar="n0", omFixed="n0", apDays="n0",
              nca0="n0", life="n0", lifeCapex="n0", gearing="pct2", profile="n0", rate="pct2", dc="n0", tdep="pct1", tax="pct1", valDate="date", yDays="n0", req="pct2", constrN="n0",
              hard="n0", upfront="pct2", commit="pct2", facility="n0", drawdown="n0", eqCommit="n0", tenor="n0", dscr="x2", gmax="pct0", dsraN="n0", shlPct="pct0", shlRate="pct1", omSens="pct0")
RTOK = dict(U=("n1", "Asset base at COD (total uses)"), D=("n1", "Senior debt"), E=("n1", "Sponsor funding"), g=("pct2", "Gearing"), cap=("n1", "Debt capacity at COD"), binding=("raw", "Binding constraint"),
            irr=("pct2", "Blended sponsor IRR"), npv=("n1", "Blended NPV at the required return"), minDSCR=("x4", "Minimum DSCR"), avgDSCR=("x4", "Average DSCR"), llcr=("x4", "LLCR at COD"), plcr=("x4", "PLCR at COD"),
            maxDSRA=("n0", "Peak DSRA balance"), sumDiv=("n0", "Total dividends"), shlInt=("n0", "Shareholder-loan interest paid"), shlPrin=("n0", "Shareholder-loan principal repaid"),
            idc=("n1", "Interest during construction"), cfee=("n1", "Commitment fee"), upfrontFee=("n1", "Upfront fee"), hardTotal=("n0", "Hard cost"), sh0=("n1", "Shareholder loan at COD"), sc0=("n1", "Share capital at COD"))
STOK = dict(npv=("n1", "Shareholder NPV (start model)"), irr=("pct2", "Shareholder XIRR (start model)"), pirr=("pct2", "Project XIRR (start model)"), minDSCR=("x2", "Minimum DSCR (start model, profile 1)"),
            avgDSCR=("x2", "Average DSCR (start model)"), rev=("n0", "Total revenue (20 years)"), cost=("n0", "Total operating cost"), ebitda=("n0", "Total EBITDA"), dep=("n0", "Total accounting depreciation"),
            intr=("n0", "Total senior interest"), pat=("n0", "Total profit after tax"), tax=("n0", "Total tax expense"), cfads=("n0", "Total CFADS"), div=("n0", "Total dividends"))
RMAP = dict(upfrontFee=NB["upfront"], hardTotal=NB["hard"], sh0=NB["shl0"], sc0=NB["sc0"])
def default_token(key):
    if key.startswith("R."):
        k = key[2:]
        if k not in RTOK: return None
        v = RMAP.get(k, NB.get(k)); return fnum(v, RTOK[k][0])
    if key.startswith("S."):
        k = key[2:]
        if k not in STOK: return None
        return fnum(NS[k], STOK[k][0])
    if key == "nca0": return "100,000"
    if key == "profile": return "4"
    if key == "gearing": return fnum(NB["g"], "pct2")
    if key in P: return fnum(P[key], KEYFMT.get(key, "n2"))
    if key in TEXTDEF: return TEXTDEF[key]
    return None
TEXTDEF = dict(MATDATE="31 Dec 2031", OS="Windows or Mac", drawdownName="pro-rata", idcName="opening balance", repayName="sculpted", sizingName="solved by Goal Seek", taxIntName="interest deductible", modeName="project finance")
def resolve(text):
    return re.sub(r"\{\{([A-Za-z0-9_.]+)\}\}", lambda m: (default_token(m.group(1)) if default_token(m.group(1)) is not None else m.group(0)), text)

def xl_date(v):
    try:
        f = float(v)
        if 36000 < f < 60000: d = dt.date(1899, 12, 30) + dt.timedelta(days=int(f)); return f"{d.day} {d.strftime('%b %Y')}"
    except Exception: pass
    return str(v)
def fval(v):
    if v is None or v == "": return ""
    if isinstance(v, str): return v
    a = abs(v)
    if a >= 1000: return f"{v:,.2f}"
    if a >= 1: return f"{v:,.4f}".rstrip("0").rstrip(".")
    return f"{v:.6g}"

FUNCS = INP.get("funcs") or []
TOOLS["excel"] = ", ".join(FUNCS)
# ------------------------------------------------------------------------------------------------ specification and checkpoints
def spec_rows(b):
    atl = A_PF if b["atlas"] == "pf" else A_ST
    rows = [x for x in atl if x["s"] in b["sheet"] and x["t"] in ("pull", "calc", "const")]
    out = []
    for x in rows:
        if x["s"] not in ("InpC", "InpS") and x["r"] in (2, 3, 4, 5): continue
        out.append(x)
    return out
def spec_lines(b):
    L = []
    for x in spec_rows(b):
        lab = xl_date(x["l"]); r = f'{x["s"]}!R{x["r"]}'
        if x["s"] == "InpC":
            sc = x.get("sc")
            if not sc: continue
            vals = " / ".join(sc[i] if sc[i] != "" else "-" for i in range(3))
            L.append(f'{r} | {lab} | unit {x.get("u","")} | F: {x["f"]} | Base / Downside / Upside: {vals}')
            continue
        if x["s"] == "InpS":
            L.append(f'{r} | {lab} | unit {x.get("u","")} | J..CO: typed time series | total H={fval(x.get("h"))}'); continue
        parts = [r, lab]
        if x["f"] and x["f"] not in ("Constant",): parts.append(f'F: {x["f"]}' if not x["f"] in ("IS", "CF", "BS", "IS&CF") else f'statement tag {x["f"]}')
        if x["j"]: parts.append(f'J: {x["j"]}')
        if x.get("x"): parts.append(f'first-column exception, K: {x["x"]}')
        if x.get("h") not in (None, "") and not (isinstance(x["h"], (int, float)) and abs(x["h"]) < 1e-9): parts.append(f'H={fval(x["h"]) if not isinstance(x["h"], str) else x["h"]}')
        elif isinstance(x.get("h"), (int, float)) and x["t"] in ("calc",): parts.append("H=0 or blank (no meaningful total)")
        if x.get("lv") not in (None, "") and not isinstance(x.get("lv"), str):
            lv = x["lv"]; parts.append(f'L={xl_date(lv) if (36000 < lv < 60000 and re.search(r"date|ending|beginning|period|start", lab, re.I)) else fval(lv)}')
        sv = [(k, x.get(key)) for k, key in (("Dec-23", "v23"), ("Dec-31", "v31"), ("CO", "vco")) if isinstance(x.get(key), (int, float))]
        if sv and x["s"] != "Constr" and x["t"] in ("calc", "pull") and any(abs(v) > 1e-9 for _, v in sv): parts.append("spot " + ", ".join(f"{k}={fval(v)}" for k, v in sv))
        L.append(" | ".join(parts))
    return L
def checkpoint_lines(b):
    L = []
    for c in b.get("checks", []): L.append("- " + c)
    return L
def inputs_lines(b):
    L = []
    for k in b["inputs"]:
        if k not in ROWS: continue
        u = "" if KEYFMT.get(k, "n2") in ("pct0", "pct1", "pct2", "x2", "date") else UNIT.get(k, "")
        L.append(f'- {LAB.get(k, k).strip()} (InpC row {ROWS[k]}): {{{{{k}}}}} {u}'.rstrip())
    return L or ["- (no numeric inputs: this block is structural)"]
BLOCK_RESULTS = {"B04": ["S.rev"], "B05": ["S.cost"], "B06": ["S.tax"], "B07": ["S.dep"], "B08": ["S.intr", "S.minDSCR"], "B09": ["S.div"], "B10": ["S.ebitda", "S.pat", "S.cfads"],
                 "B11": ["S.npv", "S.irr", "S.pirr"], "B12": ["S.npv", "S.irr"], "B13": ["S.npv", "S.irr"], "B14": ["R.hardTotal", "R.upfrontFee", "R.idc", "R.cfee", "R.U", "R.D", "R.E"],
                 "B15": ["R.U", "R.D", "R.E"], "B16": ["R.cap", "R.D", "R.g", "R.binding", "R.minDSCR"], "B17": ["R.minDSCR", "R.avgDSCR"], "B18": ["R.maxDSRA", "R.irr"],
                 "B19": ["R.sh0", "R.sc0", "R.shlInt", "R.shlPrin", "R.irr"], "B20": ["R.minDSCR", "R.avgDSCR", "R.llcr", "R.plcr"], "B21": ["R.irr", "R.npv", "R.sumDiv"],
                 "B22": ["R.irr", "R.g", "R.D", "R.minDSCR", "R.binding"]}
def keyresults_lines(b):
    ks = BLOCK_RESULTS.get(b["id"], [])
    if not ks: return []
    L = ["EXPECTED KEY RESULTS FOR THESE INPUTS (from the verified engine)"]
    for k in ks:
        lab = (RTOK if k.startswith("R.") else STOK)[k[2:]][1]; L.append(f"- {lab}: {{{{{k}}}}}")
    return L

def fill(tpl, b, os_="{{OS}}"):
    spec = "\n".join(spec_lines(b)) if b["atlas"] else "(structural block: no row specification; follow the build order below)\n" + "\n".join(f"{i+1}. {s}" for i, s in enumerate(b["steps"]))
    cks = "\n".join(checkpoint_lines(b)) or "(see the checks listed for the sheets this block touches)"
    rep = {"TITLE": b["title"], "SHEETS": ", ".join(b["sheet"]) if b["sheet"] else "the workbook structure", "PURPOSE": b["purpose"], "CONCEPT": b["concept"], "DEPENDS": b["depends"],
           "PRODUCES": b["produces"], "SPEC": spec, "CHECKPOINTS": cks, "KEYRESULTS": "\n".join(keyresults_lines(b)), "INPUTS": "\n".join(inputs_lines(b)), "CHARTER": CHARTER,
           "OS": os_, "TOOLS": "{{TOOLS_%s}}"}
    out = tpl
    for k, v in rep.items(): out = out.replace("{{" + k + "}}", v)
    return out
def prompt_text(kind, b, resolved=True):
    tpl = TEMPLATES[kind]
    t = fill(tpl, b)
    t = t.replace("{{TOOLS_%s}}", TOOLS.get(kind, "")).replace("{{TOOLS}}", TOOLS.get(kind, ""))
    return resolve(t) if resolved else t

# ------------------------------------------------------------------------------------------------ data for the app
def app_blocks():
    out = []
    for b in BLOCKS:
        item = {k: b[k] for k in ("id", "title", "day", "sheet", "purpose", "depends", "produces", "inputs", "concept", "steps", "checks", "options", "pitfalls")}
        item["spec"] = "\n".join(spec_lines(b)) if b["atlas"] else ""
        item["results"] = BLOCK_RESULTS.get(b["id"], [])
        out.append(item)
    return out
tokens = dict(P={k: dict(label=LAB.get(k, k).strip(), unit=UNIT.get(k, ""), fmt=KEYFMT.get(k, "n2")) for k in ROWS}, R={k: dict(fmt=v[0], label=v[1]) for k, v in RTOK.items()},
              S={k: dict(fmt=v[0], label=v[1]) for k, v in STOK.items()})
json.dump(dict(blocks=app_blocks(), templates=TEMPLATES, tools=TOOLS, charter=CHARTER, paths=PATHS, diag=DIAG, defects=DEFECTS, patterns=PATTERNS, tokens=tokens),
          open(f"{ROOT}/data/promptbook.json", "w"), ensure_ascii=False, separators=(",", ":"))

# ------------------------------------------------------------------------------------------------ QMD
Q = []
w = Q.append
SHORT = dict(tutor="A Tutor", excel="B Formulas", script="C Script", replica="D Replica", verify="V Audit")
def md_table(head, rows, align=None):
    s = "| " + " | ".join(head) + " |\n|" + "|".join("---" for _ in head) + "|\n"
    for r in rows: s += "| " + " | ".join(str(c).replace("|", "\\|").replace("\n", " ") for c in r) + " |\n"
    return s
def code(txt, lang="text"): return f"::: {{.prompt}}\n```{lang}\n{txt}\n```\n:::\n"
def bq(t): return t.replace("\n", " ")

w('''---
title: "MIPF Model Prompt Book"
subtitle: "Everything that builds the TrainStat financial model: prompts, specifications, checkpoints, options and alternative paths"
author: "Prof Bongo Adi, Lagos Business School"
date: last-modified
date-format: "D MMMM YYYY"
description: "Mastering Infrastructure and Project Finance Boot Camp, 14 to 21 October 2026. Reproduces the complete corrected model (start model and project-finance extension) with copy-ready prompts for five build paths (plus a reading path for lenders and lawyers), independent verification and the options that change the answer."
format:
  html:
    from: markdown-tex_math_dollars
    theme: [cosmo, custom.scss]
    toc: true
    toc-depth: 3
    toc-location: left
    number-sections: true
    code-copy: true
    code-overflow: wrap
    anchor-sections: true
    smooth-scroll: true
    page-layout: full
    embed-resources: true
    include-before-body: header.html
    include-after-body: footer.html
    link-external-newwindow: true
lang: en
---

''')
CAV_MD = "\n".join('::: {.callout-warning title="' + t + '"}\n' + d + "\n:::\n" for t, d in CAVEATS)
RET_MD = md_table(["#", "Convention", "What it does", "Effect and option"], [d[:4] for d in DEFECTS if d[0].startswith("R")])
MAP_MD = md_table(["Model input (where)", "Contract or document that controls it", "Course day"], CONTRACT_MAP)
QS_MD = "\n".join(f"{i+1}. {q}" for i, q in enumerate(CREDIT_QUESTIONS))
TRANSCRIPT_MD = "\n".join(f"**{who}:** {txt}\n" for who, txt in TUTOR_TRANSCRIPT)
w(f'''# Start here {{.unnumbered}}

This book is the **recipe** for the TrainStat model that is built on Days 4 to 7 of the boot camp. It is written so that a facilitator, a participant, a reviewer or another AI assistant can rebuild every sheet, check every number and choose a different path where the course path does not suit. It has four layers.

1. **Specification.** Every sheet, every row, every formula in the first timeline column, taken directly from the verified workbooks (not retyped).
2. **Prompts.** For each of the 24 build blocks, five ready-to-paste prompts: a tutor, a formula generator, a script builder, an independent replica and an auditor. Each prompt contains the specification, the input values and the checkpoints, so it works on its own.
3. **Evidence.** Every checkpoint number was produced by an independent engine and agrees with Microsoft Excel (the final build was recalculated in Excel for Mac on 10 October 2026 in all three scenarios) and with a full formula evaluation of the delivered workbooks. Base case: shareholder NPV **{NS["npv"]:,.1f}**, XIRR **{NS["irr"]*100:.2f}%** (start model); sized debt **{NB["D"]:,.1f}** at gearing **{NB["g"]*100:.2f}%**, minimum DSCR **{NB["minDSCR"]:.4f}x**, blended sponsor IRR **{NB["irr"]*100:.2f}% measured from COD** (**{NUM["dated"]["pro"]["irrDated"]*100:.2f}%** when each contribution is dated when it is paid; see the retained conventions) (project-finance model).
4. **Options.** Alternative paths (drawdown, interest during construction, repayment style, DSRA, shareholder loan, tax treatment, sizing) with the effect of each on the answer, computed, not guessed.

::: {{.callout-tip title="The interactive companion"}}
`mipf_model_builder.html` (same folder) runs the whole model in your browser. Change any input, switch any option, see every statement, ratio, check and chart, and export the prompts tailored to **your** inputs, with the expected results for those inputs inserted in the checkpoints. Use it to explore; use this book to build.
:::

::: {{.callout-note title="Contacts"}}
Prof Bongo Adi, Lagos Business School. Phone / WhatsApp +234 706 164 8699. badi@lbs.edu.ng. bongo.adi@fulbrightmail.org.
:::

## How to use this book {{.unnumbered}}

| If you want to... | Do this |
|---|---|
| Learn to build the model in Excel | Pick **Path A** (tutor) and work through blocks B00 to B23 in order. Paste the tutor prompt, then type the formulas yourself. |
| Build quickly and correct later | Pick **Path B** (formula generator), paste, fill right, then run **V** (verify) before moving on. |
| Rebuild the workbook reproducibly | Pick **Path C** (script). Keep the generated scripts in version control. |
| Prove that a workbook is right | Pick **Path D** (replica) and compare to the precision shown (the Atlas holds full-precision values), then run **V**. |
| Change the structure (e.g. equity first, no DSRA) | Go to the **Options** table at the end of the block and to the [options atlas](#sec-options); each option says what to change in the prompt and what the answer becomes. |
| Read and challenge the model without building it | Pick **Path L** (see the chapter on scope, caveats and retained conventions) and answer the ten credit questions in the app. |
| Teach it | Use the Day 4 to Day 7 slide decks for the sessions and this book for homework and self-study. |

# The build paths {{#sec-paths}}

{md_table(["Path", "What happens", "Best for", "Cost / risk"], [(f"**{p[1]}**", p[2], p[3], p[4]) for p in PATHS] + [("**L. Lender and lawyer reading path**", "No Excel build: run the interactive app and answer ten credit questions (see Scope, caveats and retained conventions).", "Lawyers, credit officers, regulators", "Fast; you learn to read the model, not to build it")])}
**Rule of thumb.** Never move to the next block until the verify prompt (V) returns PASS and the checkpoints agree. Errors compound across sheets; a wrong flag in `Time` poisons everything.

# Scope, caveats and retained conventions {{#sec-caveats}}

{CAVEATS_INTRO}

{CAV_MD}
## Conventions retained from the original workbook {{.unnumbered}}

These are known simplifications. They were not changed so that every checkpoint matches the delivered workbook; each is quantified so that you can decide.

{RET_MD}
## From model input to contract clause {{.unnumbered}}

{MAP_MD}
## Path L: the lender and lawyer reading path (no Excel build) {{.unnumbered}}

Use the interactive app and this book without building the model. Run the Base case, then answer these ten credit questions with the app (tabs Summary, Debt and cover, Scenarios and sensitivity, Prompt studio).

{QS_MD}

# The model charter {{#sec-charter}}

Paste this charter at the start of any conversation, or let each block prompt carry it (they do). It is the contract that makes the formulas auditable.

{code(CHARTER)}
# Prompt patterns that work for modelling {{#sec-patterns}}

{md_table(["Pattern", "How", "In this book"], PATTERNS)}
# A worked tutor session (Path A) {{#sec-transcript}}

What a good Path A conversation looks like for block B05 (OpCost). The tutor explains, hints and checks; the learner types.

{TRANSCRIPT_MD}
# Build sequence at a glance {{#sec-sequence}}

{md_table(["Block", "Day", "Sheet(s)", "Delivers", "Checkpoint"], [(f'[{b["id"]}](#sec-{b["id"].lower()})', b["day"], ", ".join(b["sheet"]) if b["sheet"] else "structure", b["produces"][:110], (b["checks"][0] if b["checks"] else "")[:110]) for b in BLOCKS])}
''')

# ---------------------------------------------------------------- block chapters
w("# The build blocks {#sec-blocks}\n\nEach block follows the same eleven-part pattern: purpose, concept, inputs, build order, specification, prompts (five paths), checkpoints, options, failure modes. Values shown are the course **Base** case unless stated.\n")
for b in BLOCKS:
    w(f'\n## {b["id"]} {b["title"]} {{#sec-{b["id"].lower()}}}\n')
    w(f'::: {{.block-meta}}\n**Day** {b["day"].replace("Day ", "", 1) if b["day"].startswith("Day") else b["day"]} · **Sheet(s)** {", ".join(b["sheet"]) if b["sheet"] else "workbook structure"} · **Depends on** {b["depends"]} · **Produces** {b["produces"]} · **Suggested time (Path A)** {TIMES[b["id"]]} minutes\n\n**By the end you can** {OBJECTIVES[b["id"]]}.\n:::\n')
    w(f'**Purpose.** {b["purpose"]}\n\n**Concept.** {b["concept"]}\n')
    il = [x for x in b["inputs"] if x in ROWS]
    if il:
        rows = []
        for k in il:
            r = ROWS[k]
            sc = [P and INP["P"][s][k] for s in ("Base", "Downside", "Upside")]
            f = KEYFMT.get(k, "n2")
            vals = [fnum(v, f) for v in sc]
            rows.append((LAB.get(k, k).strip(), f"InpC row {r}", vals[0], vals[1], vals[2], UNIT.get(k, "")))
        w("### Inputs used\n\n" + md_table(["Input", "Where", "Base", "Downside", "Upside", "Unit"], rows))
        w("\n(In the project-finance workbook the Base, Downside and Upside facility and gearing cells hold the solved values; see B16.)\n" if "facility" in il or "gearing" in il else "")
    w("### Build order\n\n" + "\n".join(f"{i+1}. {s}" for i, s in enumerate(b["steps"])) + "\n")
    if b["atlas"]:
        sl = spec_lines(b)
        w(f'### Specification ({len(sl)} rows)\n\n::: {{.callout-note collapse="true" title="Show the row-by-row specification"}}\n' + "Format: sheet row | label | formulas | totals (H) and first-forecast-quarter values (L) from the verified workbook.\n\n" + code("\n".join(sl)) + ":::\n")
    w("### Prompts\n\n::: {.panel-tabset}\n")
    for kind, name, *_ in PATHS:
        w(f"#### {SHORT[kind]}\n\n" + code(prompt_text(kind, b)))
    w(":::\n")
    w("### Checkpoints\n\n" + "\n".join(f"- {c}" for c in b["checks"]) + "\n")
    w("### Options and alternative paths\n\n" + md_table(["Option", "How to change the build", "Effect"], b["options"]))
    w("### Failure modes\n\n" + md_table(["Symptom", "Likely cause", "Fix"], b["pitfalls"]))
    w('::: {.callout-note collapse="true" title="Self-check: concept questions and what to do when it breaks"}\n**Concept questions**\n\n' + "\n".join(f"{i+1}. {q}\n   *Answer:* {an}" for i, (q, an) in enumerate(CONCEPT_QA[b["id"]])) + "\n\n**When it breaks**\n\n" + "\n".join(f"{i+1}. You see: {p[0]}. *Likely cause and fix:* {p[1]}. {p[2]}." for i, p in enumerate(b["pitfalls"])) + "\n:::\n")

# ---------------------------------------------------------------- options atlas
def pct(v): return f"{v*100:.2f}%"
O = NUM["opt"]
w("\n# Options atlas: what changes the answer {#sec-options}\n\nAll figures are the Base scenario of the project-finance model, re-solved for each option (gearing found so that debt drawn equals debt sized), computed by the engine in `mipf_model_builder.html`. Where an option is not in the delivered workbook it is marked *app only*.\n")
def optrows(d, labelf, keys):
    return [labelf(k) + [f'{d[k]["U"]:,.0f}', f'{d[k]["D"]:,.0f}', pct(d[k]["g"]), f'{d[k]["minDSCR"]:.2f}x', pct(d[k]["irr"]), f'{d[k]["npv"]:,.0f}'] for k in keys]
H = ["Option", "Project cost", "Senior debt", "Gearing", "Min DSCR", "Blended IRR (from COD, R1)", "NPV @25.25% (from COD)"]
w("## Drawdown and interest during construction\n\nIRR and NPV in this table are measured from COD, as in the workbook (convention R1). Equity first looks better from COD; **dated at the contributions the ranking reverses** (see \"Sponsor IRR: measured from COD versus dated\" below).\n\n" + md_table(H, [["Pro-rata, interest on opening balance (course)"] + optrows(O["drawdown"], lambda k: [], ["pro"])[0],
   ["Equity first, opening-balance interest"] + optrows(O["drawdown"], lambda k: [], ["eq1"])[0], ["Equity first, average-balance interest (*app only*)"] + optrows(O["drawdown"], lambda k: [], ["eq1avg"])[0],
   ["Pro-rata, average-balance interest (algebraic, *app only* in the solved case)"] + optrows(O["idc"], lambda k: [], ["avg"])[0]]))
T = NUM["teaching"]
w("\nTeaching case on Day 6 (facility 60,000, gearing 60%, hard cost 94,850):\n\n" + md_table(["Method", "IDC", "Commitment fee", "Total uses", "Debt at COD", "Equity at COD"],
   [(n, f'{T[k]["idc"]:,.1f}', f'{T[k]["cfee"]:,.1f}', f'{T[k]["U"]:,.1f}', f'{T[k]["D"]:,.1f}', f'{T[k]["E"]:,.1f}') for n, k in (("Pro-rata, opening balance", "open"), ("Pro-rata, average balance", "avg"), ("Equity first", "eq1"), ("Equity first, average balance", "eq1avg"))]))
rn = dict(sculpt="Sculpted (profile 4)", p1="Profile 1 (7.5 years straight line)", p2="Profile 2 (10 years)", p3="Profile 3 (15 years)", equal="Equal principal over the tenor (*app only*)")
w("\n## Repayment style (same debt size, different shape)\n\nThe debt is sized once on the sculpting capacity (target 2.25x over 40 quarters); the other shapes then repay that debt. They show why sculpting exists: with the same debt, a straight-line profile collapses cover in the weakest quarters. Profile 2 shows a higher IRR at a minimum DSCR of about 1.2x: that is not bankable at this debt size (below typical sizing levels and near lock-up); lenders limit back-ended profiles through average-life and tail requirements. These rows are *app only*: in the workbook the shareholder loan is repaid after the Sculpt tenor, so with profiles 2 and 3 it can be repaid while senior debt is still outstanding.\n\n" +
  md_table(["Repayment", "Debt", "Min DSCR", "Average DSCR", "Last repayment quarter", "Blended IRR"], [(rn[k], f'{O["repay"][k]["D"]:,.0f}', f'{O["repay"][k]["minDSCR"]:.2f}x', f'{O["repay"][k]["avgDSCR"]:.2f}x', O["repay"][k]["lastRep"], pct(O["repay"][k]["irr"])) for k in rn]))
w("\n## DSRA cover (periods of senior debt service)\n\n" + md_table(["Cover periods", "Peak DSRA", "Min DSCR", "Blended IRR", "NPV @25.25%", "Total dividends"], [(k, f'{O["dsra"][k]["maxDSRA"]:,.0f}', f'{O["dsra"][k]["minDSCR"]:.2f}x', pct(O["dsra"][k]["irr"]), f'{O["dsra"][k]["npv"]:,.0f}', f'{O["dsra"][k]["sumDiv"]:,.0f}') for k in O["dsra"]]))
w("\n## Shareholder loan share of sponsor funding\n\n" + md_table(["SHL share", "Loan at COD", "Interest paid", "Blended IRR", "NPV @25.25%"], [(f'{float(k)*100:.0f}%', f'{O["shl"][k]["shl0"]:,.0f}', f'{O["shl"][k]["shlInt"]:,.0f}', pct(O["shl"][k]["irr"]), f'{O["shl"][k]["npv"]:,.0f}') for k in O["shl"]]))
w("\n## Tax treatment of interest\n\n" + md_table(["Treatment", "Blended IRR", "NPV @25.25%", "Deferred tax at the end"], [("Interest deductible (corrected model)", pct(O["taxInt"]["on"]["irr"]), f'{O["taxInt"]["on"]["npv"]:,.0f}', f'{O["taxInt"]["on"]["dtaxEnd"]:,.0f}'),
   ("Interest not deducted (original error, *app only* in the PF model)", pct(O["taxInt"]["off"]["irr"]), f'{O["taxInt"]["off"]["npv"]:,.0f}', f'{O["taxInt"]["off"]["dtaxEnd"]:,.0f}')]) + "\nA stranded deferred-tax balance at the end of the forecast is the signature of this error. In the 'not deducted' case retained cash also goes negative, so its IRR is indicative only.\n")
for key, title, fm in (("gmax", "Maximum gearing", lambda k: f'{float(k)*100:.0f}%'), ("dscr", "Target DSCR", lambda k: f'{float(k):.2f}x'), ("tenor", "Senior debt tenor (quarters)", lambda k: k), ("rate", "All-in senior interest rate", lambda k: f'{float(k)*100:.1f}%')):
    w(f"\n## {title}\n\n" + md_table([title, "Debt", "Gearing", "Binding", "Min DSCR", "Blended IRR"], [(fm(k), f'{O[key][k]["D"]:,.0f}', pct(O[key][k]["g"]), O[key][k]["binding"], f'{O[key][k]["minDSCR"]:.2f}x', pct(O[key][k]["irr"])) for k in O[key]]))
w("\n## Structure grid: target DSCR x tenor (75% gearing cap)\n\n" + md_table(["Target DSCR", "Tenor (quarters)", "Capacity", "Debt", "Gearing", "Min DSCR", "Blended IRR", "Binding"], [(f'{g["dscr"]:.2f}x', g["tenor"], f'{g["cap"]:,.0f}', f'{g["D"]:,.0f}', pct(g["g"]), f'{g["minDSCR"]:.2f}x', pct(g["irr"]), g["binding"]) for g in NUM["grid"]]))
w("\n## One-way sensitivities (each fully re-solved)\n\n" + md_table(["Case", "Blended IRR", "Min DSCR", "Debt", "Gearing", "NPV @25.25%"], [("Base", pct(NB["irr"]), f'{NB["minDSCR"]:.2f}x', f'{NB["D"]:,.0f}', pct(NB["g"]), f'{NB["npv"]:,.0f}')] + [(t["name"], pct(t["irr"]), f'{t["minDSCR"]:.2f}x', f'{t["D"]:,.0f}', pct(t["g"]), f'{t["npv"]:,.0f}') for t in NUM["tornado"]]) +
  "\nFare and occupancy shocks give identical results because revenue is the product of fare and passengers.\n")
w("\n## The three scenarios (each solved)\n\n" + md_table(["Scenario", "Project cost", "Debt", "Equity", "Gearing", "Binding", "Min DSCR", "LLCR", "Blended IRR", "NPV"], [(s, f'{NUM["pf"][s]["U"]:,.0f}', f'{NUM["pf"][s]["D"]:,.0f}', f'{NUM["pf"][s]["E"]:,.0f}', pct(NUM["pf"][s]["g"]), NUM["pf"][s]["binding"], f'{NUM["pf"][s]["minDSCR"]:.2f}x', f'{NUM["pf"][s]["llcr"]:.2f}x', pct(NUM["pf"][s]["irr"]), f'{NUM["pf"][s]["npv"]:,.0f}') for s in NUM["pf"]]))
FZ, DT, LC, BE = NUM["frozen"], NUM["dated"], NUM["lossCF"], NUM["breakeven"]
w("\n## Debt sized once: scenarios tested on the fixed Base financing\n\nA credit committee does not re-size the debt in each scenario. Debt size and the sculpted repayment schedule are frozen at the Base case; cash flows, tax and cover are recomputed. *Refund* is the workbook's treatment of tax losses; *carry-forward* is the app option. Covenants are usually tested at each calculation date on a historic 12-month basis (and often also a projected one; LLCR tests use the projections), so both the single-quarter minimum (stricter; the weakest quarter is the 31 Dec 2023 capex quarter) and the rolling 12-month minimum are shown. IRRs marked * ignore lock-up and default consequences, which the model does not contain: in those cases distributions would be blocked.\n\n" +
  md_table(["Case on the Base financing", "Min DSCR, quarter (refund)", "Min DSCR, quarter (carry-forward)", "Min DSCR, rolling 12 months (carry-forward)", "Average DSCR", "LLCR at COD", "Blended IRR from COD"], [(k, f'{v["minRefund"]:.2f}x', f'{v["minLoss"]:.2f}x', f'{v["min12Loss"]:.2f}x', f'{v["avgRefund"]:.2f}x', f'{v["llcr"]:.2f}x', pct(v["irr"]) + (" *" if v["min12Loss"] < 1.2 else "") + ("; negative cash, indicative only" if v["negCash"] else "")) for k, v in FZ.items()]) +
  f'\nBreakeven fare (Base financing, carry-forward): the **single-quarter** minimum DSCR reaches 1.20x at a fare **{100*(1-BE["1.20"]):.1f}% below** Base and 1.00x at **{100*(1-BE["1.00"]):.1f}% below**; on the **rolling 12-month** basis the figures are **{100*(1-BE["1.20_12"]):.1f}%** and **{100*(1-BE["1.00_12"]):.1f}%** (with tax refunds: quarter {100*(1-BE["1.20r"]):.1f}% and {100*(1-BE["1.00r"]):.1f}%; rolling {100*(1-BE["1.20r_12"]):.1f}% and {100*(1-BE["1.00r_12"]):.1f}%). A credit agreement tests the rolling basis, so a fare {100*(1-BE["1.20"]):.1f}% below Base would not by itself be a lock-up event; lumpy capex is normally smoothed through a major-maintenance reserve account. The re-solved Downside (minimum DSCR {NUM["pf"]["Downside"]["minDSCR"]:.2f}x) looks safer than the Downside on the Base financing ({FZ["Downside"]["minLoss"]:.2f}x quarterly, {FZ["Downside"]["min12Loss"]:.2f}x rolling) because the lenders have already lent less.\n')
w("\n## Sponsor IRR: measured from COD versus dated at the contribution dates\n\nThe workbook (Val) dates all sponsor funding at COD, although equity is paid in during construction. The app reports both.\n\n" +
  md_table(["Case (Base)", "Blended IRR from COD (workbook)", "Blended IRR dated at contributions", "Project cost", "Sponsor funding"], [(n, pct(DT[k]["irrCOD"]), pct(DT[k]["irrDated"]), f'{DT[k]["U"]:,.0f}', f'{DT[k]["E"]:,.0f}') for n, k in (("Pro-rata, opening-balance interest (course)", "pro"), ("Equity first", "eq1"), ("Equity first, average-balance interest", "eq1avg"), ("Pro-rata, average-balance interest", "avg"))]) +
  "\nFrom COD, equity first looks better; dated at the contributions it is worse for the sponsor, which is why sponsors negotiate pro-rata drawdown or letters of credit for undrawn equity.\n")
w("\n## Tax losses: refund (workbook) versus carry-forward (app option)\n\n" + md_table(["Scenario", "Quarters with a tax refund", "Min DSCR refund", "Min DSCR carry-forward", "Blended IRR refund", "Blended IRR carry-forward", "NPV refund", "NPV carry-forward"],
  [(k, v["refundQ"], f'{v["refundMin"]:.2f}x', f'{v["loseMin"]:.2f}x', pct(v["refundIrr"]), pct(v["loseIrr"]), f'{v["refundNpv"]:,.0f}', f'{v["loseNpv"]:,.0f}') for k, v in LC.items()]))
DX = NUM["daysShort"]
w("\n## Day count: the original file versus the corrected workbook\n\nThe original workbook counted days in period as end less the first day of the month (one day short per quarter). The corrected workbook adds the missing day. The app option 'original day count' reproduces the old figures.\n\n" + md_table(["Result", "Original file (end - beginning)", "Corrected workbook (+1 day)"], [("PF Base senior debt (original file vs corrected)", f'{DX["pf"]["D"]:,.0f}', f'{NB["D"]:,.0f}'), ("PF Base blended IRR from COD (original file vs corrected)", pct(DX["pf"]["irr"]), pct(NB["irr"])), ("Start model Base NPV (original file vs corrected)", f'{DX["start"]["npv"]:,.1f}', f'{NS["npv"]:,.1f}'), ("Start model Base XIRR (original file vs corrected)", pct(DX["start"]["irr"]), pct(NS["irr"]))]))
w("\n## Start model (Days 4 and 5): corrected versus original logic\n\n" + md_table(["Scenario", "Corrected NPV", "Corrected XIRR", "Original-logic NPV", "Original-logic XIRR", "Min DSCR (profile 1)"], [(s, f'{NUM["start"][s]["npv"]:,.1f}', pct(NUM["start"][s]["irr"]), f'{NUM["startOriginal"][s]["npv"]:,.1f}', pct(NUM["startOriginal"][s]["irr"]), f'{NUM["start"][s]["minDSCR"]:.2f}x') for s in NUM["start"]]) +
  "\n\"Original logic\" means interest not deducted in cash tax and the O&M sensitivity switched off. It is **not** the original file (whose scenarios were also mis-defined): it isolates the two logic errors.\n")
w("\n### Repayment profiles of the start model (Base)\n\n" + md_table(["Profile", "Min DSCR", "Average DSCR", "Total senior interest", "Shareholder XIRR", "NPV"], [(f"Profile {p}", f'{NUM["startProfiles"][p]["minDSCR"]:.2f}x', f'{NUM["startProfiles"][p]["avgDSCR"]:.2f}x', f'{NUM["startProfiles"][p]["intr"]:,.0f}', pct(NUM["startProfiles"][p]["irr"]), f'{NUM["startProfiles"][p]["npv"]:,.1f}') for p in ("1", "2", "3")]))
w("\n### One-way sensitivities of the start model (Base)\n\n" + md_table(["Case", "NPV", "XIRR", "Total EBITDA"], [(t["name"], f'{t["npv"]:,.1f}', pct(t["irr"]), f'{t["ebitda"]:,.0f}') for t in NUM["startSens"]]))

# ---------------------------------------------------------------- diagnostics, verification, defects, appendices
w("\n# Diagnostic prompts {#sec-diag}\n\nUse these when a check fails. Replace the <<...>> placeholders with your own values.\n")
for t, p in DIAG: w(f"\n**{t}**\n\n" + code(resolve(p)))
w("\n# Verification protocol {#sec-verify}\n\nThree independent layers, each catching what the others cannot.\n\n" + md_table(["Layer", "What it proves", "How"], [
  ("1. Checks inside the workbook", "Internal consistency: balance sheet, cash, income statement, sources = uses, debt repaid, deferred tax unwound.", "Cover status and the FinStat, Time, Constr and Sculpt checks (B23)."),
  ("2. Independent replica", "The formulas implement the stated logic: two different codebases agree to the precision of the checkpoints (6 decimals for the engine values).", "Path D prompts; `node test/test_engine.js` reproduces 89 workbook reference values (all three scenarios, read from a full formula evaluation of the delivered workbooks; the same kind of list runs live on the app's Verify tab); `node test/test_options.js` runs 2,160 option combinations and requires finite results and a balancing balance sheet."),
  ("3. Real Excel", "No hidden dependency on a library: the file recalculates in Microsoft Excel to the same numbers, with zero error cells in all three scenarios.", "The final workbooks (day-count correction, facility rule, automatic calculation mode) were recalculated in Microsoft Excel for Mac on 10 October 2026 for Base, Downside and Upside: project cost, debt, IRR, NPV and minimum DSCR equal the engine to 6 decimals, Cover reads ALL CHECKS PASSED and the Dashboard DSCR guard returns 0. Repeat this check in your own copy whenever you change anything.")]) +
  "\n## Reference values (Base)\n\n" + md_table(["Quantity", "Start model", "PF model"], [("Shareholder NPV @25.25%", f'{NS["npv"]:,.2f}', f'{NB["npv"]:,.2f} (blended, from COD)'), ("Shareholder XIRR", pct(NS["irr"]), f'{pct(NB["irr"])} (blended, from COD; {pct(NUM["dated"]["pro"]["irrDated"])} dated at the contributions)'), ("Project XIRR", pct(NS["pirr"]), "n/a"),
   ("Project cost / asset base", "100,000", f'{NB["U"]:,.2f}'), ("Senior debt", "60,000", f'{NB["D"]:,.2f}'), ("Sponsor funding", "40,000", f'{NB["E"]:,.2f}'), ("Gearing", "60%", pct(NB["g"])),
   ("Minimum DSCR", f'{NS["minDSCR"]:.2f}x (profile 1)', f'{NB["minDSCR"]:.4f}x'), ("Average DSCR", f'{NS["avgDSCR"]:.2f}x', f'{NB["avgDSCR"]:.4f}x'), ("LLCR / PLCR at COD", "n/a", f'{NB["llcr"]:.4f}x / {NB["plcr"]:.4f}x'),
   ("Total dividends", f'{NS["div"]:,.0f}', f'{NB["sumDiv"]:,.0f}'), ("Peak DSRA", "n/a", f'{NB["maxDSRA"]:,.0f}')]))
w("\n## Running the tests\n\n```bash\ncd promptbook\nnode test/test_engine.js     # 89 workbook reference values (three scenarios)\nnode test/test_options.js    # 2,160 option combinations\nquarto render MIPF_Model_Prompt_Book.qmd\n```\n")
w("\n# Defects, corrections and retained conventions {#sec-defects}\n\nThree groups: defects of the original file that the delivered model corrects (each a lesson in what the verify prompt must catch), defects of the earlier build of this model found in review and corrected, and conventions that are retained and documented.\n\n## Defects of the original file (corrected)\n\n" + md_table(["#", "Defect", "What was wrong", "Correction", "Block"], [d for d in DEFECTS if d[0] in ("D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10", "D15", "D16")]) + "\n## Defects of the earlier build, found in review (corrected)\n\n" + md_table(["#", "Defect", "What was wrong", "Correction", "Block"], [d for d in DEFECTS if d[0] in ("D11", "D12", "D13", "D14")]) + "\n## Retained conventions (documented, not corrected)\n\n" + md_table(["#", "Convention", "What it does", "Effect and option", "Block"], [d for d in DEFECTS if d[0].startswith("R")]))
w("\n# Appendices {#sec-appendices}\n")
def dv(v, u):
    if v in ("", None): return ""
    if re.match(r"\d{4}-\d\d-\d\dT", str(v)): return fnum(str(v)[:10], "date")
    try:
        f = float(v)
        if "%" in (u or "") and abs(f) <= 1.5: return f"{f*100:.2f}%".replace(".00%", "%")
        return f"{f:,.3f}".rstrip("0").rstrip(".") if abs(f) < 1000 else f"{f:,.0f}"
    except Exception: return str(v)
w("## Input dictionary\n\n" + md_table(["InpC row", "Input", "Unit", "Base", "Downside", "Upside"], [(x["r"], xl_date(x["l"]), x.get("u", ""), *(dv(x["sc"][i], x.get("u", "")) for i in range(3))) for x in A_PF if x["s"] == "InpC" and x.get("sc") and x["r"] < 150 and not all(re.match(r"^[%$A-Za-z /(+)]*$", str(v)) for v in x["sc"] if v != "")]))
w("\n## Row counts by sheet\n\n" + md_table(["Sheet", "Rows in the specification (start model)", "Rows (PF model)"], [(sh, sum(1 for x in A_ST if x["s"] == sh and x["t"] in ("pull", "calc", "const")), sum(1 for x in A_PF if x["s"] == sh and x["t"] in ("pull", "calc", "const"))) for sh in sorted({x["s"] for x in A_PF})]))
sys.path.insert(0, "/private/tmp/claude-501/-Users-adibongo-Library-CloudStorage-OneDrive-Personal-Mastering-Infrastructure-Project-Finance-2023/80e3f324-173b-4993-86d1-30b33f759168/scratchpad")
try:
    import xlcommon as X
    w("\n## Excel shortcuts used in the build blocks\n")
    for nm, tb in (("Moving and selecting", X.SC_NAV), ("Editing, copying and filling", X.SC_EDIT), ("Formulas and auditing", X.SC_FORM)):
        w(f"\n**{nm}**\n\n" + md_table(["Action", "Windows", "Mac"], [(a, f"`` {b_} ``", f"`` {c_} ``") for a, b_, c_ in tb]))
except Exception as e:
    w(f"\n(shortcut tables unavailable: {e})\n")
w("\n## Token reference for the interactive app\n\nTailored prompts replace tokens such as `{{rate}}` or `{{R.irr}}` with the values of the current run. Input tokens: " + ", ".join(f"`{{{{{k}}}}}`" for k in ROWS) + ". Result tokens: " + ", ".join(f"`{{{{R.{k}}}}}`" for k in RTOK) + ". Start-model result tokens: " + ", ".join(f"`{{{{S.{k}}}}}`" for k in STOK) + ".\n")
w("\n## Glossary\n\n" + md_table(["Term", "Meaning"], [("CFADS", "Cash flow available for debt service: operating cash flow less capex and tax."), ("COD", "Commercial operation date; here 31 Dec 2021 (end of construction)."), ("DSCR", "CFADS divided by interest plus principal in the period."),
  ("LLCR / PLCR", "Present value of CFADS over the loan life / project life divided by debt outstanding."), ("IDC", "Interest during construction, capitalised into the project cost."), ("DSRA", "Debt service reserve account holding the next N quarters of debt service."),
  ("SHL", "Shareholder loan: subordinated sponsor funding that earns interest."), ("Sculpting", "Shaping repayments so that DSCR is constant."), ("POS", "Positive-number row; the next row flips the sign for the statements."), ("XIRR", "Internal rate of return using actual dates (act/365).")] + GLOSSARY_EXTRA))
STAR = re.compile(r"(?<=[\w$)\]])\*(?=[\w$(])")
def protect(txt):
    out, fenced = [], False
    for ln in txt.split("\n"):
        if ln.startswith("```"): fenced = not fenced; out.append(ln); continue
        out.append(ln if fenced else STAR.sub(r"\\*", ln))
    return "\n".join(out)
open(f"{ROOT}/MIPF_Model_Prompt_Book.qmd", "w").write(protect("\n".join(Q)))
print("QMD written:", sum(len(x) for x in Q) // 1024, "KB;", len(BLOCKS), "blocks")

"use strict";
/* MIPF Model Builder: UI around engine.js. Everything runs in the browser; nothing is sent anywhere. */
const E = MIPF, N = E.N;
const INP = DATA.inputs, PB = DATA.pb, NUMS = DATA.numbers, ATL = { pf: DATA.atlasPF, start: DATA.atlasStart };
const SCN = ["Base", "Downside", "Upside"];
const $ = (s, r) => (r || document).querySelector(s), $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
const clone = (x) => JSON.parse(JSON.stringify(x));
const esc = (s) => String(s == null ? "" : s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const sum = E.sum;

// ------------------------------------------------------------------------------------------------ formatting
const FM = {
  n0: (v) => (v == null || !isFinite(v) ? "" : Math.abs(v) < 0.5 ? "0" : v.toLocaleString("en-US", { maximumFractionDigits: 0 })),
  n1: (v) => (v == null || !isFinite(v) ? "" : v.toLocaleString("en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 })),
  n2: (v) => (v == null || !isFinite(v) ? "" : v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })),
  n3: (v) => (v == null || !isFinite(v) ? "" : String(+v.toFixed(3))),
  pct0: (v) => (isFinite(v) ? (v * 100).toFixed(0) + "%" : "n/a"), pct1: (v) => (isFinite(v) ? (v * 100).toFixed(1) + "%" : "n/a"), pct2: (v) => (isFinite(v) ? (v * 100).toFixed(2) + "%" : "n/a"),
  x2: (v) => (isFinite(v) ? v.toFixed(2) + "x" : "n/a"), x4: (v) => (isFinite(v) ? v.toFixed(4) + "x" : "n/a"), raw: (v) => String(v),
  date: (v) => { const [y, m, d] = E.ymd(typeof v === "number" ? v : E.parse(v)); return d + " " + ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][m - 1] + " " + y; },
};
const dshort = (o) => { const [y, m] = E.ymd(o); return ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][m - 1] + "-" + String(y).slice(2); };
const fmtv = (v, f) => (typeof v === "number" && !isFinite(v) ? "n/a" : f === "pct" ? FM.pct1(v) : f === "x" ? FM.x2(v) : (FM[f] || FM.n0)(v));
const download = (name, text, type) => { const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([text], { type: type || "text/plain" })); a.download = name; document.body.appendChild(a); a.click(); setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 500); };
const copy = async (text, btn) => { try { await navigator.clipboard.writeText(text); } catch (e) { const t = document.createElement("textarea"); t.value = text; document.body.appendChild(t); t.select(); try { document.execCommand("copy"); } catch (e2) {} t.remove(); } if (btn) { const o = btn.textContent; btn.textContent = "Copied"; setTimeout(() => (btn.textContent = o), 1200); } };
const csv = (rows) => rows.map((r) => r.map((c) => { const s = c == null ? "" : String(c); return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; }).join(",")).join("\n");

// ------------------------------------------------------------------------------------------------ state
const DEFSTATE = { scn: "Base", mode: "pf", o: {} };
const LIMITS = { hard: [1, 1e7], dscr: [0.5, 10], tenor: [4, 78, 1], dsraN: [0, 20, 1], gmax: [10, 95], shlPct: [0, 99], shlRate: [0, 40], upfront: [0, 10], commit: [0, 10], rate: [0, 40], tax: [0, 60], req: [0, 100], arDays: [0, 365, 1], apDays: [0, 365, 1], nca0: [1, 1e7], gearing: [0, 95], fixedGearing: [5, 95], eqCommit: [0, 1e7], facility: [1, 1e7], fareM: [-90, 500], occM: [-90, 500], omM: [-90, 500], costM: [-90, 500] };
const OPTKEYS = new Set(["fareM", "occM", "omM", "costM", "rate", "tax", "req", "arDays", "apDays", "omSens", "taxInt", "lossCF", "daysShort", "nca0", "gearing", "profile", "hard", "upfront", "commit", "drawdown", "idc", "eqCommit", "sizing", "fixedGearing", "facility", "dscr", "tenor", "gmax", "repay", "dsraN", "shlPct", "shlRate", "spend", "rateAdd"]);
function validateState(j) {
  const s = clone(DEFSTATE); if (!j || typeof j !== "object") return s;
  if (["Base", "Downside", "Upside"].includes(j.scn)) s.scn = j.scn; if (["pf", "start"].includes(j.mode)) s.mode = j.mode;
  if (j.o && typeof j.o === "object") for (const k of Object.keys(j.o)) { const v = j.o[k]; if (!OPTKEYS.has(k)) continue;
    if (k === "spend") { if (Array.isArray(v) && v.length === 8 && v.every((x) => typeof x === "number" && isFinite(x) && x >= 0 && x <= 1)) s.o.spend = v; }
    else if (typeof v === "number" && isFinite(v)) { let x = v; const f = k === "fareM" || k === "occM" || k === "omM" || k === "costM"; const lim = LIMITS[k]; if (lim) { const mult = ["rate", "tax", "req", "upfront", "commit", "gmax", "shlPct", "shlRate", "gearing", "fixedGearing"].includes(k) ? 100 : 1; let y = x * mult; if (f) y = (x - 1) * 100; y = Math.min(lim[1], Math.max(lim[0], y)); if (lim[2]) y = Math.round(y); x = f ? 1 + y / 100 : y / mult; } s.o[k] = x; }
    else if (typeof v === "boolean" && ["omSens", "taxInt", "lossCF", "daysShort"].includes(k)) s.o[k] = v;
    else if (typeof v === "string" && ["drawdown", "idc", "sizing", "repay"].includes(k) && /^[a-z0-9]{2,6}$/.test(v)) s.o[k] = v; }
  return s;
}
const loadHash = () => { try { const m = location.hash.match(/s=([^&]+)/); if (m) return JSON.parse(decodeURIComponent(escape(atob(m[1])))); } catch (e) {} return null; };
let ST = validateState(loadHash());
let TAB = "summary", CUR = null, CURS = null, CURP = null, PIN = null, STMT_VIEW = "annual", OS = "Windows or Mac";
const saveHash = () => { try { history.replaceState(null, "", "#s=" + btoa(unescape(encodeURIComponent(JSON.stringify(ST))))); } catch (e) {} };
const effOpts = () => Object.assign({}, E.DEFAULT_OPTS, ST.o, { mode: ST.mode });
const baseP = () => INP.P[ST.scn];

// ------------------------------------------------------------------------------------------------ input definitions
const FIELDS = [
  { g: "Operating drivers", open: true, items: [
    { k: "fareM", label: "Fare change vs scenario", unit: "%", t: "chg", def: 0, step: 1, tip: "Revenue = fare x passengers; a fare shock and an occupancy shock have the same effect." },
    { k: "occM", label: "Occupancy change", unit: "%", t: "chg", def: 0, step: 1 },
    { k: "omM", label: "O&M cost change", unit: "%", t: "chg", def: 0, step: 1 },
    { k: "costM", label: "All operating costs change", unit: "%", t: "chg", def: 0, step: 1 },
    { k: "rate", label: "Senior interest rate (all-in)", unit: "% p.a.", t: "pct", base: (P) => P.rate, step: 0.1 },
    { k: "tax", label: "Corporation tax rate", unit: "%", t: "pct", base: (P) => P.tax, step: 1 },
    { k: "req", label: "Shareholder required return", unit: "% p.a.", t: "pct", base: (P) => P.req, step: 0.25 },
    { k: "arDays", label: "Receivable days", unit: "days", t: "num", base: (P) => P.arDays, step: 1 },
    { k: "apDays", label: "Payable days", unit: "days", t: "num", base: (P) => P.apDays, step: 1 },
  ] },
  { g: "Logic switches (corrected model)", open: false, items: [
    { k: "omSens", label: "O&M sensitivity input is live", t: "chk", def: true, tip: "Off reproduces the original file (InpC row 46 was not wired)." },
    { k: "taxInt", label: "Interest is deductible in cash tax", t: "chk", def: true, tip: "Off reproduces the original error: cash tax ignored interest and deferred tax was stranded." },
    { k: "lossCF", label: "Carry tax losses forward (no cash refund)", t: "chk", def: false, tip: "App option. The workbook refunds tax losses in cash in the quarter they arise." },
    { k: "daysShort", label: "Original day count (one day short)", t: "chk", def: false, tip: "App option reproducing the ORIGINAL file, which counted period end minus the first day of the month (a 361-day year). The corrected workbook adds the missing day." },
  ] },
  { g: "Start model only (Days 4 and 5)", mode: "start", open: true, items: [
    { k: "nca0", label: "Asset base at acquisition", unit: "$000s", t: "num", def: 100000, step: 1000 },
    { k: "gearing", label: "% of assets financed with debt", unit: "%", t: "pct", def: 0.6, step: 1 },
    { k: "profile", label: "Repayment profile", t: "sel", def: 1, opts: [[1, "1: 7.5 years straight line"], [2, "2: 10 years"], [3, "3: 15 years"]] },
  ] },
  { g: "Construction (project finance)", mode: "pf", open: true, items: [
    { k: "hard", label: "Hard cost", unit: "$000s", t: "num", base: (P) => P.hard, step: 500 },
    { k: "upfront", label: "Upfront fee (% of facility)", unit: "%", t: "pct", base: (P) => P.upfront, step: 0.05 },
    { k: "commit", label: "Commitment fee (% p.a. undrawn)", unit: "%", t: "pct", base: (P) => P.commit, step: 0.05 },
    { k: "drawdown", label: "Drawdown method", t: "sel", def: "pro", opts: [["pro", "Pro-rata debt : equity"], ["eq1", "Equity first"]] },
    { k: "idc", label: "Interest during construction", t: "sel", def: "open", opts: [["open", "On opening balance (workbook)"], ["avg", "On average balance (algebraic)"]] },
    { k: "eqCommit", label: "Equity commitment (equity first, fixed gearing)", unit: "$000s", t: "num", base: (P) => P.eqCommit, step: 500 },
  ] },
  { g: "Debt sizing and repayment (project finance)", mode: "pf", open: true, items: [
    { k: "sizing", label: "Sizing", t: "sel", def: "solve", opts: [["solve", "Solve gearing (Goal Seek logic)"], ["fixed", "Fixed gearing"]] },
    { k: "fixedGearing", label: "Fixed gearing", unit: "%", t: "pct", def: 0.6, step: 1, only: () => effOpts().sizing === "fixed" },
    { k: "facility", label: "Facility override (fixed sizing)", unit: "$000s", t: "num", def: null, step: 500, only: () => effOpts().sizing === "fixed", blank: true },
    { k: "dscr", label: "Target DSCR", unit: "x", t: "num", base: (P) => P.dscr, step: 0.05 },
    { k: "tenor", label: "Senior debt tenor", unit: "quarters", t: "num", base: (P) => P.tenor, step: 4 },
    { k: "gmax", label: "Maximum gearing", unit: "%", t: "pct", base: (P) => P.gmax, step: 1 },
    { k: "repay", label: "Repayment style", t: "sel", def: "sculpt", opts: [["sculpt", "Sculpted to target DSCR"], ["p1", "Profile 1 (7.5 yrs)"], ["p2", "Profile 2 (10 yrs)"], ["p3", "Profile 3 (15 yrs)"], ["equal", "Equal principal (app only)"]] },
  ] },
  { g: "Reserve account and sponsor funding (project finance)", mode: "pf", open: true, items: [
    { k: "dsraN", label: "DSRA cover", unit: "quarters", t: "num", base: (P) => P.dsraN, step: 1 },
    { k: "shlPct", label: "Shareholder loan share of sponsor funding", unit: "%", t: "pct", base: (P) => P.shlPct, step: 5 },
    { k: "shlRate", label: "Shareholder loan interest", unit: "% p.a.", t: "pct", base: (P) => P.shlRate, step: 0.5 },
  ] },
];
const PRESETS = {
  "Course Base: project finance": { scn: "Base", mode: "pf", o: {} },
  "Course Downside: project finance": { scn: "Downside", mode: "pf", o: {} },
  "Course Upside: project finance": { scn: "Upside", mode: "pf", o: {} },
  "Start model, Base (Days 4 and 5)": { scn: "Base", mode: "start", o: {} },
  "Start model, original logic (two errors)": { scn: "Base", mode: "start", o: { taxInt: false, omSens: false } },
  "Day 6 teaching case (60% gearing, facility 60,000)": { scn: "Base", mode: "pf", o: { sizing: "fixed", fixedGearing: 0.6, facility: 60000 } },
  "Day 6 teaching case, equity first": { scn: "Base", mode: "pf", o: { sizing: "fixed", fixedGearing: 0.6, facility: 60000, drawdown: "eq1" } },
  "Equity-first drawdown (solved)": { scn: "Base", mode: "pf", o: { drawdown: "eq1" } },
  "No DSRA and no shareholder loan": { scn: "Base", mode: "pf", o: { dsraN: 0, shlPct: 0 } },
  "Straight-line profile 1 on the solved debt": { scn: "Base", mode: "pf", o: { repay: "p1" } },
  "Lender view: 2.50x target, 32 quarters": { scn: "Base", mode: "pf", o: { dscr: 2.5, tenor: 32 } },
};

// field value helpers
function fieldDefault(f) { return f.base ? f.base(baseP()) : f.def; }
function fieldValue(f) {
  const o = ST.o;
  if (f.t === "chg") return o[f.k] != null ? (o[f.k] - 1) * 100 : 0;
  if (o[f.k] !== undefined && o[f.k] !== null) return f.t === "pct" ? o[f.k] * 100 : o[f.k];
  const d = fieldDefault(f); return d == null ? "" : f.t === "pct" ? d * 100 : d;
}
function isChanged(f) { return ST.o[f.k] !== undefined && ST.o[f.k] !== null; }
function setField(f, raw) {
  if (f.t === "chk") { const v = raw; if (v === f.def) delete ST.o[f.k]; else ST.o[f.k] = v; return; }
  if (f.t === "sel") { const v = isNaN(+raw) ? raw : +raw; if (v === f.def) delete ST.o[f.k]; else ST.o[f.k] = v; return; }
  if (raw === "" || raw == null) { delete ST.o[f.k]; return; }
  let v = +raw; if (!isFinite(v)) return;
  const lim = LIMITS[f.k]; if (lim) { v = Math.min(lim[1], Math.max(lim[0], v)); if (lim[2]) v = Math.round(v); }
  if (f.t === "chg") { v = 1 + v / 100; if (Math.abs(v - 1) < 1e-12) { delete ST.o[f.k]; return; } }
  else if (f.t === "pct") v = v / 100;
  const d = fieldDefault(f); if (d != null && Math.abs(v - d) < 1e-12 && f.t !== "chg") { delete ST.o[f.k]; return; }
  ST.o[f.k] = v;
}

// ------------------------------------------------------------------------------------------------ compute
function recompute() {
  const op = effOpts();
  try { CUR = E.build(INP, ST.scn, op); } catch (err) { showFail(err); return; }
  const shared = { fareM: op.fareM, occM: op.occM, omM: op.omM, costM: op.costM, rateAdd: op.rateAdd, omSens: op.omSens, taxInt: op.taxInt, lossCF: op.lossCF, daysShort: op.daysShort, tax: op.tax, req: op.req, arDays: op.arDays, apDays: op.apDays, rate: op.rate };
  if (ST.mode === "start") { CURS = CUR; CURP = E.build(INP, ST.scn, Object.assign({}, shared, { mode: "pf" })); }
  else { CURP = CUR; CURS = E.build(INP, ST.scn, Object.assign({}, shared, { mode: "start", profile: 1 })); }
  saveHash(); renderAll();
}
const isCourseBase = () => Object.keys(ST.o).length === 0;
const isBaseCase = () => ST.scn === "Base" && Object.keys(ST.o).length === 0;
function showFail(err) { $("#p-" + TAB).innerHTML = `<div class="note warn" role="alert"><b>These inputs could not be calculated</b> (${esc(err && err.message || err)}). <button id="failReset">Reset all inputs</button></div>`; const b = $("#failReset"); if (b) b.onclick = () => { ST = clone(DEFSTATE); recompute(); }; $$("section.panel").forEach((p) => p.classList.toggle("on", p.id === "p-" + TAB)); syncSide(); renderTabs(); }

// ------------------------------------------------------------------------------------------------ side panel
function buildSide() {
  const s = $("#side");
  let h = `<a class="skip" href="#tabs">Skip to results</a><div id="clampNote" class="u" role="status" aria-live="polite"></div><div class="row"><div class="seg" id="modeSeg" role="group" aria-label="Model"><button data-m="start">Start model (Days 4 to 5)</button><button data-m="pf">Project finance (Days 6 to 7)</button></div></div>
  <div class="fld"><label for="scnSel">Scenario</label><select id="scnSel">${SCN.map((x) => `<option>${x}</option>`).join("")}</select></div>
  <div class="fld"><label for="preSel">Preset</label><select id="preSel"><option value="">Choose a preset...</option>${Object.keys(PRESETS).map((k) => `<option>${esc(k)}</option>`).join("")}</select></div>
  <div class="row"><button id="resetBtn" class="ghost">Reset all</button><button id="pinBtn" class="gold" title="Pin this run; KPIs then show the change from it">Pin run</button><button id="linkBtn" class="ghost" title="Copy a link that restores these inputs">Share link</button></div>
  <div class="row"><button id="expJson" class="ghost">Export inputs</button><button id="impJson" class="ghost">Import</button><input type="file" id="impFile" accept=".json" hidden></div>`;
  for (const g of FIELDS) {
    h += `<details class="grp" data-g="${esc(g.g)}" ${g.open ? "open" : ""}><summary>${esc(g.g)}</summary><div class="body">`;
    for (const f of g.items) {
      const id = "f_" + f.k;
      if (f.t === "chk") h += `<div class="fld"><label for="${id}" title="${esc(f.tip || "")}">${esc(f.label)}</label><input type="checkbox" id="${id}" data-k="${f.k}"></div>`;
      else if (f.t === "sel") h += `<div class="fld"><label for="${id}">${esc(f.label)}</label><select id="${id}" data-k="${f.k}">${f.opts.map(([v, l]) => `<option value="${v}">${esc(l)}</option>`).join("")}</select></div>`;
      else h += `<div class="fld" data-only="${f.only ? 1 : 0}"><label for="${id}" title="${esc(f.tip || "")}">${esc(f.label)} <span class="u">${esc(f.unit || "")}</span></label><input type="number" id="${id}" data-k="${f.k}" step="${f.step || "any"}" ${LIMITS[f.k] ? `min="${f.t === "chg" ? LIMITS[f.k][0] : LIMITS[f.k][0]}" max="${LIMITS[f.k][1]}"` : ""} inputmode="decimal"></div>`;
    }
    if (g.g.startsWith("Construction")) h += `<div class="fld"><label>Spend profile (8 quarters, % of hard cost)</label><span class="u" id="spendSum"></span></div><div id="spendBox" style="display:grid;grid-template-columns:repeat(4,1fr);gap:4px"></div>`;
    h += `</div></details>`;
  }
  h += `<div class="note" style="font-size:.76rem">Highlighted fields differ from the scenario value. Every change recomputes the full 84-quarter model in about a millisecond.</div>`;
  s.innerHTML = h;
  $$("#modeSeg button").forEach((b) => b.addEventListener("click", () => { ST.mode = b.dataset.m; recompute(); }));
  $("#scnSel").addEventListener("change", (e) => { ST.scn = e.target.value; recompute(); });
  $("#preSel").addEventListener("change", (e) => { const p = PRESETS[e.target.value]; if (p) { ST = clone(p); recompute(); } e.target.value = ""; });
  $("#resetBtn").addEventListener("click", () => { ST = clone(DEFSTATE); recompute(); });
  $("#pinBtn").addEventListener("click", () => { PIN = kpis(CUR); renderAll(); });
  $("#linkBtn").addEventListener("click", (e) => { saveHash(); copy(location.href, e.target); });
  $("#expJson").addEventListener("click", () => download("mipf_inputs.json", JSON.stringify(ST, null, 1), "application/json"));
  $("#impJson").addEventListener("click", () => $("#impFile").click());
  $("#impFile").addEventListener("change", (e) => { const f = e.target.files[0]; if (!f) return; f.text().then((t) => { try { const j = JSON.parse(t); if (!j || typeof j !== "object" || (j.scn === undefined && j.mode === undefined && j.o === undefined)) throw 0; ST = validateState(j); recompute(); } catch (er) { alert("Not a valid inputs file (expected a file exported with Export inputs)."); } e.target.value = ""; }); });
  s.addEventListener("input", (e) => {
    const k = e.target.dataset.k; if (!k) return;
    const f = FIELDS.flatMap((g) => g.items).find((x) => x.k === k); if (!f) return;
    setField(f, f.t === "chk" ? e.target.checked : e.target.value);
    clearTimeout(buildSide.t); buildSide.t = setTimeout(recompute, 120);
  });
  s.addEventListener("change", (e) => {
    const el = e.target, k = el.dataset && el.dataset.k, f = k && FIELDS.flatMap((g) => g.items).find((x) => x.k === k), typed = el.value;
    let msg = "";
    if (f && el.type === "number" && typed !== "" && LIMITS[f.k]) { const lim = LIMITS[f.k]; let v = +typed; const c = Math.min(lim[1], Math.max(lim[0], lim[2] ? Math.round(v) : v)); if (c !== v) msg = `Adjusted to ${c}: allowed range ${lim[0]} to ${lim[1]}${lim[2] ? " (whole numbers)" : ""}.`; }
    syncSide();
    $$(".clampmsg").forEach((n) => n.remove());
    if (msg && el.closest(".fld")) { const d = document.createElement("div"); d.className = "u clampmsg"; d.setAttribute("role", "status"); d.textContent = msg; el.closest(".fld").after(d); setTimeout(() => d.remove(), 6000); }
  });
  s.addEventListener("input", (e) => { if (e.target.dataset.sp != null) { const a = ST.o.spend ? ST.o.spend.slice() : baseP().spend.slice(); a[+e.target.dataset.sp] = (+e.target.value) / 100; ST.o.spend = a; clearTimeout(buildSide.t); buildSide.t = setTimeout(recompute, 120); } });
}
function syncSide() {
  $$("#modeSeg button").forEach((b) => { b.classList.toggle("on", b.dataset.m === ST.mode); b.setAttribute("aria-pressed", b.dataset.m === ST.mode); });
  $("#scnSel").value = ST.scn;
  for (const g of FIELDS) {
    const d = $(`details[data-g="${g.g}"]`); d.style.display = !g.mode || g.mode === ST.mode ? "" : "none";
    for (const f of g.items) {
      const el = $("#f_" + f.k); if (!el) continue;
      const row = el.closest(".fld"); row.style.display = f.only && !f.only() ? "none" : "";
      if (f.t === "chk") { el.checked = ST.o[f.k] !== undefined ? ST.o[f.k] : f.def; el.classList.toggle("chg", isChanged(f)); }
      else if (f.t === "sel") { el.value = String(ST.o[f.k] !== undefined ? ST.o[f.k] : f.def); el.classList.toggle("chg", isChanged(f)); }
      else if (document.activeElement !== el) { const v = fieldValue(f); el.value = v === "" ? "" : +(+v).toFixed(4); el.classList.toggle("chg", isChanged(f)); }
    }
  }
  const sp = ST.o.spend || baseP().spend; const box = $("#spendBox");
  if (box) { if (!box.children.length || box.dataset.n !== String(sp.length)) { box.dataset.n = sp.length; box.innerHTML = sp.map((v, i) => `<input type="number" data-sp="${i}" step="1" min="0" max="100" title="Quarter ${i + 1}" aria-label="Spend share, construction quarter ${i + 1}, percent">`).join(""); }
    $$("input", box).forEach((el, i) => { if (document.activeElement !== el) el.value = +(sp[i] * 100).toFixed(3); el.classList.toggle("chg", !!ST.o.spend); });
    const t = sum(sp); $("#spendSum").textContent = "sum " + (t * 100).toFixed(1) + "%"; $("#spendSum").style.color = Math.abs(t - 1) > 1e-6 ? "var(--bad)" : "var(--ok)"; }
}

// ------------------------------------------------------------------------------------------------ results helpers
function kpis(R) {
  if (R.mode === "pf") return { "Blended sponsor IRR (from COD)": [R.irr, "pct2"], "Sponsor IRR dated at contributions": [R.o.irrDated, "pct2"], "Blended NPV": [R.npv, "n0"], "Minimum DSCR": [R.o.minDSCR, "x2"], "Average DSCR": [R.o.avgDSCR, "x2"], "LLCR at COD": [R.o.llcrCOD, "x2"], "PLCR at COD": [R.o.plcrCOD, "x2"],
    "Gearing": [R.gearing, "pct2"], "Senior debt": [R.c.D, "n0"], "Sponsor funding": [R.c.E, "n0"], "Project cost": [R.U, "n0"], "Binding constraint": [R.binding, "raw"], "Peak DSRA": [R.o.maxDSRA, "n0"], "Total dividends": [R.o.sumDiv, "n0"] };
  return { "Shareholder XIRR": [R.irr, "pct2"], "Shareholder NPV": [R.npv, "n0"], "Project XIRR": [R.pirr, "pct2"], "Minimum DSCR": [R.minDSCR, "x2"], "Average DSCR": [R.avgDSCR, "x2"], "Total EBITDA": [sum(R.m.ebitda), "n0"], "Total CFADS": [sum(R.m.cfads), "n0"], "Total dividends": [sum(R.m.div), "n0"], "Senior debt": [R.m.D0, "n0"] };
}
const prettyDate = (iso) => (/^\d{4}-\d\d-\d\d$/.test(iso) ? FM.date(iso) : iso);
function paybackDate(R) {
  const fl = R.mode === "pf" ? R.o.flows : R.m.sh, i0 = R.mode === "pf" ? R.o.i0 : R.i0; let c = 0;
  for (let t = i0; t < N; t++) { c += fl[t]; if (c >= 0 && t > i0) return E.iso(R.m.end[t]); } return "not within the forecast";
}
function tokens() {
  const R = CURP, S = CURS, T = {};
  const base = R.mode === "pf" ? { U: R.U, D: R.c.D, E: R.c.E, g: R.gearing, cap: R.cap, binding: R.binding, irr: R.irr, npv: R.npv, minDSCR: R.o.minDSCR, avgDSCR: R.o.avgDSCR, llcr: R.o.llcrCOD, plcr: R.o.plcrCOD, maxDSRA: R.o.maxDSRA, sumDiv: R.o.sumDiv,
    shlInt: sum(R.o.paid), shlPrin: sum(R.o.sp), idc: sum(R.c.idc), cfee: sum(R.c.cfee), upfrontFee: sum(R.c.upfront), hardTotal: sum(R.c.spend), sh0: R.o.sh0, sc0: R.o.sc0 } : null;
  const st = { npv: S.npv, irr: S.irr, pirr: S.pirr, minDSCR: S.minDSCR, avgDSCR: S.avgDSCR, rev: sum(S.m.rev), cost: sum(S.m.cost), ebitda: sum(S.m.ebitda), dep: sum(S.m.dep), intr: sum(S.m.intr), pat: sum(S.m.pat), tax: sum(S.m.taxexp), cfads: sum(S.m.cfads), div: sum(S.m.div) };
  return { R: base, S: st };
}
function tokenText(key) {
  const op = effOpts(), TK = tokens();
  if (key.startsWith("R.")) { const k = key.slice(2); if (!TK.R) return "(n/a)"; const d = PB.tokens.R[k]; return d && TK.R[k] != null ? fmtv(TK.R[k], d.fmt) : null; }
  if (key.startsWith("S.")) { const k = key.slice(2), d = PB.tokens.S[k]; return d ? fmtv(TK.S[k], d.fmt) : null; }
  const mat = (() => { try { if (ST.mode === "start" && CUR && CUR.m) { let last = -1; CUR.m.rep.forEach((r, i) => { if (r > 1e-6) last = i; }); return last >= 0 ? FM.date(CUR.m.end[last]) : "the last repayment quarter"; } if (CURP && CURP.o) { const o = CURP.o, t = o.cnt.findIndex((c, i) => c === o.lastRep && CURP.m.fc[i] === 1); return t >= 0 ? FM.date(CURP.m.end[t]) : "the last repayment quarter"; } } catch (e) {} return "the last repayment quarter"; })();
  const names = { MATDATE: mat, OS: OS, drawdownName: op.drawdown === "eq1" ? "equity first" : "pro-rata", idcName: op.idc === "avg" ? "average balance (algebraic)" : "opening balance", repayName: { sculpt: "sculpted", p1: "profile 1", p2: "profile 2", p3: "profile 3", equal: "equal principal" }[op.repay],
    sizingName: op.sizing === "fixed" ? "fixed gearing" : "solved by Goal Seek", taxIntName: op.taxInt ? "interest deductible" : "interest not deducted (original error)", modeName: ST.mode === "pf" ? "project finance" : "start model" };
  if (names[key] != null) return names[key];
  if (key === "nca0") return ST.mode === "pf" ? FM.n0(CUR.U) + " (linked to Constr!F52)" : FM.n0(CUR.P.nca0);
  if (key === "gearing") return ST.mode === "pf" ? FM.pct2(CUR.gearing) : FM.pct2(CUR.P.gearing);
  if (key === "profile") return ST.mode === "pf" ? "4" : String(op.profile);
  if (key === "facility") return ST.mode === "pf" ? FM.n0(Math.round(CUR.cap)) : "n/a";
  const d = PB.tokens.P[key]; if (d && CUR.P[key] !== undefined) return fmtv(CUR.P[key], d.fmt);
  return null;
}
const resolveTokens = (t) => t.replace(/\{\{([A-Za-z0-9_.]+)\}\}/g, (m, k) => { const v = tokenText(k); return v == null ? m : v; });

// ------------------------------------------------------------------------------------------------ charts
const PAL = ["#141B4D", "#D99A2B", "#1C7293", "#7A8AA5", "#b3261e", "#1e7b34", "#0B5E82"];
function niceTicks(lo, hi, n) {
  if (!(hi > lo)) { hi = lo + 1; }
  const raw = (hi - lo) / n, mag = Math.pow(10, Math.floor(Math.log10(raw))), f = raw / mag, step = (f < 1.5 ? 1 : f < 3 ? 2 : f < 7 ? 5 : 10) * mag;
  const a = Math.floor(lo / step) * step, b = Math.ceil(hi / step) * step, t = []; for (let v = a; v <= b + step / 2; v += step) t.push(+v.toFixed(10)); return t;
}
function chart(o) {
  const W = o.w || 560, H = o.h || 230, m = { l: 52, r: 10, t: 10, b: 30 }, labels = o.labels, n = labels.length, series = o.series, stack = o.stack, bar = o.type === "bar";
  const yf = o.yfmt || FM.n0;
  let lo = Infinity, hi = -Infinity;
  if (stack) for (let i = 0; i < n; i++) { let p = 0, q = 0; series.forEach((s) => { const v = s.data[i] || 0; if (v >= 0) p += v; else q += v; }); hi = Math.max(hi, p); lo = Math.min(lo, q); }
  else series.forEach((s) => s.data.forEach((v) => { if (v != null && isFinite(v)) { hi = Math.max(hi, v); lo = Math.min(lo, v); } }));
  if (!isFinite(lo)) { lo = 0; hi = 1; } if (bar || stack || o.zero) lo = Math.min(lo, 0);
  const tk = niceTicks(lo, hi, 5); lo = tk[0]; hi = tk[tk.length - 1];
  const X = (i) => m.l + (bar ? ((i + 0.5) * (W - m.l - m.r)) / n : n === 1 ? (W - m.l - m.r) / 2 : (i * (W - m.l - m.r)) / (n - 1)), Y = (v) => m.t + (1 - (v - lo) / (hi - lo)) * (H - m.t - m.b);
  let s = `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(o.title || "chart")}">`;
  tk.forEach((t) => { s += `<line x1="${m.l}" x2="${W - m.r}" y1="${Y(t)}" y2="${Y(t)}" stroke="#d9e1ea" stroke-width="${t === 0 ? 1.2 : 0.6}"/><text x="${m.l - 4}" y="${Y(t) + 3}" text-anchor="end">${yf(t)}</text>`; });
  const every = Math.max(1, Math.ceil(n / (o.xticks || 10)));
  labels.forEach((l, i) => { if (i % every === 0) s += `<text x="${X(i)}" y="${H - 10}" text-anchor="middle">${esc(l)}</text>`; });
  const bw = bar ? Math.max(2, ((W - m.l - m.r) / n) * 0.7 / (stack ? 1 : series.length)) : 0;
  const pos = new Array(n).fill(0), neg = new Array(n).fill(0);
  series.forEach((sr, si) => {
    const col = sr.color || PAL[si % PAL.length];
    if (bar) sr.data.forEach((v, i) => { v = v || 0; let y0, y1; if (stack) { if (v >= 0) { y0 = pos[i]; pos[i] += v; y1 = pos[i]; } else { y0 = neg[i]; neg[i] += v; y1 = neg[i]; } } else { y0 = 0; y1 = v; }
      const x = stack ? X(i) - bw / 2 : X(i) - (bw * series.length) / 2 + si * bw; s += `<rect x="${x.toFixed(1)}" y="${Math.min(Y(y0), Y(y1)).toFixed(1)}" width="${bw.toFixed(1)}" height="${Math.max(0.5, Math.abs(Y(y0) - Y(y1))).toFixed(1)}" fill="${col}"><title>${esc(sr.name)} ${esc(labels[i])}: ${yf(v)}</title></rect>`; });
    else { let d = ""; sr.data.forEach((v, i) => { if (v == null || !isFinite(v)) return; d += (d ? "L" : "M") + X(i).toFixed(1) + " " + Y(v).toFixed(1); }); s += `<path d="${d}" fill="none" stroke="${col}" stroke-width="${sr.dash ? 1.4 : 2}" ${sr.dash ? 'stroke-dasharray="5 3"' : ""}/>`;
      if (n <= 40) sr.data.forEach((v, i) => { if (v != null && isFinite(v)) s += `<circle cx="${X(i).toFixed(1)}" cy="${Y(v).toFixed(1)}" r="2" fill="${col}"><title>${esc(sr.name)} ${esc(labels[i])}: ${yf(v)}</title></circle>`; }); }
  });
  s += "</svg><div class=\"legend\">" + series.map((sr, i) => `<span><i style="background:${sr.color || PAL[i % PAL.length]}"></i>${esc(sr.name)}</span>`).join("") + "</div>";
  return `<div class="card"><h3>${esc(o.title || "")}</h3>${s}</div>`;
}
const slice = (a, i0) => a.slice(i0);

// ------------------------------------------------------------------------------------------------ tables
function tbl(head, rows, opt) { opt = opt || {};
  return `<div class="scroll" style="${opt.max ? "max-height:" + opt.max : ""}"><table class="t"><thead><tr>${head.map((h) => `<th>${esc(h)}</th>`).join("")}</tr></thead><tbody>${rows.map((r) => `<tr class="${r.cls || ""}">${r.cells.map((c, i) => `<td class="${i === 0 ? "l" : ""}">${c}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`; }
const rawCell = (c) => { const t = String(c).replace(/<[^>]*>/g, "").replace(/&amp;/g, "&"); return /^-?[\d,]+(\.\d+)?$/.test(t) ? t.replace(/,/g, "") : t; };
const tcsv = (head, rows) => csv([head].concat(rows.map((r) => r.cells.map(rawCell))));

// annual aggregation
function groupYears(R, i0) { const ys = [], idx = []; for (let t = i0; t < N; t++) { const y = E.ymd(R.m.end[t])[0]; if (!ys.length || ys[ys.length - 1] !== y) { ys.push(y); idx.push([]); } idx[idx.length - 1].push(t); } return { ys, idx }; }
function statementRows(R) {
  const m = R.m, pf = R.mode === "pf", o = R.o, Z = new Array(N).fill(0), neg = (a) => a.map((v) => -v);
  const tot = (...as) => Z.map((_, t) => as.reduce((s, a) => s + a[t], 0));
  const R_ = [];
  const sec = (l) => R_.push({ sec: l }), row = (l, a, kind, cls) => R_.push({ l, a, kind: kind || "flow", cls });
  if (pf) {
    sec("INCOME STATEMENT"); row("Operating revenue", m.rev); row("Operating cost", neg(m.cost)); row("EBITDA", m.ebitda, "flow", "sub"); row("Accounting depreciation", neg(m.dep)); row("Senior debt interest", neg(o.intr)); row("Shareholder loan interest", neg(o.due));
    row("Profit before tax", o.pbt, "flow", "sub"); row("Tax expense", neg(o.taxexp)); row("Profit after tax", o.pat, "flow", "sub");
    sec("CASH FLOW"); row("Operating revenue received", m.rec); row("Operating cost paid", neg(m.paid)); row("Capital expenditure", neg(m.capex)); row("Tax paid", neg(o.taxpaid)); row("Cash flow available for debt service (CFADS)", o.cfads, "flow", "sub");
    row("Senior debt interest", neg(o.intr)); row("Senior debt principal", neg(o.prin)); row("Cash flow available to shareholders", o.cf42, "flow", "sub"); row("DSRA (funding) / release", o.rel.map((v, t) => v - o.fund[t])); row("Shareholder loan interest paid", neg(o.paid));
    row("Shareholder loan principal repaid", neg(o.sp)); row("Share capital redemption", neg(o.red)); row("Cash flow available for dividends", o.cfdiv, "flow", "sub"); row("Dividends declared and paid", neg(o.div)); row("Net cash flow", o.cfdiv.map((v, t) => v - o.div[t]), "flow", "sub");
    sec("BALANCE SHEET"); row("Non-current assets", m.nca, "bal"); row("Receivables", m.ar, "bal"); row("Retained cash", o.rcash, "bal"); row("DSRA balance", o.dsra, "bal"); row("Total assets", tot(m.nca, m.ar, o.rcash, o.dsra), "bal", "sub");
    row("Payables", m.ap, "bal"); row("Senior debt", o.bal, "bal"); row("Deferred tax", o.dtax, "bal"); row("Shareholder loan", o.shl, "bal"); row("Share capital", o.sc, "bal"); row("Retained earnings", o.re, "bal"); row("Total liabilities and shareholder funds", tot(m.ap, o.bal, o.dtax, o.shl, o.sc, o.re), "bal", "sub");
    row("Balance sheet check (assets less liabilities)", o.chk, "bal");
  } else {
    sec("INCOME STATEMENT"); row("Operating revenue", m.rev); row("Operating cost", neg(m.cost)); row("EBITDA", m.ebitda, "flow", "sub"); row("Accounting depreciation", neg(m.dep)); row("Senior debt interest", neg(m.intr)); row("Profit before tax", m.pbt, "flow", "sub"); row("Tax expense", neg(m.taxexp)); row("Profit after tax", m.pat, "flow", "sub");
    sec("CASH FLOW"); row("Operating revenue received", m.rec); row("Operating cost paid", neg(m.paid)); row("Capital expenditure", neg(m.capex)); row("Tax paid", neg(m.taxpaid)); row("CFADS", m.cfads, "flow", "sub"); row("Senior debt interest", neg(m.intr)); row("Senior debt principal", neg(m.rep));
    row("Share capital redemption", neg(m.red)); row("Dividends declared and paid", neg(m.div)); row("Net cash flow", m.cfads.map((v, t) => v - m.intr[t] - m.rep[t] - m.red[t] - m.div[t]), "flow", "sub");
    sec("BALANCE SHEET"); row("Non-current assets", m.nca, "bal"); row("Receivables", m.ar, "bal"); row("Retained cash", m.rcash, "bal"); row("Total assets", tot(m.nca, m.ar, m.rcash), "bal", "sub"); row("Payables", m.ap, "bal"); row("Senior debt", m.debt, "bal"); row("Deferred tax", R.dtax, "bal");
    row("Share capital", m.sc, "bal"); row("Retained earnings", m.re, "bal"); row("Total liabilities and shareholder funds", tot(m.ap, m.debt, R.dtax, m.sc, m.re), "bal", "sub");
  }
  return R_;
}
function stmtTable(R, view) {
  const i0 = R.mode === "pf" ? R.o.i0 : R.i0, rows = statementRows(R); let head, cols;
  if (view === "annual") { const g = groupYears(R, i0); head = ["US$ 000s"].concat(g.ys.map(String)); cols = g.idx; }
  else { head = ["US$ 000s"].concat(Array.from({ length: N - i0 }, (_, k) => dshort(R.m.end[i0 + k]))); cols = Array.from({ length: N - i0 }, (_, k) => [i0 + k]); }
  const out = rows.map((r) => r.sec ? { cls: "sec", cells: [r.sec].concat(cols.map(() => "")) } : { cls: r.cls || "", cells: [esc(r.l)].concat(cols.map((ix) => FM.n0(r.kind === "bal" ? r.a[ix[ix.length - 1]] : sum(ix.map((t) => r.a[t]))))) });
  return { head, rows: out };
}

// ------------------------------------------------------------------------------------------------ panels
const TABS = [["summary", "Summary"], ["construction", "Construction"], ["statements", "Statements"], ["debt", "Debt and cover"], ["scenarios", "Scenarios and sensitivity"], ["prompts", "Prompt studio"], ["atlas", "Formula atlas"], ["verify", "Verify"], ["guide", "Guide"]];
function renderTabs() {
  const nav = $("#tabs");
  if (!nav.children.length) {
    nav.setAttribute("role", "tablist"); nav.setAttribute("aria-label", "Results");
    nav.innerHTML = TABS.map(([k, l]) => `<button role="tab" id="tab-${k}" data-t="${k}" aria-controls="p-${k}">${l}</button>`).join("");
    $$("#tabs button").forEach((b) => { b.addEventListener("click", () => { TAB = b.dataset.t; renderAll(); b.focus(); });
      b.addEventListener("keydown", (e) => { const ks = TABS.map((t) => t[0]), i = ks.indexOf(b.dataset.t); let j = -1; if (e.key === "ArrowRight") j = (i + 1) % ks.length; else if (e.key === "ArrowLeft") j = (i + ks.length - 1) % ks.length; else if (e.key === "Home") j = 0; else if (e.key === "End") j = ks.length - 1; if (j >= 0) { e.preventDefault(); TAB = ks[j]; renderAll(); $("#tab-" + ks[j]).focus(); } }); });
    $$("section.panel").forEach((p) => { p.setAttribute("role", "tabpanel"); p.setAttribute("aria-labelledby", "tab-" + p.id.slice(2)); });
  }
  $$("#tabs button").forEach((b) => { const on = b.dataset.t === TAB; b.classList.toggle("on", on); b.setAttribute("aria-selected", on); b.tabIndex = on ? 0 : -1; });
}
function renderAll() {
  syncSide(); renderTabs();
  $$("section.panel").forEach((p) => p.classList.toggle("on", p.id === "p-" + TAB));
  ({ summary: pSummary, construction: pConstruction, statements: pStatements, debt: pDebt, scenarios: pScenarios, prompts: pPrompts, atlas: pAtlas, verify: pVerify, guide: pGuide })[TAB]();
}
function banner() {
  const op = effOpts(), parts = [`<b>${ST.mode === "pf" ? "Project finance model" : "Start model"}</b>`, `scenario <b>${ST.scn}</b>`];
  if (Object.keys(ST.o).length) parts.push(`<b>${Object.keys(ST.o).length}</b> input(s) changed`); else parts.push("course inputs");
  const ck = E.checks(CUR), bad = ck.filter((c) => !c.ok);
  const sp = ST.o.spend ? sum(ST.o.spend) : 1, spendWarn = ST.mode === "pf" && Math.abs(sp - 1) > 1e-6 ? `<span class="pill bad">spend profile sums to ${(sp * 100).toFixed(1)}%, not 100%</span> ` : "";
  const lim = "";
  const wr = E.warnings(CUR), wrHtml = wr.length ? `<ul class="warnlist">${wr.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>` : "";
  return `<div class="note" aria-live="polite">${spendWarn}${lim}${parts.join(" &middot; ")} &middot; checks: ${bad.length ? `<span class="pill bad">${bad.length} failing</span>` : '<span class="pill ok">ALL CHECKS PASSED</span>'} ${isCourseBase() ? "" : '&middot; <i>inputs differ from the course case, so values differ from the course checkpoints</i>'}${wrHtml}</div>`;
}
function headline(R) {
  const m = R.m, ck = E.checks(R);
  if (ck.some((c) => !c.ok)) return `<div class="card headline"><h3>In one paragraph</h3><p>The summary is not shown because an integrity check fails for these inputs. See the checks below and the warnings above.</p></div>`;
  if (R.mode !== "pf") {
    const pb = prettyDate(paybackDate(R)), prof = ["", "7.5-year", "10-year", "15-year"][effOpts().profile];
    const cover = R.minDSCR < 1 ? `Debt service is <b>not covered</b> in the weakest quarter (minimum DSCR <b>${FM.x2(R.minDSCR)}</b>).` : `The ${FM.n0(m.D0)} senior loan is covered at a minimum of <b>${FM.x2(R.minDSCR)}</b> (average ${FM.x2(R.avgDSCR)}) with the ${prof} straight-line profile.`;
    return `<div class="card headline"><h3>In one paragraph</h3><p>The shareholders put in ${FM.n0(m.sc0)} and receive ${FM.n0(sum(m.div) + sum(m.red))} over 20 years: a shareholder XIRR of <b>${FM.pct2(R.irr)}</b> against the ${FM.pct2(R.P.req)} they require, an NPV of <b>${FM.n0(R.npv)}</b> and payback by <b>${esc(pb)}</b>. ${cover} ${R.npv < 0 ? "The shareholders do <b>not</b> earn their required return." : "The shareholders earn more than their required return."}</p></div>`;
  }
  const o = R.o, op = effOpts(); let fz = "";
  try {
    const base = Object.assign({}, op, { lossCF: true, frozen: null }), f = E.build(INP, ST.scn, base);
    const be = E.breakeven(INP, ST.scn, base, 1.2), q = o.minDSCR;
    const dn = ST.scn === "Base" ? E.build(INP, "Downside", Object.assign({}, base, { frozen: f })) : null;
    const cases = [];
    if (dn) cases.push(`on this fixed financing the Downside gives a minimum cover of <b>${FM.x2(dn.o.minDSCR)}</b> in the weakest quarter (<b>${FM.x2(dn.o.minDSCR12)}</b> on a rolling 12-month basis, losses carried forward)`);
    if (q <= 1.2) cases.push(`the case itself is <b>already at or below the 1.20x lock-up</b> in its weakest quarter`);
    else if (isFinite(be)) cases.push(`the quarterly minimum reaches the 1.20x lock-up when fares are <b>${((1 - be) * 100).toFixed(1)}% below</b> the case`);
    else cases.push("cover stays above the 1.20x lock-up for every fare level tested");
    fz = " " + cases[0].charAt(0).toUpperCase() + cases[0].slice(1) + (cases.length > 1 ? ", and " + cases.slice(1).join(", and ") : "") + ".";
  } catch (e) {}
  const lead = `Lenders can lend <b>${FM.n0(R.c.D)}</b> against a project cost of ${FM.n0(R.U)} (<b>${FM.pct1(R.gearing)}</b> gearing; ${R.binding === "Fixed gearing" ? "the gearing is fixed by input" : `${R.binding === "Gearing" ? "the <b>gearing cap</b> sets the size" : `the <b>${esc(R.binding)}</b> test sets the size`}`}). The sponsors fund ${FM.n0(R.c.E)} and earn a blended IRR of <b>${FM.pct2(R.irr)}</b> measured from COD, or <b>${FM.pct2(o.irrDated)}</b> when each contribution is dated when it is paid. Minimum DSCR is <b>${FM.x2(o.minDSCR)}</b> (LLCR ${FM.x2(o.llcrCOD)}).`;
  return `<div class="card headline"><h3>In one paragraph</h3><p>${lead}${fz}</p></div>`;
}
function pSummary() {
  const R = CUR, K = kpis(R), p = $("#p-summary");
  let h = banner() + headline(R) + '<div class="kpis">';
  for (const [k, [v, f]] of Object.entries(K)) {
    let delta = ""; if (PIN && PIN[k] && typeof v === "number") { const d = v - PIN[k][0]; if (Math.abs(d) > 1e-9) delta = `<small>${d > 0 ? "+" : ""}${f.startsWith("pct") ? (d * 100).toFixed(2) + " pts" : f.startsWith("x") ? d.toFixed(2) + "x" : FM.n0(d)} vs pinned</small>`; }
    const warn = (k === "Minimum DSCR" && v < 1.2) || (k.includes("NPV") && v < 0);
    h += `<div class="kpi ${warn ? "warn" : ""}"><small>${esc(k)}</small><b>${fmtv(v, f)}</b>${delta}</div>`;
  }
  h += `<div class="kpi"><small>Sponsor payback</small><b style="font-size:1.05rem">${esc(prettyDate(paybackDate(R)))}</b></div></div>`;
  h += '<div class="grid2">';
  if (R.mode === "pf") {
    const o = R.o, i0 = o.i0, lab = (a) => a.map((d) => dshort(d));
    h += chart({ title: "Sources of funds in construction (US$ 000s)", labels: lab(R.c.ends), type: "bar", stack: true, series: [{ name: "Equity", data: R.c.eq, color: "#D99A2B" }, { name: "Senior debt", data: R.c.debt, color: "#141B4D" }] });
    h += chart({ title: "CFADS and senior debt service (US$ 000s)", labels: lab(slice(R.m.end, i0 + 1)), series: [{ name: "CFADS", data: slice(o.cfads, i0 + 1), color: "#141B4D" }, { name: "Debt service", data: slice(o.DS, i0 + 1), color: "#D99A2B" }] });
    h += chart({ title: "DSCR by quarter", labels: lab(slice(R.m.end, i0 + 1)), yfmt: FM.x2, zero: true, series: [{ name: "DSCR", data: slice(o.dscrT, i0 + 1).map((v, k) => (o.DS[i0 + 1 + k] > 1e-3 ? v : null)), color: "#0B5E82" }, { name: "Target", data: new Array(N - i0 - 1).fill(R.op.dscr != null ? R.op.dscr : R.P.dscr), color: "#b3261e", dash: true }] });
    h += chart({ title: "Balances: senior debt, DSRA, shareholder loan", labels: lab(slice(R.m.end, i0)), series: [{ name: "Senior debt", data: slice(o.bal, i0), color: "#141B4D" }, { name: "DSRA", data: slice(o.dsra, i0), color: "#D99A2B" }, { name: "Shareholder loan", data: slice(o.shl, i0), color: "#1C7293" }] });
    const g = groupYears(R, i0 + 1);
    h += chart({ title: "Dividends and sponsor cash by year (US$ 000s)", labels: g.ys.map(String), type: "bar", series: [{ name: "Dividends", data: g.idx.map((ix) => sum(ix.map((t) => o.div[t]))), color: "#1C7293" }, { name: "Loan interest + principal + redemption", data: g.idx.map((ix) => sum(ix.map((t) => o.paid[t] + o.sp[t] + o.red[t]))), color: "#D99A2B" }] });
    let c = 0; const cum = []; for (let t = i0; t < N; t++) { c += o.flows[t]; cum.push(c); }
    h += chart({ title: "Cumulative blended sponsor cash flow (US$ 000s)", labels: lab(slice(R.m.end, i0)), zero: true, series: [{ name: "Cumulative", data: cum, color: "#1e7b34" }] });
  } else {
    const m = R.m, i0 = R.i0, g = groupYears(R, i0 + 1), lab = (a) => a.map((d) => dshort(d));
    h += chart({ title: "Revenue and EBITDA by year (US$ 000s)", labels: g.ys.map(String), type: "bar", series: [{ name: "Revenue", data: g.idx.map((ix) => sum(ix.map((t) => m.rev[t]))), color: "#0B5E82" }, { name: "EBITDA", data: g.idx.map((ix) => sum(ix.map((t) => m.ebitda[t]))), color: "#D99A2B" }] });
    h += chart({ title: "CFADS and debt service by quarter", labels: lab(slice(m.end, i0 + 1)), series: [{ name: "CFADS", data: slice(m.cfads, i0 + 1), color: "#141B4D" }, { name: "Debt service", data: slice(R.ds, i0 + 1), color: "#D99A2B" }] });
    h += chart({ title: "DSCR by quarter", labels: lab(slice(m.end, i0 + 1)), yfmt: FM.x2, zero: true, series: [{ name: "DSCR", data: slice(R.dscrT, i0 + 1).map((v, k) => (R.ds[i0 + 1 + k] > 1e-3 ? v : null)), color: "#0B5E82" }] });
    h += chart({ title: "Senior debt balance (US$ 000s)", labels: lab(slice(m.end, i0)), series: [{ name: "Debt", data: slice(m.debt, i0), color: "#141B4D" }] });
    h += chart({ title: "Dividends by year (US$ 000s)", labels: g.ys.map(String), type: "bar", series: [{ name: "Dividends", data: g.idx.map((ix) => sum(ix.map((t) => m.div[t]))), color: "#1C7293" }] });
  }
  h += `<div class="card"><h3>Integrity checks</h3><ul class="checks">${E.checks(R).map((c) => `<li><span>${esc(c.name)}</span><span><span class="pill ${c.ok ? "ok" : "bad"}">${c.ok ? "OK" : "FAIL"}</span> <span class="mono">${c.value.toExponential(1)}</span></span></li>`).join("")}</ul></div></div>`;
  h += `<div class="row noprint"><button id="exRes">Export results (JSON)</button><button id="exKpi" class="ghost">Export KPIs (CSV)</button><button id="exPdf" class="ghost">Print or save as PDF</button></div>`;
  p.innerHTML = h;
  $("#exRes").onclick = () => download("mipf_results.json", JSON.stringify({ state: ST, kpis: Object.fromEntries(Object.entries(K).map(([k, [v]]) => [k, v])), tokens: tokens() }, null, 1), "application/json");
  $("#exKpi").onclick = () => download("mipf_kpis.csv", csv([["KPI", "Value"]].concat(Object.entries(K).map(([k, [v, f]]) => [k, typeof v === "number" ? v : v]))), "text/csv");
  $("#exPdf").onclick = () => window.print();
}
function pConstruction() {
  const p = $("#p-construction");
  if (CUR.mode !== "pf") { p.innerHTML = banner() + '<div class="note warn">Construction applies to the project-finance model (Days 6 and 7). Switch to <b>Project finance</b> in the left panel.</div>'; return; }
  const c = CUR.c, head = ["US$ 000s"].concat(c.ends.map(dshort), ["Total"]);
  const r = (l, a, cls) => ({ cls, cells: [l].concat(a.map(FM.n1), [FM.n1(sum(a))]) });
  const rows = [r("Days in quarter", c.days.map((d) => d), ""), r("Hard cost spend", c.spend), r("Upfront fee", c.upfront), r("Interest during construction (IDC)", c.idc), r("Commitment fee", c.cfee), r("Total uses of funds", c.uses, "sub"), r("Equity drawdown", c.eq), r("Senior debt drawdown", c.debt), r("Total sources of funds", c.eq.map((v, i) => v + c.debt[i]), "sub"), r("Sources less uses (check)", c.uses.map((u, i) => c.eq[i] + c.debt[i] - u))];
  rows[0].cells = ["Days in quarter"].concat(c.days.map(String), [String(sum(c.days))]); rows.push({ cells: ["Senior debt balance END"].concat(c.bal.map(FM.n1), [""]) });
  p.innerHTML = banner() + `<div class="kpis"><div class="kpi"><small>Project cost at COD</small><b>${FM.n1(c.U)}</b></div><div class="kpi"><small>Senior debt at COD</small><b>${FM.n1(c.D)}</b></div><div class="kpi"><small>Sponsor funding</small><b>${FM.n1(c.E)}</b></div><div class="kpi"><small>IDC + fees</small><b>${FM.n1(sum(c.idc) + sum(c.cfee) + sum(c.upfront))}</b></div><div class="kpi"><small>Gearing</small><b>${FM.pct2(c.D / c.U)}</b></div></div>` +
    '<div class="card"><h3>Constr sheet by quarter</h3>' + tbl(head, rows) + `</div><div class="grid2" style="margin-top:10px">` +
    chart({ title: "Uses of funds by quarter", labels: c.ends.map(dshort), type: "bar", stack: true, series: [{ name: "Hard cost", data: c.spend, color: "#141B4D" }, { name: "Upfront fee", data: c.upfront, color: "#7A8AA5" }, { name: "IDC", data: c.idc, color: "#D99A2B" }, { name: "Commitment fee", data: c.cfee, color: "#1C7293" }] }) +
    chart({ title: "Senior debt balance during construction", labels: c.ends.map(dshort), series: [{ name: "Debt", data: c.bal, color: "#141B4D" }] }) + `</div><div class="row noprint"><button id="exC">Download CSV</button></div>`;
  $("#exC").onclick = () => download("mipf_construction.csv", tcsv(head, rows), "text/csv");
}
function pStatements() {
  const p = $("#p-statements"), t = stmtTable(CUR, STMT_VIEW);
  p.innerHTML = banner() + `<div class="row noprint"><div class="seg"><button data-v="annual" aria-pressed="${STMT_VIEW === "annual"}" class="${STMT_VIEW === "annual" ? "on" : ""}">Annual</button><button data-v="quarterly" aria-pressed="${STMT_VIEW === "quarterly"}" class="${STMT_VIEW === "quarterly" ? "on" : ""}">Quarterly (J to CO)</button></div><button id="exS">Download CSV</button></div><div class="card">${tbl(t.head, t.rows)}</div>`;
  $$("button[data-v]", p).forEach((b) => (b.onclick = () => { STMT_VIEW = b.dataset.v; pStatements(); }));
  $("#exS").onclick = () => download("mipf_statements_" + STMT_VIEW + ".csv", tcsv(t.head, t.rows), "text/csv");
}
function pDebt() {
  const p = $("#p-debt"), R = CUR;
  if (R.mode !== "pf") {
    const m = R.m, i0 = R.i0, head = ["Quarter ending", "CFADS", "Interest", "Principal", "Debt service", "DSCR", "Debt balance"], rows = [];
    for (let t = i0 + 1; t < N; t++) if (R.ds[t] > 1e-3 || m.debt[t] > 0.001) rows.push({ cells: [dshort(m.end[t]), FM.n1(m.cfads[t]), FM.n1(m.intr[t]), FM.n1(m.rep[t]), FM.n1(R.ds[t]), R.ds[t] > 1e-3 ? FM.x2(R.dscrT[t]) : "", FM.n1(m.debt[t])] });
    p.innerHTML = banner() + `<div class="card"><h3>Senior debt and DSCR (start model)</h3>${tbl(head, rows, { max: "65vh" })}</div><div class="row noprint"><button id="exD">Download CSV</button></div>`; $("#exD").onclick = () => download("mipf_debt.csv", tcsv(head, rows), "text/csv"); return;
  }
  const o = R.o, i0 = o.i0, head = ["Quarter ending", "CFADS", "Interest", "Principal", "Debt service", "DSCR", "Senior balance", "LLCR", "PLCR", "DSRA target", "DSRA balance", "SHL balance", "SHL interest paid", "Dividends"], rows = [];
  for (let t = i0; t < N; t++) { if (t > i0 && o.DS[t] < 1e-3 && o.bal[t - 1] < 1e-3 && o.shl[t] < 1e-3 && o.div[t] < 1e-3 && R.m.fc[t] === 0) continue;
    rows.push({ cls: t === i0 ? "sub" : "", cells: [dshort(R.m.end[t]) + (t === i0 ? " (COD)" : ""), FM.n1(o.cfads[t]), FM.n1(o.intr[t]), FM.n1(o.prin[t]), FM.n1(o.DS[t]), o.DS[t] > 1e-3 ? FM.x2(o.dscrT[t]) : "", FM.n1(o.bal[t]), o.llcr[t] ? FM.x2(o.llcr[t]) : "", o.plcr[t] ? FM.x2(o.plcr[t]) : "", FM.n1(o.tgt[t]), FM.n1(o.dsra[t]), FM.n1(o.shl[t]), FM.n1(o.paid[t]), FM.n1(o.div[t])] }); }
  p.innerHTML = banner() + `<div class="kpis"><div class="kpi"><small>Debt capacity at COD</small><b>${FM.n1(R.cap)}</b></div><div class="kpi"><small>Debt size</small><b>${FM.n1(R.c.D)}</b></div><div class="kpi"><small>Binding constraint</small><b>${R.binding}</b></div><div class="kpi"><small>DSCR delivered at sizing</small><b>${FM.x4(o.dscrAct)}</b></div><div class="kpi"><small>Min / avg DSCR</small><b style="font-size:1.1rem">${FM.x2(o.minDSCR)} / ${FM.x2(o.avgDSCR)}</b></div><div class="kpi"><small>LLCR / PLCR at COD</small><b style="font-size:1.1rem">${FM.x2(o.llcrCOD)} / ${FM.x2(o.plcrCOD)}</b></div></div><div class="card"><h3>Debt schedule, cover ratios, DSRA and shareholder loan</h3>${tbl(head, rows, { max: "62vh" })}</div><div class="row noprint"><button id="exD">Download CSV</button></div>`;
  $("#exD").onclick = () => download("mipf_debt_and_cover.csv", tcsv(head, rows), "text/csv");
}
function runScenario(scn, extra) { return E.build(INP, scn, Object.assign({}, effOpts(), extra || {})); }
const SHOCKS = { pf: [["Fare -10%", { fareM: 0.9 }], ["Fare +10%", { fareM: 1.1 }], ["Occupancy -10%", { occM: 0.9 }], ["O&M +10%", { omM: 1.1 }], ["O&M -10%", { omM: 0.9 }], ["All operating cost +10%", { costM: 1.1 }], ["Interest +1 pt", { rateAdd: 0.01 }], ["Interest -1 pt", { rateAdd: -0.01 }], ["Hard cost +10%", { hard: 1.1 }], ["Hard cost -10%", { hard: 0.9 }], ["Target DSCR +0.25x", { dscr: 0.25 }], ["Target DSCR -0.25x", { dscr: -0.25 }]],
  start: [["Fare -10%", { fareM: 0.9 }], ["Fare +10%", { fareM: 1.1 }], ["Occupancy -10%", { occM: 0.9 }], ["O&M +10%", { omM: 1.1 }], ["All operating cost +10%", { costM: 1.1 }], ["Interest +1 pt", { rateAdd: 0.01 }], ["Interest -1 pt", { rateAdd: -0.01 }]] };
function shock(extra) { const e = Object.assign({}, extra), op = effOpts();
  if (e.fareM) e.fareM = op.fareM * e.fareM; if (e.occM) e.occM = op.occM * e.occM; if (e.omM) e.omM = op.omM * e.omM; if (e.costM) e.costM = op.costM * e.costM;
  if (e.hard) e.hard = (op.hard != null ? op.hard : baseP().hard) * e.hard; if (e.dscr) e.dscr = (op.dscr != null ? op.dscr : baseP().dscr) + e.dscr; if (e.rateAdd) e.rateAdd = (op.rateAdd || 0) + e.rateAdd; return e; }
function pScenarios() {
  const p = $("#p-scenarios"), pf = ST.mode === "pf", rows = [];
  const hd = pf ? ["Scenario", "Project cost", "Senior debt", "Sponsor funding", "Gearing", "Binding", "Min DSCR", "LLCR", "Blended IRR", "NPV"] : ["Scenario", "Shareholder NPV", "Shareholder XIRR", "Project XIRR", "Min DSCR", "Total EBITDA", "Total dividends"];
  for (const s of SCN) { const r = runScenario(s); rows.push({ cls: s === ST.scn ? "sub" : "", cells: pf ? [s, FM.n0(r.U), FM.n0(r.c.D), FM.n0(r.c.E), FM.pct2(r.gearing), r.binding, FM.x2(r.o.minDSCR), FM.x2(r.o.llcrCOD), FM.pct2(r.irr), FM.n0(r.npv)] : [s, FM.n1(r.npv), FM.pct2(r.irr), FM.pct2(r.pirr), FM.x2(r.minDSCR), FM.n0(sum(r.m.ebitda)), FM.n0(sum(r.m.div))] }); }
  const base = CUR, bm = pf ? base.irr : base.irr, bd = pf ? base.o.minDSCR : base.minDSCR;
  const tor = SHOCKS[ST.mode].map(([n, e]) => { const r = runScenario(ST.scn, shock(e)); return { n, irr: r.irr, d: pf ? r.o.minDSCR : r.minDSCR, D: pf ? r.c.D : r.m.D0, npv: r.npv }; });
  const tmax = Math.max(...tor.map((t) => Math.abs(t.irr - bm)), 1e-9);
  const trow = tor.map((t) => ({ cells: [esc(t.n), FM.pct2(t.irr), (t.irr - bm >= 0 ? "+" : "") + ((t.irr - bm) * 100).toFixed(2) + " pts", `<svg width="130" height="12" aria-hidden="true"><rect x="${t.irr >= bm ? 65 : 65 - 62 * Math.abs(t.irr - bm) / tmax}" y="1" width="${62 * Math.abs(t.irr - bm) / tmax}" height="10" fill="${t.irr >= bm ? "#1e7b34" : "#b3261e"}"/><line x1="65" x2="65" y1="0" y2="12" stroke="#888"/></svg>`, FM.x2(t.d), FM.n0(t.D), FM.n0(t.npv)] }));
  let frz = "";
  if (pf) {
    const op0 = effOpts(), cases = [["Downside", "Downside", {}], ["Upside", "Upside", {}], ["Fare -10%", ST.scn, { fareM: 0.9 }], ["Fare -15%", ST.scn, { fareM: 0.85 }], ["Fare -20%", ST.scn, { fareM: 0.8 }], ["O&M +20%", ST.scn, { omM: 1.2 }]].filter((c) => c[1] !== ST.scn || c[2].fareM || c[2].omM);
    const ref = CUR, refL = E.build(INP, ST.scn, Object.assign({}, op0, { lossCF: true }));
    const rows2 = cases.map(([n, sc, e]) => { const o1 = Object.assign({}, op0, { frozen: ref }, e.fareM ? { fareM: op0.fareM * e.fareM } : {}, e.omM ? { omM: op0.omM * e.omM } : {}), o2 = Object.assign({}, o1, { lossCF: true, frozen: refL });
      const a = E.build(INP, sc, o1), b = E.build(INP, sc, o2); const bad = b.o.minDSCR < 1.2;
      const neg = Math.min(...b.o.rcash.slice(b.o.i0)) < -1e-3, stressed = b.o.minDSCR12 < 1.2; return { cells: [esc(n), `<span class="${a.o.minDSCR < 1.2 ? "bad" : ""}">${FM.x2(a.o.minDSCR)}</span>`, `<span class="${bad ? "bad" : ""}">${FM.x2(b.o.minDSCR)}</span>`, `<span class="${stressed ? "bad" : ""}">${FM.x2(b.o.minDSCR12)}</span>`, FM.x2(b.o.avgDSCR), FM.x2(b.o.llcrCOD), `${FM.pct2(b.irr)}${stressed || neg ? " *" : ""}`] }; });
    const be = (t, l, basis) => { const v = E.breakeven(INP, ST.scn, Object.assign({}, op0, { lossCF: l }), t, basis); return isFinite(v) ? ((1 - v) * 100).toFixed(1) + "% below" : "n/a"; };
    frz = `<div class="card" style="margin-top:10px"><h3>Debt sized once: cases tested on the FIXED ${ST.scn} financing</h3><p class="u" style="font-size:.82rem">Debt size and the sculpted schedule are frozen at the current run; cash flow, tax and cover are recomputed. This is what a credit committee reads. Red = below the usual 1.20x lock-up.</p>${tbl(["Case", "Min DSCR, quarter (tax refund)", "Min DSCR, quarter (carry-forward)", "Min DSCR, rolling 12 months (carry-forward)", "Average DSCR", "LLCR at COD", "Blended IRR from COD"], rows2)}<p class="note">Breakeven fare (carry-forward). <b>Single-quarter</b> minimum DSCR: 1.20x at a fare <b>${be(1.2, true)}</b> the scenario, 1.00x at <b>${be(1.0, true)}</b>. <b>Rolling 12-month</b> (the usual covenant basis): 1.20x at <b>${be(1.2, true, "r12")}</b>, 1.00x at <b>${be(1.0, true, "r12")}</b>. With tax refunds, quarter: ${be(1.2, false)} and ${be(1.0, false)}. * IRRs marked * ignore lock-up and default consequences (the model has none) and may rest on negative cash: indicative only. The re-solved Downside above looks safer only because the lenders have already lent less.</p></div>`;
  }
  p.innerHTML = banner() + `<div class="card"><h3>The three scenarios${pf ? " (each re-solved: gearing found so that debt drawn equals debt sized)" : ""}</h3>${tbl(hd, rows)}</div>` +
    `<div class="card" style="margin-top:10px"><h3>One-way sensitivities around the current run (${pf ? "each fully re-solved" : "start model"})</h3>${tbl(["Shock", pf ? "Blended IRR" : "XIRR", "Change", "", "Min DSCR", pf ? "Debt" : "Debt (initial)", "NPV"], trow)}<p class="note">Fare and occupancy shocks are equivalent because revenue = fare x passengers.</p></div>` +
    frz + (pf ? `<div class="card" style="margin-top:10px"><h3>Structure grid: target DSCR x tenor (current inputs otherwise)</h3><div class="row noprint"><button id="gridBtn">Compute grid (12 solves)</button><button id="gridCsv" class="ghost">Download CSV</button></div><div id="gridOut"></div></div>` : "");
  if (pf) { let G = null; $("#gridBtn").onclick = () => { G = []; const ds = [1.75, 2.0, 2.25, 2.5], ts = [32, 40, 48]; ds.forEach((d) => ts.forEach((t) => { const r = runScenario(ST.scn, { dscr: d, tenor: t }); G.push({ d, t, D: r.c.D, g: r.gearing, md: r.o.minDSCR, irr: r.irr, b: r.binding }); }));
      const hi = Math.max(...G.map((x) => x.irr)), lo = Math.min(...G.map((x) => x.irr)); const col = (v) => `hsl(${40 + 80 * ((v - lo) / (hi - lo || 1))},70%,${85 - 15 * ((v - lo) / (hi - lo || 1))}%)`;
      $("#gridOut").innerHTML = tbl(["Target DSCR", "Tenor (quarters)", "Debt", "Gearing", "Binding", "Min DSCR", "Blended IRR"], G.map((x) => ({ cells: [FM.x2(x.d), x.t, FM.n0(x.D), FM.pct1(x.g), x.b, FM.x2(x.md), `<span class="heat" style="background:${col(x.irr)};padding:1px 6px;border-radius:4px">${FM.pct2(x.irr)}</span>`] }))); };
    $("#gridCsv").onclick = () => G ? download("mipf_structure_grid.csv", csv([["DSCR", "Tenor", "Debt", "Gearing", "Binding", "MinDSCR", "IRR"]].concat(G.map((x) => [x.d, x.t, x.D, x.g, x.b, x.md, x.irr]))), "text/csv") : alert("Compute the grid first."); }
}

// ------------------------------------------------------------------------------------------------ prompt studio
let PS = { block: "B14", kind: "tutor" };
const KINDS = PB.paths.map((p) => ({ k: p[0], n: p[1] }));
function blockById(id) { return PB.blocks.find((b) => b.id === id); }
function inputsText(b) { const rows = INP.rows; const L = b.inputs.filter((k) => rows[k]).map((k) => { const d = PB.tokens.P[k] || {}; const u = ["pct0", "pct1", "pct2", "x2", "date"].includes(d.fmt) ? "" : d.unit || ""; return `- ${d.label || k} (InpC row ${rows[k]}): {{${k}}} ${u}`.trim(); }); return L.length ? L.join("\n") : "- (no numeric inputs: this block is structural)"; }
function keyResultsText(b) { if (!b.results || !b.results.length) return ""; return "EXPECTED KEY RESULTS FOR THESE INPUTS (from the verified engine)\n" + b.results.map((k) => `- ${(PB.tokens[k[0]][k.slice(2)] || {}).label}: {{${k}}}`).join("\n"); }
function buildPrompt(b, kind) {
  let spec = b.spec || "(structural block: no row specification; follow the build order below)\n" + b.steps.map((s, i) => `${i + 1}. ${s}`).join("\n");
  if (b.spec && !isBaseCase()) spec = spec.replace(/\s*\|\s*(H=|L=|spot )[^|\n]*/g, "") + "\n(The H, L and spot reference values of the course Base case are omitted because the scenario or inputs differ from Base; use the live key results below.)";
  const cp = (b.checks.map((c) => "- " + c).join("\n") || "(see the checks of the sheets this block touches)") + (isBaseCase() ? "" : "\n(The values above are the course Base case. The scenario or inputs differ, so rely on the live key results below.)");
  const rep = { TITLE: b.title, SHEETS: b.sheet ? b.sheet.join(", ") : "the workbook structure", PURPOSE: b.purpose, CONCEPT: b.concept, DEPENDS: b.depends, PRODUCES: b.produces, SPEC: spec, CHECKPOINTS: cp, KEYRESULTS: keyResultsText(b), INPUTS: inputsText(b), CHARTER: PB.charter, OS: OS, TOOLS: PB.tools[kind] || "" };
  let t = PB.templates[kind]; for (const k in rep) t = t.split("{{" + k + "}}").join(rep[k]);
  if (!isBaseCase()) t = t.replace(/ The specification lines list the reference values[^.]*\./, ""); return resolveTokens(t);
}
const protectStars = (txt) => { let fenced = false; return txt.split("\n").map((ln) => { if (ln.startsWith("```")) { fenced = !fenced; return ln; } return fenced ? ln : ln.replace(/(?<=[\w$)\]])\*(?=[\w$(])/g, "\\*"); }).join("\n"); };
function exportHeadHtml() {
  const css = ".mipf-hero{display:flex;align-items:center;gap:14px;flex-wrap:wrap;background:#141B4D;color:#fff;padding:12px 18px;border-bottom:4px solid #D99A2B}.mipf-hero img{height:42px;background:#fff;border-radius:6px;padding:3px}.mipf-hero .t{flex:1;min-width:240px;font-size:.85rem}.mipf-hero .t b{display:block;font-size:1.05rem}.prompt{position:relative}.copy-prompt{position:absolute;top:6px;right:6px;z-index:2;background:#0B5E82;color:#fff;border:0;border-radius:6px;padding:4px 10px;font-weight:700;cursor:pointer}.copy-prompt:focus-visible{outline:3px solid #D99A2B}";
  const js = 'document.addEventListener("DOMContentLoaded",function(){document.querySelectorAll("div.prompt").forEach(function(d){var pre=d.querySelector("pre");if(!pre)return;var b=document.createElement("button");b.type="button";b.className="copy-prompt";b.textContent="Copy prompt";b.setAttribute("aria-label","Copy this prompt to the clipboard");b.addEventListener("click",function(){var t=pre.innerText,done=function(){b.textContent="Copied";setTimeout(function(){b.textContent="Copy prompt"},1400)};if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(t).then(done,function(){});else{var a=document.createElement("textarea");a.value=t;document.body.appendChild(a);a.select();try{document.execCommand("copy")}catch(e){}a.remove();done()}});d.insertBefore(b,d.firstChild)})});';
  return "<style>" + css + "</style><script>" + js + "<\/script>";
}
function exportHeroHtml() {
  const im = [...document.querySelectorAll("header.top img")].map((i) => i.src);
  const alts = ["Lagos Business School", "MIPF", "bongo.ai"];
  const imgs = im.slice(0, 3).map((u, i) => `<img src="${u}" alt="${alts[i]}">`).join("");
  return `<div class="mipf-hero">${imgs}<div class="t"><b>Mastering Infrastructure and Project Finance Boot Camp: tailored Model Prompt Book</b>Prof Bongo Adi &middot; +234 706 164 8699 &middot; badi@lbs.edu.ng &middot; bongo.adi@fulbrightmail.org</div></div>`;
}
function tailoredQmd() {
  const K = kpis(CUR); let q = `---\ntitle: "MIPF Model Prompt Book: tailored run"\nsubtitle: "${ST.mode === "pf" ? "Project finance model" : "Start model"}, scenario ${ST.scn}"\nauthor: "Prof Bongo Adi, Lagos Business School (+234 706 164 8699, badi@lbs.edu.ng, bongo.adi@fulbrightmail.org)"\nformat:\n  html:\n    from: markdown-tex_math_dollars\n    toc: true\n    code-copy: true\n    embed-resources: true\n    include-in-header:\n      text: |\n        ${exportHeadHtml()}\n    include-before-body:\n      text: |\n        ${exportHeroHtml()}\n---\n\n`;
  q += "# Run summary\n\n| KPI | Value |\n|---|---|\n" + Object.entries(K).map(([k, [v, f]]) => `| ${k} | ${fmtv(v, f)} |`).join("\n") + "\n\nInputs changed from the course case:\n\n```json\n" + JSON.stringify(ST, null, 1) + "\n```\n\n# Charter\n\n```text\n" + PB.charter + "\n```\n\n";
  for (const b of PB.blocks) {
    q += `# ${b.id} ${b.title}\n\n**Day** ${b.day.replace(/^Day /, "")}. **Purpose.** ${b.purpose}\n\n**Concept.** ${b.concept}\n\n`;
    q += "## Build order\n\n" + b.steps.map((s, i) => `${i + 1}. ${s}`).join("\n") + "\n\n## Prompts\n\n";
    for (const k of KINDS) q += `### ${k.n}\n\n::: {.prompt}\n\`\`\`text\n${buildPrompt(b, k.k)}\n\`\`\`\n:::\n\n`;
    q += "## Checkpoints\n\n" + b.checks.map((c) => "- " + c).join("\n") + "\n\n## Options\n\n| Option | How | Effect |\n|---|---|---|\n" + b.options.map((o) => `| ${o[0]} | ${o[1]} | ${o[2]} |`).join("\n") + "\n\n## Failure modes\n\n| Symptom | Cause | Fix |\n|---|---|---|\n" + b.pitfalls.map((o) => `| ${o[0]} | ${o[1]} | ${o[2]} |`).join("\n") + "\n\n";
  }
  return protectStars(q);
}
function pPrompts() {
  const p = $("#p-prompts"), b = blockById(PS.block), txt = buildPrompt(b, PS.kind);
  p.innerHTML = banner() + `<div class="note">Prompts are tailored to the <b>current inputs</b>: the input values and the expected key results in each prompt are those of the run on screen. Open the Prompt Book (QMD / HTML) for the full specification of every block.</div>
  <div class="row"><select id="psBlock" class="sel" aria-label="Build block" style="max-width:520px">${PB.blocks.map((x) => `<option value="${x.id}" ${x.id === PS.block ? "selected" : ""}>${x.id} ${esc(x.title)}</option>`).join("")}</select>
  <select id="psOS" class="sel" aria-label="Operating system" style="max-width:160px">${["Windows or Mac", "Windows", "Mac"].map((x) => `<option ${x === OS ? "selected" : ""}>${x}</option>`).join("")}</select></div>
  <div class="row">${KINDS.map((k) => `<button data-k="${k.k}" aria-pressed="${k.k === PS.kind}" class="${k.k === PS.kind ? "" : "ghost"}">${esc(k.n)}</button>`).join("")}</div>
  <textarea class="prompt" id="psText" spellcheck="false" aria-label="Prompt text"></textarea>
  <div class="row noprint"><button id="psCopy">Copy prompt</button><button id="psDl" class="ghost">Download .txt</button><button id="psQmd" class="gold">Download tailored Prompt Book (.qmd, all blocks)</button><span class="u" id="psLen"></span></div>
  <div class="grid2" style="margin-top:8px"><div class="card"><h3>About this block</h3><p><b>${esc(b.day)}</b> · depends on ${esc(b.depends)}</p><p>${esc(b.purpose)}</p><p><b>Concept.</b> ${esc(b.concept)}</p><p><b>Build order</b></p><ol>${b.steps.map((s) => `<li>${esc(s)}</li>`).join("")}</ol></div>
  <div class="card"><h3>Options, checkpoints, failure modes</h3><p><b>Checkpoints</b></p><ul>${b.checks.map((c) => `<li>${esc(c)}</li>`).join("")}</ul><p><b>Options</b></p>${tbl(["Option", "How", "Effect"], b.options.map((o) => ({ cells: o.map((x) => `<span style="white-space:normal">${esc(x)}</span>`) })))}<p><b>Failure modes</b></p>${tbl(["Symptom", "Cause", "Fix"], b.pitfalls.map((o) => ({ cells: o.map((x) => `<span style="white-space:normal">${esc(x)}</span>`) })))}</div></div>`;
  $("#psText").value = txt; $("#psLen").textContent = txt.length.toLocaleString() + " characters";
  $("#psBlock").onchange = (e) => { PS.block = e.target.value; pPrompts(); }; $("#psOS").onchange = (e) => { OS = e.target.value; pPrompts(); };
  $$("button[data-k]", p).forEach((x) => (x.onclick = () => { PS.kind = x.dataset.k; pPrompts(); }));
  $("#psCopy").onclick = (e) => copy($("#psText").value, e.target); $("#psDl").onclick = () => download(`${b.id}_${PS.kind}_prompt.txt`, $("#psText").value);
  $("#psQmd").onclick = () => download("MIPF_Prompt_Book_tailored.qmd", tailoredQmd());
}

// ------------------------------------------------------------------------------------------------ atlas
let AT = { which: "pf", sheet: "", q: "", type: "", n: 150 };
function pAtlas() {
  const p = $("#p-atlas"), all = ATL[AT.which], sheets = [...new Set(all.map((x) => x.s))];
  const q = AT.q.toLowerCase(), rows = all.filter((x) => (!AT.sheet || x.s === AT.sheet) && (!AT.type || x.t === AT.type) && (!q || (x.l + " " + x.f + " " + x.j + " " + x.s + x.r).toLowerCase().includes(q)));
  const show = rows.slice(0, AT.n);
  const trs = show.map((x) => ({ cells: [x.s, x.r, `<span style="white-space:normal">${esc(x.l)}</span>`, x.t, `<span class="mono">${esc(x.f)}</span>`, `<span class="mono">${esc(x.j)}</span>`, x.x ? `<span class="mono">${esc(x.x)}</span>` : "", x.h != null && x.h !== "" ? (typeof x.h === "number" ? FM.n2(x.h) : esc(x.h)) : "", x.lv != null && typeof x.lv === "number" ? FM.n2(x.lv) : ""] }));
  p.innerHTML = `<div class="note">Every row of every sheet of the verified workbooks (${all.length.toLocaleString()} rows in the ${AT.which === "pf" ? "project-finance" : "start"} model): label, formula in the constant column (F), formula in the first timeline column (J), first-column exception, row total (H) and the value in column L (first forecast quarter, Base). This is the specification the prompts are built from.</div>
  <div class="row"><div class="seg"><button data-w="start" aria-pressed="${AT.which === "start"}" class="${AT.which === "start" ? "on" : ""}">Start model</button><button data-w="pf" aria-pressed="${AT.which === "pf"}" class="${AT.which === "pf" ? "on" : ""}">Project-finance model</button></div>
  <select id="atS" class="sel" aria-label="Sheet filter" style="max-width:150px"><option value="">All sheets</option>${sheets.map((s) => `<option ${s === AT.sheet ? "selected" : ""}>${s}</option>`).join("")}</select>
  <select id="atT" class="sel" aria-label="Row type filter" style="max-width:150px"><option value="">All types</option>${["pull", "calc", "const"].map((s) => `<option ${s === AT.type ? "selected" : ""}>${s}</option>`).join("")}</select>
  <input class="txt" id="atQ" aria-label="Search label or formula" placeholder="Search label or formula, e.g. SUMIFS, DSCR, EOMONTH" value="${esc(AT.q)}" style="max-width:340px"><span class="u">${rows.length} rows</span><button id="atCsv" class="ghost">CSV</button><button id="atSpec" class="ghost">Copy as prompt spec</button></div>
  ${tbl(["Sheet", "Row", "Label", "Type", "F (constant)", "J (first column)", "Exception (K)", "H total", "L value"], trs, { max: "68vh" })}${rows.length > AT.n ? `<div class="row"><button id="atMore">Show 150 more</button></div>` : ""}`;
  $$("button[data-w]", p).forEach((b) => (b.onclick = () => { AT.which = b.dataset.w; AT.sheet = ""; pAtlas(); }));
  $("#atS").onchange = (e) => { AT.sheet = e.target.value; AT.n = 150; pAtlas(); }; $("#atT").onchange = (e) => { AT.type = e.target.value; AT.n = 150; pAtlas(); };
  $("#atQ").oninput = (e) => { clearTimeout(pAtlas.t); const v = e.target.value; pAtlas.t = setTimeout(() => { AT.q = v; AT.n = 150; pAtlas(); const q = $("#atQ"); q.focus(); q.setSelectionRange(v.length, v.length); }, 250); }; if ($("#atMore")) $("#atMore").onclick = () => { AT.n += 150; pAtlas(); };
  $("#atCsv").onclick = () => download("mipf_formula_atlas.csv", csv([["Sheet", "Row", "Label", "Type", "F", "J", "Exception K", "H total", "L value"]].concat(rows.map((x) => [x.s, x.r, x.l, x.t, x.f, x.j, x.x || "", x.h == null ? "" : x.h, x.lv == null ? "" : x.lv]))), "text/csv");
  $("#atSpec").onclick = (e) => copy(rows.map((x) => `${x.s}!R${x.r} | ${x.l} | F: ${x.f} | J: ${x.j}${x.x ? " | exception K: " + x.x : ""}`).join("\n"), e.target);
}

// ------------------------------------------------------------------------------------------------ verification (in-browser)
function refTests() {
  const S0 = (s, o) => E.build(INP, s, Object.assign({ mode: "start" }, o || {})), PF = (s, o) => E.build(INP, s, Object.assign({ mode: "pf" }, o || {}));
  const T = (o) => E.construction(Object.assign({ H: 94850, g: 0.6, facility: 60000, upfront: 0.02, commit: 0.0075, rate: 0.065, dc: 360, idc: "open", drawdown: "pro", eqCommit: 40000, cod: E.ord(2021, 12, 31), nq: 8, mpp: 3, spend: INP.P.Base.spend }, o || {}));
  const t = [];
  const add = (n, f, w, tol) => t.push([n, f, w, tol]);
  add("Start Base shareholder NPV", () => S0("Base").npv, 17608.98731048808, 0.01);
  add("Start Base shareholder XIRR", () => S0("Base").irr, 0.3372310379718108, 1e-06);
  add("Start Base minimum DSCR (profile 1)", () => S0("Base").minDSCR, 1.1663261671210836, 1e-05);
  add("Start Base total CFADS", () => sum(S0("Base").m.cfads), 582323.9405780912, 0.01);
  add("Start Base total dividends", () => sum(S0("Base").m.div), 464032.94057809055, 0.01);
  add("Start Downside shareholder NPV", () => S0("Downside").npv, -6413.43075114246, 0.01);
  add("Start Downside shareholder XIRR", () => S0("Downside").irr, 0.22356835072305378, 1e-06);
  add("Start Downside minimum DSCR (profile 1)", () => S0("Downside").minDSCR, 0.7326986794402474, 1e-05);
  add("Start Downside total CFADS", () => sum(S0("Downside").m.cfads), 439072.92823280237, 0.01);
  add("Start Downside total dividends", () => sum(S0("Downside").m.div), 320781.9282328017, 0.01);
  add("Start Upside shareholder NPV", () => S0("Upside").npv, 40330.887152220515, 0.01);
  add("Start Upside shareholder XIRR", () => S0("Upside").irr, 0.4590542585501192, 1e-06);
  add("Start Upside minimum DSCR (profile 1)", () => S0("Upside").minDSCR, 1.575461277174449, 1e-05);
  add("Start Upside total CFADS", () => sum(S0("Upside").m.cfads), 718233.7448995315, 0.01);
  add("Start Upside total dividends", () => sum(S0("Upside").m.div), 599942.7448995309, 0.01);
  add("PF Base project cost", () => PF("Base").U, 101067.79924517678, 0.001);
  add("PF Base senior debt", () => PF("Base").c.D, 72154.22476191197, 0.001);
  add("PF Base sponsor funding", () => PF("Base").c.E, 28913.57448326479, 0.001);
  add("PF Base minimum DSCR", () => PF("Base").o.minDSCR, 2.2966072005060587, 1e-06);
  add("PF Base LLCR at COD", () => PF("Base").o.llcrCOD, 2.39985735277099, 1e-05);
  add("PF Base PLCR at COD", () => PF("Base").o.plcrCOD, 4.192333041644041, 1e-05);
  add("PF Base blended XIRR", () => PF("Base").irr, 0.4303359863473701, 1e-06);
  add("PF Base blended NPV", () => PF("Base").npv, 28243.559585447718, 0.01);
  add("PF Base total dividends", () => PF("Base").o.sumDiv, 442553.82286558725, 0.01);
  add("PF Base shareholder-loan interest paid", () => sum(PF("Base").o.paid), 18390.59599787667, 0.01);
  add("PF Base IDC", () => sum(PF("Base").c.idc), 4155.295949257809, 0.001);
  add("PF Downside project cost", () => PF("Downside").U, 99498.17037854169, 0.001);
  add("PF Downside senior debt", () => PF("Downside").c.D, 53910.52105918301, 0.001);
  add("PF Downside sponsor funding", () => PF("Downside").c.E, 45587.64931935867, 0.001);
  add("PF Downside minimum DSCR", () => PF("Downside").o.minDSCR, 2.3424558939528004, 1e-06);
  add("PF Downside LLCR at COD", () => PF("Downside").o.llcrCOD, 2.4605143105628313, 1e-05);
  add("PF Downside PLCR at COD", () => PF("Downside").o.plcrCOD, 4.278358601459601, 1e-05);
  add("PF Downside blended XIRR", () => PF("Downside").irr, 0.22341087903034987, 1e-06);
  add("PF Downside blended NPV", () => PF("Downside").npv, -7230.724550240018, 0.01);
  add("PF Downside total dividends", () => PF("Downside").o.sumDiv, 297218.3905553014, 0.01);
  add("PF Downside shareholder-loan interest paid", () => sum(PF("Downside").o.paid), 29947.659983185942, 0.01);
  add("PF Downside IDC", () => sum(PF("Downside").c.idc), 3107.48696233698, 0.001);
  add("PF Upside project cost", () => PF("Upside").U, 101402.98425676113, 0.001);
  add("PF Upside senior debt", () => PF("Upside").c.D, 76052.23819257086, 0.001);
  add("PF Upside sponsor funding", () => PF("Upside").c.E, 25350.746064190284, 0.001);
  add("PF Upside minimum DSCR", () => PF("Upside").o.minDSCR, 2.6820115612365925, 1e-06);
  add("PF Upside LLCR at COD", () => PF("Upside").o.llcrCOD, 2.7832830124532095, 1e-05);
  add("PF Upside PLCR at COD", () => PF("Upside").o.plcrCOD, 4.877427864424978, 1e-05);
  add("PF Upside blended XIRR", () => PF("Upside").irr, 0.6690296825377111, 1e-06);
  add("PF Upside blended NPV", () => PF("Upside").npv, 53023.72041746605, 0.01);
  add("PF Upside total dividends", () => PF("Upside").o.sumDiv, 578768.4193949479, 0.01);
  add("PF Upside shareholder-loan interest paid", () => sum(PF("Upside").o.paid), 15985.022234910559, 0.01);
  add("PF Upside IDC", () => sum(PF("Upside").c.idc), 4378.96571959954, 0.001);
  add("Original day count reproduces the old start-model NPV (17,687.86)", () => S0("Base", { daysShort: true }).npv, 17687.8614, 0.01);
  add("Original day count reproduces the old PF senior debt (72,403)", () => PF("Base", { daysShort: true }).c.D, 72403.4453, 0.01);
  add("Teaching case total uses", () => T().U, 100022.9, 0.1); add("Teaching case IDC", () => sum(T().idc), 3458.2, 0.1); add("Teaching case commitment fee", () => sum(T().cfee), 514.7, 0.1); add("Teaching case debt at COD", () => T().D, 60013.8, 0.1);
  add("Teaching case average-balance IDC", () => sum(T({ idc: "avg" }).idc), 3972.9, 0.1); add("Teaching case average-balance uses", () => T({ idc: "avg" }).U, 100535.6, 0.1); add("Teaching case equity-first IDC", () => sum(T({ drawdown: "eq1" }).idc), 2212.6, 0.1); add("Teaching case equity-first uses", () => T({ drawdown: "eq1" }).U, 98921.1, 0.1);
  add("Dated sponsor IRR is below the IRR from COD", () => (PF("Base").o.irrDated < PF("Base").irr ? 1 : 0), 1, 0);
  add("Equity first: better from COD, worse when dated", () => { const a = PF("Base"), b = PF("Base", { drawdown: "eq1" }); return b.irr > a.irr && b.o.irrDated < a.o.irrDated ? 1 : 0; }, 1, 0);
  add("XIRR is n/a when there is no sign change", () => (Number.isNaN(E.xirr([1, 2, 3], [1, 2, 3])) ? 1 : 0), 1, 0);
  add("Start model: balance sheet check", () => E.checks(S0("Base"))[0].value, 0, 1e-3);
  for (const c of ["Balance sheet balances in every column", "Sources equal uses in every construction quarter", "Senior debt repaid in full", "Shareholder loan repaid in full", "Deferred tax unwinds to zero", "DSRA ends at zero", "Debt drawn equals debt sized (Goal Seek gap)", "Debt drawn does not exceed the facility", "Spend profile sums to 100%"]) add("PF integrity: " + c, () => (E.checks(PF("Base")).find((x) => x.name === c) || { value: 1 }).value, 0, 1e-3);
  return t;
}
function pVerify() {
  const p = $("#p-verify");
  p.innerHTML = `<div class="note">This engine is a line-by-line port of the Python replicas that were verified against the workbooks (Cover, Val and Ratios sheets, three scenarios, zero error cells). The reference values below are read from a full formula evaluation of the delivered workbooks, which was also confirmed in Microsoft Excel (10 October 2026); the tests recompute them in your browser, so you can see that this page reproduces the workbook.</div><div class="row"><button id="vRun">Run reference tests</button><span id="vSum"></span></div><div id="vOut"></div>`;
  $("#vRun").onclick = () => { const T = refTests(); let ok = 0; const rows = T.map(([n, f, w, tol]) => { let v; try { v = f(); } catch (e) { v = NaN; } const pass = Math.abs(v - w) <= tol; ok += pass; return { cells: [esc(n), w.toLocaleString("en-US", { maximumFractionDigits: 6 }), isFinite(v) ? v.toLocaleString("en-US", { maximumFractionDigits: 6 }) : "error", tol, `<span class="pill ${pass ? "ok" : "bad"}">${pass ? "PASS" : "FAIL"}</span>`] }; });
    $("#vSum").innerHTML = `<span class="pill ${ok === T.length ? "ok" : "bad"}">${ok} of ${T.length} passed</span>`; $("#vOut").innerHTML = tbl(["Test", "Reference", "This page", "Tolerance", ""], rows, { max: "68vh" }); };
  $("#vRun").click();
}
function pGuide() {
  $("#p-guide").innerHTML = `<div class="grid2"><div class="card"><h3>What this app is</h3><p>An interactive version of the TrainStat model built on Days 4 to 7 of the Mastering Infrastructure and Project Finance Boot Camp (Lagos Business School, 14 to 22 October 2026). It runs the complete 84-quarter model in your browser: operating model, tax, assets, debt, equity, three statements, valuation (start model) and construction, debt sizing and sculpting, DSRA, shareholder loan, cover ratios and blended sponsor returns (project-finance model).</p>
  <p>It does not replace the Excel workbook; it is the fast way to explore options, to produce checkpoint numbers for any set of inputs, and to generate prompts tailored to those inputs.</p></div>
  <div class="card"><h3>How to use it</h3><ol><li>Choose <b>Start model</b> (Days 4 and 5) or <b>Project finance</b> (Days 6 and 7), and a scenario.</li><li>Change any input in the left panel. Changed inputs are highlighted; <b>Reset all</b> restores the course case.</li><li>Read the results in <b>Summary</b>, <b>Construction</b>, <b>Statements</b> and <b>Debt and cover</b>; compare in <b>Scenarios and sensitivity</b>; use <b>Pin run</b> to see the change from a reference run.</li><li>Open <b>Prompt studio</b> to copy prompts for any of the 24 build blocks, tailored to your inputs, or download a complete tailored Prompt Book (.qmd).</li><li><b>Share link</b> copies a URL that restores your inputs.</li></ol></div>
  <div class="card"><h3>Method and limits</h3><ul><li>Units: US$ thousands; quarterly timeline of 84 columns (30 Sep 2021 to 30 Jun 2042); COD 31 Dec 2021; forecast 2022 to 2041.</li><li>Project-finance sizing: capacity by backward recursion at the target DSCR over the tenor, on CFADS with tax computed before interest (no circularity); debt = minimum of capacity and the gearing cap; gearing solved so that debt drawn equals debt sized (the Goal Seek logic of the workbook).</li><li>Options marked <i>app only</i> (equal-principal repayment, average-balance interest with equity first, fixed-gearing equity cheque) are not in the delivered workbook.</li><li>Illustrative teaching model: not investment, legal or tax advice. Covenant levels are examples.</li><li>All calculation is local; nothing is sent to a server.</li></ul></div>
  <div class="card"><h3>Caveats and retained conventions</h3><ul><li><b>Illustrative teaching case.</b> Inputs are not market-calibrated; nothing here is investment, legal, tax or credit advice. The credit agreement, the concession and the applicable tax law govern a real transaction.</li><li><b>One currency.</b> US$ throughout; a naira-revenue project needs a currency-mismatch, convertibility and indexation analysis that this model does not contain.</li><li><b>Tax is jurisdiction-specific.</b> 30% rate, 5% per quarter written-down value, interest fully deductible, losses refunded in cash (option: carry forward). Verify Nigerian rules before relying on any figure.</li><li><b>R1: sponsor funding is dated at COD</b> in the workbook, so the blended IRR and NPV overstate the return; the app also shows the IRR dated at the contributions. <b>R2: tax losses are refunded.</b> The original day count (one day short) is corrected in the workbook and available as an option.</li><li><b>Debt is sized once.</b> Use the fixed-financing table in Scenarios and sensitivity for cover under stress; covenants are usually tested at each calculation date on a historic (and often also a projected) 12-month basis; LLCR tests use the projections.</li><li><b>Not modelled:</b> lock-up, DSRA draw, hedging, cash sweep, contingency, major-maintenance reserve.</li><li><b>Confidentiality.</b> Do not paste confidential transaction data into AI tools your organisation has not approved.</li><li>Full text: the Prompt Book, chapter "Scope, caveats and retained conventions".</li></ul></div><div class="card"><h3>Contacts</h3><p><b>Prof Bongo Adi</b><br>Lagos Business School, Pan-Atlantic University<br>Phone / WhatsApp +234 706 164 8699<br>badi@lbs.edu.ng<br>bongo.adi@fulbrightmail.org</p><p>Facilitator for Days 4 to 7 (financial modelling): Promise Godbold.</p></div></div>`;
}

// ------------------------------------------------------------------------------------------------ boot
window.addEventListener("beforeprint", () => { const keep = TAB; $$("section.panel").forEach((p) => { const k = p.id.slice(2); TAB = k; try { ({ summary: pSummary, construction: pConstruction, statements: pStatements, debt: pDebt, scenarios: pScenarios, prompts: pPrompts, atlas: pAtlas, verify: pVerify, guide: pGuide })[k](); } catch (e) {} }); TAB = keep; });
window.addEventListener("afterprint", () => renderAll());
$("#themeBtn").onclick = () => { const r = document.documentElement, o = ["auto", "light", "dark"], n = o[(o.indexOf(r.dataset.theme) + 1) % 3]; r.dataset.theme = n; $("#themeBtn").textContent = "Theme: " + n; };
(function keepFocusWrappers() {
  const wrap = (fn) => function () {
    const a = document.activeElement, d = a && a !== document.body ? { id: a.id, k: a.dataset && a.dataset.k, v: a.dataset && a.dataset.v, w: a.dataset && a.dataset.w, tag: a.tagName } : null;
    const r = fn.apply(this, arguments);
    if (d) { let el = d.id ? document.getElementById(d.id) : null; const sc = $("#p-" + TAB) || document;
      if (!el && d.k) el = $(`[data-k="${d.k}"]`, sc); if (!el && d.v) el = $(`[data-v="${d.v}"]`, sc); if (!el && d.w) el = $(`[data-w="${d.w}"]`, sc);
      if (el && el.focus) el.focus(); }
    return r;
  };
  pSummary = wrap(pSummary); pConstruction = wrap(pConstruction); pStatements = wrap(pStatements); pDebt = wrap(pDebt); pScenarios = wrap(pScenarios); pPrompts = wrap(pPrompts); pAtlas = wrap(pAtlas);
})();
$("#themeBtn").textContent = "Theme: auto";
buildSide(); recompute();
window.MIPFAPP = { get state() { return ST; }, get run() { return CUR; }, recompute, tokenText, buildPrompt, tailoredQmd, refTests, kpis };

// Smoke test: every combination of option switches must produce finite numbers and pass the integrity checks.
const fs = require("fs"), path = require("path");
const E = require("../src/engine.js");
const inputs = JSON.parse(fs.readFileSync(path.join(__dirname, "../data/inputs.json"), "utf8"));
const finite = (x) => (Array.isArray(x) ? x.every(finite) : typeof x === "number" ? Number.isFinite(x) : true);
let n = 0, bad = 0; const notes = [];
for (const scn of ["Base", "Downside", "Upside"])
for (const idc of ["open", "avg"]) for (const drawdown of ["pro", "eq1"]) for (const repay of ["sculpt", "p1", "p2", "p3", "equal"])
for (const dsraN of [0, 2, 4]) for (const shlPct of [0, 0.6, 1]) for (const taxInt of [true, false]) for (const sizing of ["solve", "fixed"]) {
  const o = { mode: "pf", idc, drawdown, repay, dsraN, shlPct, taxInt, sizing, fixedGearing: 0.65 };
  let R; n++;
  try { R = E.build(inputs, scn, o); } catch (e) { bad++; notes.push("THROW " + JSON.stringify(o) + " " + e.message); continue; }
  const failing = E.checks(R).filter((c) => !c.ok);
  const ok = Number.isFinite(R.irr) && Number.isFinite(R.npv) && finite(R.o.chk) && finite(R.c.uses) && failing.length === 0;
  const bs = Math.max(...R.o.chk.map(Math.abs));
  if (!ok || bs > 1e-3) { bad++; if (notes.length < 25) notes.push(`${scn} ${JSON.stringify(o)} irr=${R.irr} bs=${bs.toExponential(2)}`); }
}
// course presets must be clean: every check passes and no warnings
let wbad = 0;
for (const [scn, o] of [["Base", {}], ["Downside", {}], ["Upside", {}], ["Base", { drawdown: "eq1" }], ["Base", { idc: "avg" }], ["Base", { dsraN: 0, shlPct: 0 }], ["Base", { dscr: 2.5, tenor: 32 }]]) {
  const R = E.build(inputs, scn, Object.assign({ mode: "pf" }, o)); const w = E.warnings(R); if (w.length) { wbad++; notes.push("WARN " + scn + JSON.stringify(o) + " " + w.join("; ")); }
}
bad += wbad;
console.log(n + " combinations; " + bad + " problems");
notes.forEach((x) => console.log(x));
// start-mode sweep
let sbad = 0, sn = 0;
for (const scn of ["Base", "Downside", "Upside"]) for (const profile of [1, 2, 3]) for (const taxInt of [true, false]) for (const omSens of [true, false]) {
  const R = E.build(inputs, scn, { mode: "start", profile, taxInt, omSens }); sn++;
  if (!Number.isFinite(R.irr) || !Number.isFinite(R.npv)) sbad++;
}
console.log(sn + " start-model combinations; " + sbad + " problems");
process.exit(bad + sbad ? 1 : 0);

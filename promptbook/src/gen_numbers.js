// Produces data/numbers.json: every checkpoint, option comparison and sensitivity quoted in the prompt book (all computed by engine.js).
const fs = require("fs"), path = require("path");
const E = require("./engine.js");
const inputs = JSON.parse(fs.readFileSync(path.join(__dirname, "../data/inputs.json"), "utf8"));
const S = (a) => E.sum(a), R = (x, d) => Math.round(x * Math.pow(10, d)) / Math.pow(10, d);
const kp = (r) => ({ U: r.U, D: r.c.D, E: r.c.E, g: r.gearing, cap: r.cap, binding: r.binding, irr: r.irr, npv: r.npv, minDSCR: r.o.minDSCR, avgDSCR: r.o.avgDSCR,
  llcr: r.o.llcrCOD, plcr: r.o.plcrCOD, maxDSRA: r.o.maxDSRA, sumDiv: r.o.sumDiv, shlInt: S(r.o.paid), shlPrin: S(r.o.sp), idc: S(r.c.idc), cfee: S(r.c.cfee), upfront: S(r.c.upfront),
  hard: S(r.c.spend), shl0: r.o.sh0, sc0: r.o.sc0, lastRep: r.o.lastRep, dtaxEnd: r.o.dtax[E.N - 1], eqc: r.eqc });
const ks = (r) => ({ npv: r.npv, irr: r.irr, pirr: r.pirr, minDSCR: r.minDSCR, avgDSCR: r.avgDSCR, rev: S(r.m.rev), cost: S(r.m.cost), ebitda: S(r.m.ebitda), dep: S(r.m.dep), intr: S(r.m.intr),
  pbt: S(r.m.pbt), tax: S(r.m.taxexp), taxPaid: S(r.m.taxpaid), pat: S(r.m.pat), cfads: S(r.m.cfads), div: S(r.m.div), debt0: r.m.D0, sc0: r.m.sc0 });
const N = {};
const scn = ["Base", "Downside", "Upside"];
N.start = {}; N.pf = {}; N.startOriginal = {};
for (const s of scn) {
  N.start[s] = ks(E.build(inputs, s, { mode: "start" }));
  N.startOriginal[s] = ks(E.build(inputs, s, { mode: "start", taxInt: false, omSens: false }));
  N.pf[s] = kp(E.build(inputs, s, { mode: "pf" }));
}
// start-model repayment profiles
N.startProfiles = {}; for (const p of [1, 2, 3]) N.startProfiles[p] = ks(E.build(inputs, "Base", { mode: "start", profile: p }));
// teaching case, Day 6
const T = (o) => { const c = E.construction(Object.assign({ H: 94850, g: 0.6, facility: 60000, upfront: 0.02, commit: 0.0075, rate: 0.065, dc: 360, idc: "open", drawdown: "pro", eqCommit: 40000, cod: E.ord(2021, 12, 31), nq: 8, mpp: 3, spend: inputs.P.Base.spend }, o || {}));
  return { U: c.U, D: c.D, E: c.E, idc: S(c.idc), cfee: S(c.cfee), upfront: S(c.upfront), hard: S(c.spend), uses: c.uses, eq: c.eq, debt: c.debt, idcQ: c.idc, cfeeQ: c.cfee, spend: c.spend, ends: c.ends.map(E.iso), days: c.days, bal: c.bal }; };
N.teaching = { open: T(), avg: T({ idc: "avg" }), eq1: T({ drawdown: "eq1" }), eq1avg: T({ drawdown: "eq1", idc: "avg" }) };
// option studies on the solved Base case
const B = (o) => kp(E.build(inputs, "Base", Object.assign({ mode: "pf" }, o)));
N.opt = {
  idc: { open: B({}), avg: B({ idc: "avg" }) },
  drawdown: { pro: B({}), eq1: B({ drawdown: "eq1" }), eq1avg: B({ drawdown: "eq1", idc: "avg" }) },
  repay: {}, dsra: {}, shl: {}, taxInt: { on: B({}), off: B({ taxInt: false }) }, gmax: {}, dscr: {}, tenor: {}, rate: {}, fixed: {}
};
for (const r of ["sculpt", "p1", "p2", "p3", "equal"]) N.opt.repay[r] = B({ repay: r });
for (const d of [0, 1, 2, 4, 6]) N.opt.dsra[d] = B({ dsraN: d });
for (const p of [0, 0.3, 0.6, 0.8, 1]) N.opt.shl[p] = B({ shlPct: p });
for (const g of [0.6, 0.65, 0.7, 0.75, 0.8]) N.opt.gmax[g] = B({ gmax: g });
for (const d of [1.5, 1.75, 2, 2.25, 2.5, 3]) N.opt.dscr[d] = B({ dscr: d });
for (const t of [28, 32, 36, 40, 44, 48]) N.opt.tenor[t] = B({ tenor: t });
for (const r of [0.055, 0.06, 0.065, 0.07, 0.075]) N.opt.rate[r] = B({ rate: r });
for (const g of [0.5, 0.6, 0.7]) N.opt.fixed[g] = B({ sizing: "fixed", fixedGearing: g });
// grid DSCR x tenor (Day 7 slide), 75% cap
N.grid = []; for (const d of [1.75, 2, 2.25, 2.5]) for (const t of [32, 40, 48]) { const r = B({ dscr: d, tenor: t }); N.grid.push({ dscr: d, tenor: t, cap: r.cap, D: r.D, g: r.g, minDSCR: r.minDSCR, irr: r.irr, binding: r.binding }); }
// one-way sensitivities (each fully re-solved)
const base = B({});
N.base = base;
const tor = [["Fare -10%", { fareM: 0.9 }], ["Fare +10%", { fareM: 1.1 }], ["Occupancy -10%", { occM: 0.9 }], ["Occupancy +10%", { occM: 1.1 }], ["O&M +10%", { omM: 1.1 }], ["O&M -10%", { omM: 0.9 }],
  ["All operating cost +10%", { costM: 1.1 }], ["Interest +1 pt", { rateAdd: 0.01 }], ["Interest -1 pt", { rateAdd: -0.01 }], ["Hard cost +10%", { hard: 94850 * 1.1 }], ["Hard cost -10%", { hard: 94850 * 0.9 }], ["Target DSCR 2.50x", { dscr: 2.5 }], ["Target DSCR 2.00x", { dscr: 2.0 }]];
N.tornado = tor.map(([n, o]) => { const r = B(o); return { name: n, irr: r.irr, minDSCR: r.minDSCR, D: r.D, U: r.U, g: r.g, npv: r.npv }; });
// start-model one-way (Day 5 slide)
N.startSens = [["Fare -10%", { fareM: 0.9 }], ["Fare -5%", { fareM: 0.95 }], ["Fare +5%", { fareM: 1.05 }], ["Fare +10%", { fareM: 1.1 }], ["O&M +10%", { omM: 1.1 }], ["Operating cost +10%", { costM: 1.1 }], ["Interest +1 pt", { rateAdd: 0.01 }], ["Interest -1 pt", { rateAdd: -0.01 }]]
  .map(([n, o]) => { const r = E.build(inputs, "Base", Object.assign({ mode: "start" }, o)); return { name: n, npv: r.npv, irr: r.irr, ebitda: S(r.m.ebitda) }; });
// per-quarter first rows for checkpoints (Base PF): first operating quarter L column = index 2
const r0 = E.build(inputs, "Base", { mode: "pf" }), i = 2;
N.checkL = { date: E.iso(r0.m.end[i]), rev: r0.m.rev[i], cost: r0.m.cost[i], ebitda: r0.m.ebitda[i], cfads: r0.o.cfads[i], DS: r0.o.DS[i], dscr: r0.o.dscrT[i], intr: r0.o.intr[i], prin: r0.o.prin[i], bal: r0.o.bal[i], dsra: r0.o.dsra[i], tgt: r0.o.tgt[i], shl: r0.o.shl[i], due: r0.o.due[i], div: r0.o.div[i] };
// annual summary for the reference (Base PF)
N.annual = {}; for (let t = 0; t < E.N; t++) { const y = E.ymd(r0.m.end[t])[0]; const a = N.annual[y] || (N.annual[y] = { rev: 0, ebitda: 0, cfads: 0, DS: 0, div: 0 }); a.rev += r0.m.rev[t]; a.ebitda += r0.m.ebitda[t]; a.cfads += r0.o.cfads[t]; a.DS += r0.o.DS[t]; a.div += r0.o.div[t]; }
// ---- sponsor IRR dated at the construction contribution dates, versus the workbook convention (all sponsor funding at COD)
N.dated = {};
for (const [k, o] of [["pro", {}], ["eq1", { drawdown: "eq1" }], ["eq1avg", { drawdown: "eq1", idc: "avg" }], ["avg", { idc: "avg" }]]) { const r = E.build(inputs, "Base", Object.assign({ mode: "pf" }, o)); N.dated[k] = { irrCOD: r.irr, irrDated: r.o.irrDated, U: r.U, E: r.c.E, idc: S(r.c.idc) }; }
for (const s of scn) { const r = E.build(inputs, s, { mode: "pf" }); N.dated[s] = { irrCOD: r.irr, irrDated: r.o.irrDated }; }
// ---- downside and upside tested on the Base financing (debt size and sculpted schedule frozen), with and without tax refunds
const baseRef = E.build(inputs, "Base", { mode: "pf" }), baseRefL = E.build(inputs, "Base", { mode: "pf", lossCF: true });
N.frozen = {};
for (const [name, sc, o] of [["Downside", "Downside", {}], ["Upside", "Upside", {}], ["Base fare -15%", "Base", { fareM: 0.85 }], ["Base fare -20%", "Base", { fareM: 0.8 }], ["Base fare -25%", "Base", { fareM: 0.75 }], ["Base O&M +20%", "Base", { omM: 1.2 }]]) {
  const a = E.build(inputs, sc, Object.assign({ mode: "pf", frozen: baseRef }, o)), b = E.build(inputs, sc, Object.assign({ mode: "pf", lossCF: true, frozen: baseRefL }, o));
  N.frozen[name] = { minRefund: a.o.minDSCR, avgRefund: a.o.avgDSCR, minLoss: b.o.minDSCR, avgLoss: b.o.avgDSCR, min12Refund: a.o.minDSCR12, min12Loss: b.o.minDSCR12, llcr: a.o.llcrCOD, irr: a.irr, warn: E.warnings(b), negCash: Math.min(...b.o.rcash.slice(b.o.i0)) < -1e-3 };
}
N.breakeven = { "1.00": E.breakeven(inputs, "Base", { mode: "pf", lossCF: true }, 1.0), "1.20": E.breakeven(inputs, "Base", { mode: "pf", lossCF: true }, 1.2), "1.00r": E.breakeven(inputs, "Base", { mode: "pf" }, 1.0), "1.20r": E.breakeven(inputs, "Base", { mode: "pf" }, 1.2),
  "1.00_12": E.breakeven(inputs, "Base", { mode: "pf", lossCF: true }, 1.0, "r12"), "1.20_12": E.breakeven(inputs, "Base", { mode: "pf", lossCF: true }, 1.2, "r12"), "1.00r_12": E.breakeven(inputs, "Base", { mode: "pf" }, 1.0, "r12"), "1.20r_12": E.breakeven(inputs, "Base", { mode: "pf" }, 1.2, "r12") };
// ---- tax losses: refund (workbook) versus carry-forward (app only)
N.lossCF = {}; for (const s of scn) { const a = E.build(inputs, s, { mode: "pf" }), b = E.build(inputs, s, { mode: "pf", lossCF: true }); N.lossCF[s] = { refundIrr: a.irr, loseIrr: b.irr, refundD: a.c.D, loseD: b.c.D, refundMin: a.o.minDSCR, loseMin: b.o.minDSCR, refundNpv: a.npv, loseNpv: b.npv,
  refundQ: a.o.taxpaid.filter((x) => x < -1e-9).length }; }
// ---- day-count convention: ORIGINAL file (end - start, one day short; app option) versus the corrected workbook (true calendar days)
const dsh = E.build(inputs, "Base", { mode: "pf", daysShort: true }), ssh = E.build(inputs, "Base", { mode: "start", daysShort: true });
N.daysShort = { pf: kp(dsh), start: ks(ssh) };
// ---- best structure on the grid
N.gridBest = N.grid.filter((g) => g.minDSCR >= 2.0).sort((a, b) => b.irr - a.irr)[0];
N.gridBestNpv = (() => { let best = null; for (const g of N.grid) { const r = B({ dscr: g.dscr, tenor: g.tenor }); if (g.minDSCR >= 2.0 && (!best || r.npv > best.npv)) best = { dscr: g.dscr, tenor: g.tenor, npv: r.npv, irr: r.irr }; } return best; })();
N.bestFrozen = {};
for (const [d, t] of [[2.0, 40], [2.25, 40], [1.75, 40]]) { const ref = E.build(inputs, "Base", { mode: "pf", dscr: d, tenor: t, lossCF: true }); const dn = E.build(inputs, "Downside", { mode: "pf", dscr: d, tenor: t, lossCF: true, frozen: ref });
  N.bestFrozen[d + "x/" + t] = { irr: ref.irr, irrDated: ref.o.irrDated, g: ref.gearing, D: ref.c.D, min: ref.o.minDSCR, dnMin: dn.o.minDSCR, dnMin12: dn.o.minDSCR12,
    be12: E.breakeven(inputs, "Base", { mode: "pf", dscr: d, tenor: t, lossCF: true }, 1.2), be10: E.breakeven(inputs, "Base", { mode: "pf", dscr: d, tenor: t, lossCF: true }, 1.0),
    be12r: E.breakeven(inputs, "Base", { mode: "pf", dscr: d, tenor: t, lossCF: true }, 1.2, "r12"), be10r: E.breakeven(inputs, "Base", { mode: "pf", dscr: d, tenor: t, lossCF: true }, 1.0, "r12") }; }
fs.writeFileSync(path.join(__dirname, "../data/numbers.json"), JSON.stringify(N));
console.log("numbers.json written; base", JSON.stringify(R(N.base.irr, 5)), R(N.base.minDSCR, 4));

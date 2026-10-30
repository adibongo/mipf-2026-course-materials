// Node test: engine vs reference values read from the delivered workbooks (formula evaluation of every scenario, confirmed in Microsoft Excel on 10 Oct 2026).
const fs = require("fs"), path = require("path");
const E = require("../src/engine.js");
const inputs = JSON.parse(fs.readFileSync(path.join(__dirname, "../data/inputs.json"), "utf8"));
let pass = 0, fail = 0;
function eq(name, got, want, tol) {
  const ok = Math.abs(got - want) <= tol; ok ? pass++ : fail++;
  console.log((ok ? "PASS " : "FAIL ") + name.padEnd(58) + " got " + got.toFixed(6) + "  want " + want.toFixed(6));
}
const S0 = (scn, o) => E.build(inputs, scn, Object.assign({ mode: "start" }, o || {}));
const PF = (scn, o) => E.build(inputs, scn, Object.assign({ mode: "pf" }, o || {}));
// ---- workbook reference values (corrected day count; facility = ROUNDUP(MIN(capacity, gearing cap x cost)))
eq("Start Base shareholder NPV", S0("Base").npv, 17608.98731048808, 0.01);
eq("Start Base shareholder XIRR", S0("Base").irr, 0.3372310379718108, 1e-06);
eq("Start Base minimum DSCR (profile 1)", S0("Base").minDSCR, 1.1663261671210836, 1e-05);
eq("Start Base total EBITDA", E.sum(S0("Base").m.ebitda), 789195.2008258444, 0.01);
eq("Start Base total CFADS", E.sum(S0("Base").m.cfads), 582323.9405780912, 0.01);
eq("Start Base total dividends", E.sum(S0("Base").m.div), 464032.94057809055, 0.01);
eq("Start Downside shareholder NPV", S0("Downside").npv, -6413.43075114246, 0.01);
eq("Start Downside shareholder XIRR", S0("Downside").irr, 0.22356835072305378, 1e-06);
eq("Start Downside minimum DSCR (profile 1)", S0("Downside").minDSCR, 0.7326986794402474, 1e-05);
eq("Start Downside total EBITDA", E.sum(S0("Downside").m.ebitda), 584550.8974754317, 0.01);
eq("Start Downside total CFADS", E.sum(S0("Downside").m.cfads), 439072.92823280237, 0.01);
eq("Start Downside total dividends", E.sum(S0("Downside").m.div), 320781.9282328017, 0.01);
eq("Start Upside shareholder NPV", S0("Upside").npv, 40330.887152220515, 0.01);
eq("Start Upside shareholder XIRR", S0("Upside").irr, 0.4590542585501192, 1e-06);
eq("Start Upside minimum DSCR (profile 1)", S0("Upside").minDSCR, 1.575461277174449, 1e-05);
eq("Start Upside total EBITDA", E.sum(S0("Upside").m.ebitda), 983352.0641421876, 0.01);
eq("Start Upside total CFADS", E.sum(S0("Upside").m.cfads), 718233.7448995315, 0.01);
eq("Start Upside total dividends", E.sum(S0("Upside").m.div), 599942.7448995309, 0.01);
eq("PF Base project cost", PF("Base").U, 101067.79924517678, 0.001);
eq("PF Base senior debt", PF("Base").c.D, 72154.22476191197, 0.001);
eq("PF Base sponsor funding", PF("Base").c.E, 28913.57448326479, 0.001);
eq("PF Base minimum DSCR", PF("Base").o.minDSCR, 2.2966072005060587, 1e-06);
eq("PF Base average DSCR", PF("Base").o.avgDSCR, 2.398417170529355, 1e-06);
eq("PF Base LLCR at COD", PF("Base").o.llcrCOD, 2.39985735277099, 1e-05);
eq("PF Base PLCR at COD", PF("Base").o.plcrCOD, 4.192333041644041, 1e-05);
eq("PF Base blended XIRR", PF("Base").irr, 0.4303359863473701, 1e-06);
eq("PF Base blended NPV", PF("Base").npv, 28243.559585447718, 0.01);
eq("PF Base total dividends", PF("Base").o.sumDiv, 442553.82286558725, 0.01);
eq("PF Base shareholder-loan interest paid", E.sum(PF("Base").o.paid), 18390.59599787667, 0.01);
eq("PF Base shareholder-loan principal repaid", E.sum(PF("Base").o.sp), 17781.848307207845, 0.01);
eq("PF Base IDC", E.sum(PF("Base").c.idc), 4155.295949257809, 0.001);
eq("PF Base commitment fee", E.sum(PF("Base").c.cfee), 619.4032959189708, 0.001);
eq("PF Base upfront fee", E.sum(PF("Base").c.upfront), 1443.1000000000001, 0.001);
eq("PF Downside project cost", PF("Downside").U, 99498.17037854169, 0.001);
eq("PF Downside senior debt", PF("Downside").c.D, 53910.52105918301, 0.001);
eq("PF Downside sponsor funding", PF("Downside").c.E, 45587.64931935867, 0.001);
eq("PF Downside minimum DSCR", PF("Downside").o.minDSCR, 2.3424558939528004, 1e-06);
eq("PF Downside average DSCR", PF("Downside").o.avgDSCR, 2.463258248222929, 1e-06);
eq("PF Downside LLCR at COD", PF("Downside").o.llcrCOD, 2.4605143105628313, 1e-05);
eq("PF Downside PLCR at COD", PF("Downside").o.plcrCOD, 4.278358601459601, 1e-05);
eq("PF Downside blended XIRR", PF("Downside").irr, 0.22341087903034987, 1e-06);
eq("PF Downside blended NPV", PF("Downside").npv, -7230.724550240018, 0.01);
eq("PF Downside total dividends", PF("Downside").o.sumDiv, 297218.3905553014, 0.01);
eq("PF Downside shareholder-loan interest paid", E.sum(PF("Downside").o.paid), 29947.659983185942, 0.01);
eq("PF Downside shareholder-loan principal repaid", E.sum(PF("Downside").o.sp), 28250.240187051524, 0.01);
eq("PF Downside IDC", E.sum(PF("Downside").c.idc), 3107.48696233698, 0.001);
eq("PF Downside commitment fee", E.sum(PF("Downside").c.cfee), 462.4634162047074, 0.001);
eq("PF Downside upfront fee", E.sum(PF("Downside").c.upfront), 1078.22, 0.001);
eq("PF Upside project cost", PF("Upside").U, 101402.98425676113, 0.001);
eq("PF Upside senior debt", PF("Upside").c.D, 76052.23819257086, 0.001);
eq("PF Upside sponsor funding", PF("Upside").c.E, 25350.746064190284, 0.001);
eq("PF Upside minimum DSCR", PF("Upside").o.minDSCR, 2.6820115612365925, 1e-06);
eq("PF Upside average DSCR", PF("Upside").o.avgDSCR, 2.781031761882736, 1e-06);
eq("PF Upside LLCR at COD", PF("Upside").o.llcrCOD, 2.7832830124532095, 1e-05);
eq("PF Upside PLCR at COD", PF("Upside").o.plcrCOD, 4.877427864424978, 1e-05);
eq("PF Upside blended XIRR", PF("Upside").irr, 0.6690296825377111, 1e-06);
eq("PF Upside blended NPV", PF("Upside").npv, 53023.72041746605, 0.01);
eq("PF Upside total dividends", PF("Upside").o.sumDiv, 578768.4193949479, 0.01);
eq("PF Upside shareholder-loan interest paid", E.sum(PF("Upside").o.paid), 15985.022234910559, 0.01);
eq("PF Upside shareholder-loan principal repaid", E.sum(PF("Upside").o.sp), 15590.708829477024, 0.01);
eq("PF Upside IDC", E.sum(PF("Upside").c.idc), 4378.96571959954, 0.001);
eq("PF Upside commitment fee", E.sum(PF("Upside").c.cfee), 652.9585371615916, 0.001);
eq("PF Upside upfront fee", E.sum(PF("Upside").c.upfront), 1521.06, 0.001);
// ---- original-file day count reproduces the old convention
eq("Original day count: start Base NPV (17,687.86)", S0("Base", { daysShort: true }).npv, 17687.8614, 0.01);
eq("Project XIRR is below the shareholder XIRR (leverage effect)", S0("Base").pirr < S0("Base").irr ? 1 : 0, 1, 0);
// ---- start-model one-way sensitivities keep their ordering and sign
eq("Fare -10% lowers NPV", S0("Base", { fareM: 0.9 }).npv < S0("Base").npv ? 1 : 0, 1, 0);
eq("Interest +1 pt lowers NPV", S0("Base", { rateAdd: 0.01 }).npv < S0("Base").npv ? 1 : 0, 1, 0);
let chk = E.checks(S0("Base")); eq("Start balance sheet check", chk[0].value, 0, 1e-3);
for (const c of E.checks(PF("Base"))) eq("PF check: " + c.name, c.value, 0, 1e-3);
// ---- sponsor IRR dated at the contribution dates, and the frozen-financing downside
let r = PF("Base"); eq("Dated sponsor IRR is lower than the COD IRR", r.o.irrDated < r.irr ? 1 : 0, 1, 0);
r = PF("Base", { drawdown: "eq1" }); eq("Equity first: IRR from COD higher, dated lower than pro-rata", (r.irr > PF("Base").irr && r.o.irrDated < PF("Base").o.irrDated) ? 1 : 0, 1, 0);
r = E.build(inputs, "Downside", { mode: "pf", lossCF: true, frozen: E.build(inputs, "Base", { mode: "pf", lossCF: true }) }); eq("Downside on Base financing (carry-forward): minimum DSCR in 1.3x to 1.6x", (r.o.minDSCR > 1.3 && r.o.minDSCR < 1.6) ? 1 : 0, 1, 0);
eq("XIRR returns NaN when there is no sign change", Number.isNaN(E.xirr([1, 2, 3], [1, 2, 3])) ? 1 : 0, 1, 0);
// ---- Day 6 teaching case (Constr sheet): hard cost 94,850, facility 60,000, 60% gearing (uses true days itself)
const T = (o) => E.construction(Object.assign({ H: 94850, g: 0.6, facility: 60000, upfront: 0.02, commit: 0.0075, rate: 0.065, dc: 360, idc: "open", drawdown: "pro", eqCommit: 40000,
  cod: E.ord(2021, 12, 31), nq: 8, mpp: 3, spend: inputs.P.Base.spend }, o || {}));
let c = T(); eq("Teaching: total uses (slide 100,022.9)", c.U, 100022.9, 0.1); eq("Teaching: IDC (3,458.2)", E.sum(c.idc), 3458.2, 0.1);
eq("Teaching: commitment fee (514.7)", E.sum(c.cfee), 514.7, 0.1); eq("Teaching: debt at COD (60,013.8)", c.D, 60013.8, 0.1);
c = T({ idc: "avg" }); eq("Teaching: average-balance IDC (3,972.9)", E.sum(c.idc), 3972.9, 0.1); eq("Teaching: avg uses (100,535.6)", c.U, 100535.6, 0.1);
c = T({ drawdown: "eq1" }); eq("Teaching: equity-first IDC (2,212.6)", E.sum(c.idc), 2212.6, 0.1); eq("Teaching: equity-first uses (98,921.1)", c.U, 98921.1, 0.1);
console.log("\n" + pass + " passed, " + fail + " failed");
process.exit(fail ? 1 : 0);

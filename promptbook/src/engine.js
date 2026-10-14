/* MIPF model engine: TrainStat start model (Days 4-5) and project-finance extension (Days 6-7).
 * A line-by-line port of the Python replicas that were verified against Microsoft Excel
 * (trainstat.py, pfmodel.py, pf2.py). Pure functions; works in Node and in the browser.
 * Units: US$ thousands. Quarterly timeline of 84 columns (J..CO): column 1 = 30 Sep 2021, column 2 = COD 31 Dec 2021. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.MIPF = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";
  const DAY = 86400000, N = 84;
  // ---------------------------------------------------------------- dates (integer day ordinals)
  const ord = (y, m, d) => Math.round(Date.UTC(y, m - 1, d) / DAY);
  const ymd = (o) => { const t = new Date(o * DAY); return [t.getUTCFullYear(), t.getUTCMonth() + 1, t.getUTCDate()]; };
  const iso = (o) => { const [y, m, d] = ymd(o); return y + "-" + String(m).padStart(2, "0") + "-" + String(d).padStart(2, "0"); };
  const parse = (s) => { if (typeof s === "number") return s; const [y, m, d] = String(s).slice(0, 10).split("-").map(Number); return ord(y, m, d); };
  const eom = (o, add) => { const [y, m] = ymd(o); const t = y * 12 + (m - 1) + add; return Math.round(Date.UTC(Math.floor(t / 12), (t % 12) + 1, 0) / DAY); };
  const firstOfMonth = (o, add) => { const [y, m] = ymd(o); const t = y * 12 + (m - 1) + add; return Math.round(Date.UTC(Math.floor(t / 12), t % 12, 1) / DAY); };
  const sum = (a) => a.reduce((x, y) => x + y, 0);
  const zeros = (n) => new Array(n).fill(0);

  function xirr(vals, dates) {
    const f = (r) => { let s = 0; for (let i = 0; i < vals.length; i++) s += vals[i] / Math.pow(1 + r, (dates[i] - dates[0]) / 365); return s; };
    let lo = -0.9, hi = 10, m = 0;
    if (!(f(lo) * f(hi) < 0)) return NaN; // no sign change in the bracket: no IRR
    for (let k = 0; k < 200; k++) { m = (lo + hi) / 2; if (f(lo) * f(m) <= 0) hi = m; else lo = m; }
    return m;
  }

  // ---------------------------------------------------------------- default options
  const DEFAULT_OPTS = {
    mode: "pf",            // "start" (Days 4-5) or "pf" (Days 6-7)
    omSens: true,          // O&M sensitivity input is live (corrected model); false reproduces the original file
    taxInt: true,          // interest is deductible in cash tax (corrected); false reproduces the original, stranded deferred tax
    profile: 1,            // start model repayment profile 1..3
    fareM: 1, occM: 1, omM: 1, costM: 1, rateAdd: 0,
    idc: "open",           // "open" interest on opening balance (the workbook) | "avg" average balance, solved algebraically
    drawdown: "pro",       // "pro" pro-rata | "eq1" equity first (uses eqCommit)
    repay: "sculpt",       // "sculpt" | "p1" | "p2" | "p3" | "equal" (equal principal over the tenor)
    sizing: "solve",       // "solve" (gearing found so debt drawn = debt sized) | "fixed" (use fixedGearing)
    fixedGearing: 0.60,
    dsraN: null, shlPct: null, shlRate: null, dscr: null, tenor: null, gmax: null, hard: null, upfront: null, commit: null,
    eqCommit: null, req: null, cap: null, rate: null, gearing: null, spend: null, facility: null, tax: null, arDays: null, apDays: null, tdep: null, life: null,
    lossCF: false,         // app only: tax losses are carried forward instead of refunded in cash (the workbook refunds)
    daysShort: false,      // app only: reproduce the ORIGINAL file's day count (end - start, one day short per quarter); the corrected workbook uses end - start + 1
    frozen: null,          // a previous PF result: keep its financing (debt size and repayment schedule) and test this case against it
  };

  // ---------------------------------------------------------------- operating model (Time, Esc, OpRev, OpCost, Tax, NCA, Debt, Equity, FinStat, Val)
  function run(P, S, o) {
    o = Object.assign({ profile: 1, nca0: null, fareM: 1, occM: 1, omM: 1, rateAdd: 0, costM: 1, omSens: true, taxInt: true, lossCF: false, daysShort: false }, o || {});
    const first = parse(P.first), acq = parse(P.acq), nyrs = P.nyrs, mpp = P.mpp;
    const beg = [], end = [];
    for (let i = 0; i < N; i++) { const b = firstOfMonth(first, i * mpp); beg.push(b); end.push(eom(b, mpp - 1)); }
    const days = end.map((e, i) => e - beg[i] + (o.daysShort ? 0 : 1)); // corrected workbook (Time row 30): period end minus period beginning plus 1 = true calendar days; daysShort reproduces the original one-day-short count
    const acqf = end.map((e) => (e === acq ? 1 : 0));
    const lastfc = eom(acq + 1, nyrs * 12 - 1);
    const fc = end.map((e) => (e > acq && e <= lastfc ? 1 : 0));
    const lastf = end.map((e) => (e === lastfc ? 1 : 0));
    const lastdep = eom(acq, P.life * 12);
    const depf = end.map((e) => (e > acq && e <= lastdep ? 1 : 0));
    // escalation
    const rates = P.infl.map(([d, r]) => [parse(d), r]);
    const infl = (d) => { let v = null; for (const [sd, rt] of rates) if (d >= sd) v = rt; return v; };
    const per = end.map((e) => Math.pow(1 + infl(e), 0.25) - 1);
    const cpi = zeros(N);
    for (let i = 0; i < N; i++) cpi[i] = acqf[i] ? 1 : i > 0 ? cpi[i - 1] * (1 + per[i]) : 0;
    const hesc = cpi.map((x) => (P.cpi0 / P.cpiH) * x), oesc = cpi.map((x) => (P.cpi0 / P.cpiO) * x);
    const N0 = o.nca0 !== null ? o.nca0 : P.nca0;
    // timetable inputs
    const od = S.od.map((x) => x * o.occM), oi = S.oi.map((x) => x * o.occM);
    const prof = [null, S.p1, S.p2, S.p3][o.profile];
    const arrD = S.td.map((t, i) => (fc[i] ? t * S.ad[i] : 0)), arrI = S.ti.map((t, i) => (fc[i] ? t * S.ai[i] : 0));
    const arr = arrD.map((a, i) => a + arrI[i]);
    const pax = arr.map((_, i) => P.capD * od[i] * arrD[i] + P.capI * oi[i] * arrI[i]);
    const rev = pax.map((p, i) => (fc[i] ? (P.fare * o.fareM / 1000) * p * cpi[i] : 0));
    const ar = zeros(N), rec = zeros(N);
    for (let i = 0; i < N; i++) {
      const b = i > 0 ? ar[i - 1] : 0;
      rec[i] = b + ((days[i] - P.arDays) / days[i]) * rev[i];
      ar[i] = acqf[i] ? 0 : b + rev[i] - rec[i];
    }
    const hv = arr.map((a, i) => (fc[i] ? (P.hVar / 1000) * a * hesc[i] : 0));
    const hf = hesc.map((e, i) => (fc[i] ? (P.hFixed / 4) * e : 0));
    const omk = P.omFixed * o.omM * (o.omSens ? 1 + (P.omSens || 0) : 1);
    const om = oesc.map((e, i) => (fc[i] ? (omk / 4) * e : 0));
    const cost = hv.map((v, i) => (v + hf[i] + om[i]) * o.costM);
    const ap = zeros(N), paid = zeros(N);
    for (let i = 0; i < N; i++) {
      const b = i > 0 ? ap[i - 1] : 0;
      paid[i] = b + ((days[i] - P.apDays) / days[i]) * cost[i];
      ap[i] = acqf[i] ? 0 : b + cost[i] - paid[i];
    }
    const ebitda = rev.map((r, i) => r - cost[i]);
    // NCA
    const cxMap = {}; for (const [d, a] of P.capex) cxMap[parse(d)] = a;
    const capex = end.map((e) => cxMap[e] || 0);
    const pl = P.lifeCapex * 4;
    const ret = capex.map((_, i) => { let s = 0; for (let j = 0; j <= i; j++) if (j + 1 === i + 1 - pl) s += capex[j]; return s; });
    const cdb = zeros(N), dcap = zeros(N);
    for (let i = 0; i < N; i++) { const b = i > 0 ? cdb[i - 1] : 0; dcap[i] = b / pl; cdb[i] = b + capex[i] - ret[i]; }
    const d0 = depf.map((f) => (f ? N0 / (P.life * 4) : 0));
    const dep = d0.map((x, i) => x + dcap[i]);
    const nca = zeros(N);
    for (let i = 0; i < N; i++) { const b = i > 0 ? nca[i - 1] : 0; nca[i] = acqf[i] ? N0 : b + capex[i] - dep[i]; }
    // tax written-down value
    const twdv = zeros(N), tdep = zeros(N);
    for (let i = 0; i < N; i++) { const b = i > 0 ? twdv[i - 1] : 0; tdep[i] = lastf[i] ? b : P.tdep * b; twdv[i] = acqf[i] ? N0 : b + capex[i] - tdep[i]; }
    // start-model senior debt (profiles 1-3 on the initial balance)
    const D0 = N0 * P.gearing, rate = P.rate + o.rateAdd, dc = P.dc;
    const debt = zeros(N), rep = zeros(N), intr = zeros(N);
    for (let i = 0; i < N; i++) { const b = i > 0 ? debt[i - 1] : 0; rep[i] = D0 * prof[i]; intr[i] = (b * rate / dc) * days[i]; debt[i] = acqf[i] ? D0 : b - rep[i]; }
    const taxable = ebitda.map((e, i) => e - tdep[i] - (o.taxInt ? intr[i] : 0));
    const taxpaid = taxOn(taxable, P.tax, o.lossCF);
    const pbt = ebitda.map((e, i) => e - dep[i] - intr[i]);
    const taxexp = pbt.map((x) => P.tax * x), pat = pbt.map((x, i) => x - taxexp[i]);
    const cfads = rec.map((r, i) => r - paid[i] - capex[i] - taxpaid[i]);
    // equity and dividends (start model)
    const sc0 = N0 * (1 - P.gearing), sc = zeros(N), red = zeros(N), cfd = zeros(N), div = zeros(N), rcash = zeros(N), re = zeros(N);
    for (let i = 0; i < N; i++) {
      const scb = i > 0 ? sc[i - 1] : 0;
      red[i] = scb * lastf[i]; sc[i] = acqf[i] ? sc0 : scb - red[i];
      const cfs = cfads[i] - intr[i] - rep[i]; cfd[i] = cfs - red[i];
      const rcb = i > 0 ? rcash[i - 1] : 0, reb = i > 0 ? re[i - 1] : 0;
      div[i] = Math.min(Math.max(rcb + cfd[i], 0), Math.max(reb + pat[i], 0));
      rcash[i] = acqf[i] ? 0 : rcb + cfd[i] - div[i];
      re[i] = acqf[i] ? 0 : reb + pat[i] - div[i];
    }
    const r = o.req != null ? o.req : P.req, vd = parse(P.valDate);
    const yrs = end.map((e) => (e - vd) / P.yDays), df = yrs.map((y) => 1 / Math.pow(1 + r, y));
    const sh = div.map((d, i) => d + red[i] - (acqf[i] ? sc0 : 0));
    const npv = sum(sh.map((x, i) => x * df[i]));
    const g = (k) => P[k];
    return { N, beg, end, days, acq: acqf, fc, lastf, cpi, rev, cost, ebitda, dep, tdep, capex, intr, rep, debt, pbt, pat, taxpaid, taxexp, cfads, div, sh, df, npv,
      arr, pax, hv, hf, om, rec, ar, ap, paid, nca, twdv, sc, red, rcash, re, D0, rate, dc, g, P, prof, sc0, r };
  }
  function taxOn(arr, rate, lossCF) {
    if (!lossCF) return arr.map((x) => rate * x);
    let loss = 0; return arr.map((x) => { if (x < 0) { loss -= x; return 0; } const use = Math.min(loss, x); loss -= use; return rate * (x - use); });
  }
  function shareholderIRR(m) {
    const vals = m.sh.map((x, i) => (x !== 0 ? x : i !== 0 ? 0 : -0.001));
    return xirr(vals, m.end);
  }
  // project IRR as taught on Day 5: -asset base at COD, then the model CFADS (after tax) each quarter; XIRR from the second column
  function projectIRR(m) {
    const pf = m.acq.map((a, i) => (a ? -m.nca[i] : m.cfads[i]));
    return xirr(pf.slice(1), m.end.slice(1));
  }

  // ---------------------------------------------------------------- construction (Constr sheet)
  function construction(a) {
    // a: {H,g,facility,upfront,commit,rate,dc,idc,drawdown,eqCommit,cod,nq,mpp,spend[]}
    const nq = a.nq || 8, mpp = a.mpp || 3, cod = a.cod;
    const ends = [], days = [];
    for (let i = 0; i < nq; i++) ends.push(eom(cod, -mpp * (nq - 1 - i))); // quarter nq ends at COD
    for (let i = 0; i < nq; i++) days.push(ends[i] - eom(ends[i], -mpp));
    const spend = a.spend.map((p) => a.H * p);
    let bal = 0, cumeq = 0;
    const out = { ends, days, spend, upfront: [], idc: [], cfee: [], uses: [], eq: [], debt: [], bal: [], beg: [] };
    for (let i = 0; i < nq; i++) {
      const up = i === 0 ? a.upfront * a.facility : 0;
      const cf = ((a.facility - bal) * a.commit / a.dc) * days[i];
      const k = (a.rate / a.dc) * days[i];
      const X = spend[i] + up + cf;
      let idc, uses, eq;
      if (a.drawdown === "eq1") {
        const rem = Math.max(a.eqCommit - cumeq, 0);
        const idc0 = k * bal;
        if (a.idc === "avg" && X + idc0 > rem) idc = (k * (bal + (X - rem) / 2)) / (1 - k / 2);
        else idc = idc0;
        uses = X + idc; eq = Math.min(uses, rem); cumeq += eq;
      } else {
        idc = a.idc === "avg" ? (k * (bal + (a.g * X) / 2)) / (1 - (k * a.g) / 2) : bal * k;
        uses = X + idc; eq = uses * (1 - a.g);
      }
      const d = uses - eq;
      out.beg.push(bal); out.upfront.push(up); out.idc.push(idc); out.cfee.push(cf); out.uses.push(uses); out.eq.push(eq); out.debt.push(d);
      bal += d; out.bal.push(bal);
    }
    out.U = sum(out.uses); out.D = sum(out.debt); out.E = sum(out.eq);
    return out;
  }
  // debt capacity by backward recursion (Sculpt rows 20-23)
  function capacity(cf, days, i0, dscr, ten, rate, dc) {
    const bal = zeros(N + 1), first = i0 + 1;
    for (let t = N - 1; t >= 0; t--) {
      if (t + 1 >= N) { bal[t] = 0; continue; }
      const ds = first <= t + 1 && t + 1 < first + ten ? cf[t + 1] / dscr : 0;
      bal[t] = (bal[t + 1] + ds) / (1 + (rate / dc) * days[t + 1]);
    }
    return bal[i0];
  }
  function sizingCF(m, P, lossCF) {
    // CFADS used to size debt: pre-financing cash flow less tax computed BEFORE interest (no circularity)
    const pre = m.rec.map((r, i) => r - m.paid[i] - m.capex[i]);
    const tx = taxOn(m.ebitda.map((e, i) => e - m.tdep[i]), P.tax, lossCF);
    return pre.map((p, i) => p - tx[i]);
  }
  function cparams(P, op, g, facility, eqc) {
    return { H: op.hard != null ? op.hard : P.hard, g, facility, upfront: op.upfront != null ? op.upfront : P.upfront, commit: op.commit != null ? op.commit : P.commit,
      rate: (op.rate != null ? op.rate : P.rate) + (op.rateAdd || 0), dc: P.dc, idc: op.idc, drawdown: op.drawdown, eqCommit: eqc != null ? eqc : (op.eqCommit != null ? op.eqCommit : P.eqCommit),
      cod: parse(P.acq), nq: P.constrN, spend: op.spend || P.spend };
  }
  // Goal-Seek logic: find the gearing (pro-rata) or equity cheque (equity-first) so that debt drawn equals debt sized; iterate the asset base U
  function solve(P, S, op) {
    const dscr = op.dscr != null ? op.dscr : P.dscr, ten = op.tenor != null ? op.tenor : P.tenor, gmax = op.gmax != null ? op.gmax : P.gmax;
    const rate = (op.rate != null ? op.rate : P.rate) + (op.rateAdd || 0);
    const base = { fareM: op.fareM, occM: op.occM, omM: op.omM, costM: op.costM, rateAdd: op.rateAdd, omSens: op.omSens, taxInt: op.taxInt, lossCF: op.lossCF, daysShort: op.daysShort };
    let U = P.nca0, m, cfs, cap, c, x = 0, gg = 0.6, eqc = null;
    for (let it = 0; it < 40; it++) {
      m = run(P, S, Object.assign({}, base, { nca0: U }));
      cfs = sizingCF(m, P, op.lossCF);
      const i0 = m.acq.indexOf(1);
      cap = capacity(cfs, m.days, i0, dscr, ten, rate, P.dc);
      // the facility is the commitment that can actually be drawn: ROUNDUP of the lower of DSCR capacity and the gearing cap on the project cost (fees are charged on it)
      const fac = op.sizing === "fixed" ? (op.facility != null ? op.facility : Math.ceil(op.fixedGearing * U - 1e-9)) : Math.ceil(Math.min(cap, gmax * U) - 1e-9);
      if (op.sizing === "fixed") {
        gg = op.fixedGearing; c = construction(cparams(P, op, gg, fac));
        if (op.drawdown === "eq1") { eqc = c.U * (1 - gg); for (let k = 0; k < 30; k++) { c = construction(cparams(P, op, gg, fac, eqc)); eqc = c.U * (1 - gg); } } // equity cheque = (1 - gearing) x uses
      } else if (op.drawdown === "eq1") {
        let lo = 0, hi = 3 * (op.hard != null ? op.hard : P.hard);
        for (let k = 0; k < 80; k++) {
          x = (lo + hi) / 2; c = construction(cparams(P, op, null, fac, x));
          const target = Math.min(cap, gmax * c.U);
          if (c.D > target) lo = x; else hi = x;
        }
        eqc = x; c = construction(cparams(P, op, null, fac, x)); gg = c.D / c.U;
      } else {
        let lo = 0.2, hi = 0.97;
        for (let k = 0; k < 80; k++) {
          gg = (lo + hi) / 2; c = construction(cparams(P, op, gg, fac));
          const target = Math.min(cap, gmax * c.U);
          if (c.D > target) hi = gg; else lo = gg;
        }
        c = construction(cparams(P, op, gg, fac));
      }
      if (Math.abs(c.U - U) < 1e-7) { U = c.U; break; }
      U = c.U;
    }
    m = run(P, S, Object.assign({}, base, { nca0: U }));
    cfs = sizingCF(m, P, op.lossCF);
    return { m, c, g: gg, cap, cfs, U, eqc, fac: op.sizing === "fixed" ? (op.facility != null ? op.facility : Math.ceil(op.fixedGearing * U - 1e-9)) : Math.ceil(Math.min(cap, gmax * U) - 1e-9) };
  }

  // ---------------------------------------------------------------- operations after COD (Sculpt, Debt, DSRA, SHL, Equity, FinStat, Ratios, Val)
  function ops(P, m, c, cfs, op) {
    const dscr = op.dscr != null ? op.dscr : P.dscr, ten = op.tenor != null ? op.tenor : P.tenor;
    const shlPct = op.shlPct != null ? op.shlPct : P.shlPct, shlRate = op.shlRate != null ? op.shlRate : P.shlRate, dsraN = op.dsraN != null ? op.dsraN : P.dsraN;
    const rate = (op.rate != null ? op.rate : P.rate) + (op.rateAdd || 0), dc = P.dc, tr = P.tax;
    const { days, end } = m, i0 = m.acq.indexOf(1), first = i0 + 1;
    const D = c.D, U = c.U, E = c.E;
    const cap = capacity(cfs, days, i0, dscr, ten, rate, dc), dscrAct = (dscr * cap) / D;
    const cnt = zeros(N); for (let t = 0; t < N; t++) cnt[t] = (t > 0 ? cnt[t - 1] : 0) + m.fc[t];
    const pre = m.rec.map((r, i) => r - m.paid[i] - m.capex[i]);
    const bal = zeros(N), intr = zeros(N), prin = zeros(N), DS = zeros(N);
    let lastRep = ten; // counter of the last repayment quarter
    const rp = op.repay || "sculpt";
    const profArr = rp === "p1" ? op.S.p1 : rp === "p2" ? op.S.p2 : rp === "p3" ? op.S.p3 : null;
    if (profArr) { lastRep = 0; for (let t = 0; t < N; t++) if (profArr[t] > 1e-12) lastRep = Math.max(lastRep, cnt[t]); }
    for (let t = 0; t < N; t++) {
      const b = t > 0 ? bal[t - 1] : 0;
      if (t === i0) { bal[t] = D; continue; }
      intr[t] = ((b * rate) / dc) * days[t];
      if (op.frozen) { prin[t] = op.frozen.o.prin[t]; DS[t] = prin[t] + intr[t]; } // principal frozen; interest follows the balance
      else if (rp === "sculpt") { if (first <= t && t < first + ten) { DS[t] = cfs[t] / dscrAct; prin[t] = DS[t] - intr[t]; } }
      else if (profArr) { prin[t] = D * profArr[t]; DS[t] = prin[t] + intr[t]; }
      else if (rp === "equal") { if (first <= t && t < first + ten) { prin[t] = D / ten; DS[t] = prin[t] + intr[t]; } }
      bal[t] = b - prin[t];
    }
    const tgt = zeros(N);
    for (let t = i0; t < N; t++) { let s = 0; for (let u = 0; u < N; u++) if (cnt[u] > cnt[t] && cnt[u] <= cnt[t] + dsraN) s += DS[u]; tgt[t] = s; }
    const dsra = zeros(N), fund = zeros(N), rel = zeros(N);
    const sh0 = E * shlPct, sc0 = E - sh0;
    const shl = zeros(N), due = zeros(N), paid = zeros(N), capz = zeros(N), sp = zeros(N), sc = zeros(N), red = zeros(N), div = zeros(N), rcash = zeros(N), re = zeros(N), pat = zeros(N), pbt = zeros(N);
    let lossBal = op.lossCF ? 0 : null; const lossTax = (x) => { if (x < 0) { lossBal -= x; return 0; } const u = Math.min(lossBal, x); lossBal -= u; return tr * (x - u); };
    const taxpaid = zeros(N), cfads = zeros(N), cf42 = zeros(N), dtax = zeros(N), taxexp = zeros(N), cfdiv = zeros(N), avail = zeros(N), taxable = zeros(N);
    for (let t = 0; t < N; t++) {
      if (t === i0) { shl[t] = sh0; sc[t] = sc0; continue; }
      const sb = t > 0 ? shl[t - 1] : 0; due[t] = ((sb * shlRate) / dc) * days[t];
      taxable[t] = m.ebitda[t] - m.tdep[t] - (op.taxInt ? intr[t] + due[t] : 0);
      taxpaid[t] = lossBal === null ? tr * taxable[t] : lossTax(taxable[t]);
      cfads[t] = pre[t] - taxpaid[t]; cf42[t] = cfads[t] - DS[t];
      const b = t > 0 ? dsra[t - 1] : 0;
      const f = Math.min(Math.max(tgt[t] - b, 0), Math.max(cf42[t], 0)), r = Math.max(b - tgt[t], 0);
      fund[t] = f; rel[t] = r; dsra[t] = b + f - r;
      const av = Math.max(cf42[t] + r - f, 0); avail[t] = av;
      paid[t] = Math.min(due[t], av); capz[t] = due[t] - paid[t];
      const post = cnt[t] > lastRep ? 1 : 0;
      sp[t] = post * Math.min(sb + capz[t], av - paid[t]);
      shl[t] = sb + capz[t] - sp[t];
      const scb = t > 0 ? sc[t - 1] : 0; red[t] = scb * m.lastf[t]; sc[t] = scb - red[t];
      cfdiv[t] = cf42[t] + r - f - paid[t] - sp[t] - red[t];
      pbt[t] = m.ebitda[t] - m.dep[t] - intr[t] - due[t];
      taxexp[t] = tr * pbt[t]; pat[t] = pbt[t] - taxexp[t];
      const rcb = t > 0 ? rcash[t - 1] : 0, reb = t > 0 ? re[t - 1] : 0;
      div[t] = Math.min(Math.max(rcb + cfdiv[t], 0), Math.max(reb + pat[t], 0));
      rcash[t] = rcb + cfdiv[t] - div[t]; re[t] = reb + pat[t] - div[t];
      dtax[t] = (t > 0 ? dtax[t - 1] : 0) + taxexp[t] - taxpaid[t];
    }
    const chk = zeros(N);
    for (let t = i0; t < N; t++) chk[t] = m.nca[t] + m.ar[t] + rcash[t] + dsra[t] - (m.ap[t] + bal[t] + dtax[t] + shl[t] + sc[t] + re[t]);
    // sponsor returns
    const flows = div.map((d, t) => d + paid[t] + sp[t] + red[t]); flows[i0] -= sc0 + sh0;
    const ds = end.slice(i0), fl = flows.slice(i0);
    const irr = xirr(fl, ds);
    // sponsor IRR with each construction-quarter contribution dated when it is paid (the workbook dates all sponsor funding at COD)
    const dflows = c.eq.map((e) => -e).concat(flows.slice(i0 + 1)); const ddates = c.ends.concat(end.slice(i0 + 1));
    const irrDated = xirr(dflows, ddates);
    const vd = parse(P.valDate), req = op.req != null ? op.req : P.req;
    const npv = sum(fl.map((x, k) => x / Math.pow(1 + req, (ds[k] - vd) / P.yDays)));
    // cover ratios
    const dsc = [], dscrT = zeros(N);
    for (let t = 0; t < N; t++) if (DS[t] > 1e-3) { dscrT[t] = cfads[t] / DS[t]; dsc.push(dscrT[t]); }
    // rolling 12-month DSCR (4 quarters), the basis on which covenants are usually tested
    const dscr12 = zeros(N), d12 = [];
    for (let t = i0 + 4; t < N; t++) { let c4 = 0, d4 = 0, full = true; for (let k = 0; k < 4; k++) { c4 += cfads[t - k]; d4 += DS[t - k]; if (DS[t - k] <= 1e-3) full = false; } if (full && d4 > 1e-3) { dscr12[t] = c4 / d4; d12.push(dscr12[t]); } } // only windows wholly inside the repayment period
    const rt = days.map((d) => (rate / dc) * d);
    const loanFlag = cnt.map((x, t) => (x >= 1 && x <= lastRep ? 1 : 0)), projFlag = m.fc;
    const pv = (flag) => { const a = zeros(N + 1); for (let t = N - 1; t >= 0; t--) a[t] = t + 1 >= N ? 0 : (a[t + 1] + cfads[t + 1] * flag[t + 1]) / (1 + rt[t + 1]); return a; };
    const pvL = pv(loanFlag), pvP = pv(projFlag);
    const llcr = bal.map((b, t) => (b > 0.001 ? pvL[t] / b : 0)), plcr = bal.map((b, t) => (b > 0.001 ? pvP[t] / b : 0));
    const sumOf = (a) => sum(a);
    // lock-up style stats
    return { D, U, E, cap, dscrAct, bal, intr, prin, DS, tgt, dsra, fund, rel, shl, due, paid, sp, sc, red, div, rcash, re, pat, pbt, taxpaid, cfads, cf42, dtax, chk, irr, npv,
      irrDated, dscr12, minDSCR12: d12.length ? Math.min(...d12) : 0, minDSCR: dsc.length ? Math.min(...dsc) : 0, avgDSCR: dsc.length ? sum(dsc) / dsc.length : 0, i0, sh0, sc0, flows, taxexp, cfdiv, avail, cnt, dscrT, llcr, plcr, taxable,
      llcrCOD: llcr[i0], plcrCOD: plcr[i0], lastRep, maxDSRA: Math.max(...dsra), sumDiv: sumOf(div) };
  }

  // ---------------------------------------------------------------- top-level API
  function build(inputs, scn, userOpts) {
    const P0 = inputs.P[scn], S = inputs.S;
    const op = Object.assign({}, DEFAULT_OPTS, userOpts || {});
    const P = Object.assign({}, P0);
    // direct overrides of inputs from the UI
    for (const k of ["req", "dscr", "tenor", "gmax", "hard", "upfront", "commit", "eqCommit", "dsraN", "shlPct", "shlRate", "tax", "arDays", "apDays", "tdep", "life"]) if (op[k] != null) P[k] = op[k];
    if (op.rate != null) P.rate = op.rate;
    if (op.nca0 != null) P.nca0 = op.nca0;
    const base = { fareM: op.fareM, occM: op.occM, omM: op.omM, costM: op.costM, rateAdd: op.rateAdd, omSens: op.omSens, taxInt: op.taxInt, lossCF: op.lossCF, daysShort: op.daysShort };
    if (op.mode === "start") {
      P.gearing = op.gearing != null ? op.gearing : P.startGearing != null ? P.startGearing : 0.6; // the start model's typed 60% (the PF workbook stores the solved gearing here)
      P.nca0 = op.nca0 != null ? op.nca0 : 100000;               // typed asset base (the PF workbook links this cell to Constr!F52)
      const m = run(P, S, Object.assign({}, base, { profile: op.profile }));
      const irr = shareholderIRR(m);
      const i0 = m.acq.indexOf(1);
      const ds = m.debt.map((_, t) => m.intr[t] + m.rep[t]);
      const dsc = []; for (let t = 0; t < N; t++) if (ds[t] > 1e-3) dsc.push(m.cfads[t] / ds[t]);
      return { mode: "start", scn, op, P, m, irr, npv: m.npv, pirr: projectIRR(m), i0, ds, dtax: cumTaxDef(m), minDSCR: Math.min(...dsc), avgDSCR: sum(dsc) / dsc.length, dscrT: ds.map((d, t) => (d > 1e-3 ? m.cfads[t] / d : 0)) };
    }
    const o2 = Object.assign({}, op, { S });
    let sol;
    if (op.frozen) { const f = op.frozen, m = run(P, S, Object.assign({}, base, { nca0: f.U })); sol = { m, c: f.c, g: f.g, cap: f.cap, cfs: sizingCF(m, P, op.lossCF), U: f.U, eqc: f.eqc, fac: f.fac }; } // financing fixed at the reference case
    else sol = solve(P, S, o2);
    const o = ops(P, sol.m, sol.c, sol.cfs, o2);
    return { mode: "pf", scn, op, P, m: sol.m, c: sol.c, g: sol.g, cap: sol.cap, cfs: sol.cfs, o, irr: o.irr, npv: o.npv, U: sol.U, eqc: sol.eqc, fac: sol.fac, frozenIgnored: !!(op.frozen && ((op.hard != null && op.hard !== op.frozen.P.hard) || (op.upfront != null && op.upfront !== op.frozen.P.upfront) || (op.commit != null && op.commit !== op.frozen.P.commit) || (op.eqCommit != null && op.eqCommit !== op.frozen.P.eqCommit) || op.drawdown !== op.frozen.op.drawdown || op.idc !== op.frozen.op.idc || op.spend != null || (op.facility != null && op.facility !== op.frozen.fac))),
      gearing: sol.c.D / sol.c.U, binding: op.sizing === "fixed" ? "Fixed gearing" : sol.cap <= (op.gmax != null ? op.gmax : P.gmax) * sol.c.U + 1e-6 ? "DSCR" : "Gearing" };
  }
  // integrity checks used by the app and the tests
  function checks(R) {
    const out = [];
    const tol = 1e-3;
    if (R.mode === "pf") {
      out.push(["Spend profile sums to 100%", Math.abs(sum(R.P.spend) - 1) > 1e-9 && !R.op.spend ? Math.abs(sum(R.P.spend) - 1) : Math.abs(sum(R.op.spend || R.P.spend) - 1)]);
      out.push(["Sources equal uses in every construction quarter", Math.max(...R.c.uses.map((u, i) => Math.abs(u - R.c.eq[i] - R.c.debt[i])))]);
      out.push(["Balance sheet balances in every column", Math.max(...R.o.chk.map(Math.abs))]);
      out.push(["Debt drawn does not exceed the facility", R.op.frozen || (R.op.sizing === "fixed" && R.op.facility != null) ? 0 : Math.max(0, R.c.D - R.fac - 1e-6)]);
      out.push(["Debt drawn equals debt sized (Goal Seek gap)", R.op.sizing === "solve" && !R.op.frozen ? Math.abs(R.c.D - Math.min(R.cap, (R.op.gmax != null ? R.op.gmax : R.P.gmax) * R.c.U)) : 0]);
      out.push(["Senior debt repaid in full", Math.abs(R.o.bal[R.o.bal.length - 1])]);
      out.push(["Shareholder loan repaid in full", Math.abs(R.o.shl[R.o.shl.length - 1])]);
      out.push(["Deferred tax unwinds to zero", R.op.taxInt ? Math.abs(R.o.dtax[R.o.dtax.length - 1]) : 0]);
      out.push(["DSRA ends at zero", Math.abs(R.o.dsra[R.o.dsra.length - 1])]);
    } else {
      const m = R.m, i0 = R.i0;
      let mx = 0; for (let t = i0; t < N; t++) { const A = m.nca[t] + m.ar[t] + m.rcash[t]; const L = m.ap[t] + m.debt[t] + (cumTaxDef(m)[t]) + m.sc[t] + m.re[t]; mx = Math.max(mx, Math.abs(A - L)); }
      out.push(["Balance sheet balances in every column", mx]);
      out.push(["Senior debt repaid in full", Math.abs(m.debt[N - 1])]);
    }
    return out.map(([n, v]) => ({ name: n, value: v, ok: v <= tol }));
  }
  // soft warnings: the model still balances, but a lender would object to the result
  function warnings(R) {
    const w = [], tol = 1e-3;
    if (R.mode !== "pf") { const m = R.m; if (Math.min(...m.rcash.slice(R.i0)) < -tol) w.push("Retained cash is negative in some quarter (cash shortfall)."); if (R.minDSCR < 1) w.push("Minimum DSCR is below 1.00x: debt service is not covered in at least one quarter."); return w; }
    const o = R.o, i0 = o.i0;
    if (R.frozenIgnored) w.push("A construction input (cost, fees, drawdown, facility or spend profile) was changed on a frozen financing and is ignored: the project cost and financing stay at the reference case (a cost overrun needs a funding source).");
    if (Math.min(...o.prin.slice(i0 + 1)) < -tol) w.push("Negative principal in some quarter: the sculpted schedule re-borrows because CFADS is too low (check the downside).");
    if (Math.min(...o.dsra.slice(i0)) < -tol) w.push("DSRA balance is negative.");
    if (Math.min(...o.rcash.slice(i0)) < -tol) w.push("Retained cash is negative in some quarter: the model pays share-capital redemption or shareholder-loan cash that the project does not have.");
    if (o.minDSCR < 1) w.push("Minimum DSCR is below 1.00x: debt service is not covered in at least one quarter and the DSRA is not drawn in this model.");
    else if (o.minDSCR < 1.2) w.push("Minimum DSCR is below 1.20x, the usual dividend lock-up level (the model has no lock-up).");
    for (let t = i0 + 1; t < N; t++) if (o.sp[t] > tol && o.bal[t - 1] > 1) { w.push("Shareholder-loan principal is repaid while senior debt is still outstanding (repayment style other than sculpted)."); break; }
    if (R.op.sizing === "fixed" && R.op.facility != null && R.c.D > R.op.facility + 1) w.push("Debt drawn exceeds the facility override: add IDC and fees to the facility.");
    if (R.op.sizing !== "fixed" && (R.g <= 0.2001 || R.g >= 0.9699)) w.push("The gearing solver reached its bracket (20% to 97%): the inputs are not feasible.");
    return w;
  }
  // revenue fall (fare multiplier) at which the minimum DSCR on a FIXED financing reaches the target
  function breakeven(inputs, scn, userOpts, target, basis) {
    const ref = build(inputs, scn, userOpts); if (ref.mode !== "pf") return NaN;
    const f = (x) => { const r = build(inputs, scn, Object.assign({}, userOpts, { frozen: ref, fareM: (userOpts.fareM || 1) * x })); return (basis === "r12" ? r.o.minDSCR12 : r.o.minDSCR) - target; };
    let lo = 0.3, hi = 1; if (f(hi) < 0) return NaN; if (f(lo) > 0) return lo;
    for (let k = 0; k < 40; k++) { const m = (lo + hi) / 2; if (f(m) > 0) hi = m; else lo = m; }
    return (lo + hi) / 2;
  }
  function cumTaxDef(m) { const a = zeros(N); for (let t = 0; t < N; t++) a[t] = (t > 0 ? a[t - 1] : 0) + (m.acq[t] ? 0 : m.taxexp[t] - m.taxpaid[t]); return a; }

  const api = { N, ord, ymd, iso, parse, eom, xirr, run, shareholderIRR, projectIRR, construction, capacity, sizingCF, solve, ops, build, checks, warnings, breakeven, DEFAULT_OPTS, sum };
  return api;
});

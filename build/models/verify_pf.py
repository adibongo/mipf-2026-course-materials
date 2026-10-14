import json, sys
sys.path.insert(0,"/private/tmp/claude-501/s/model")
import pf2
from pf2 import solve, ops
from openpyxl.utils import get_column_letter as L
fname="pf_formulas.xlsx"
def run(scn):
    V=json.load(open(f"pf_{scn}.json")); g=lambda sh,a: V.get(f"'[{fname}]{sh.upper()}'!{a}")
    errs=[(k,v) for k,v in V.items() if isinstance(v,str) and v.startswith("#") and k!="#REF!"]
    print(f"\n[{scn}] errors:",errs[:5])
    print(" checks FinStat F80,F83,F86; Time F120; Constr F55,H48; Sculpt F32:",[g("FinStat",a) for a in ("F80","F83","F86")],g("Time","F120"),g("Constr","F55"),g("Constr","H48"),g("Sculpt","F32"))
    mx=max(abs(g("FinStat",f"{L(c)}{r}") or 0) for r in (80,83,86) for c in range(10,94)); print(" max check flag across all columns:",mx)
    print(" Constr U/D/E:",g("Constr","F52"),g("Constr","F53"),g("Constr","F54"),"| Sculpt cap/size/bind/dscr:",g("Sculpt","F26"),g("Sculpt","F29"),g("Sculpt","F30"),g("Sculpt","F31"))
    print(" Ratios min/avg DSCR, LLCR, PLCR:",g("Ratios","F13"),g("Ratios","F14"),g("Ratios","F22"),g("Ratios","F28"))
    print(" Val NPV(F41) IRR(F51):",g("Val","F41"),g("Val","F51"))
    print(" end balances CO: debt",g("Debt","CO45"),"SHL",g("SHL","CO24"),"DSRA",g("DSRA","CO18"),"deftax",g("FinStat","CO72"),"RE",g("FinStat","CO74"),"BS tot",g("FinStat","CO66"),g("FinStat","CO75"))
    return V,g
V,g=run("Base")
m,c,gg,cap,cfs=solve(); o=ops(m,c,cfs)
print("\nMIRROR  U/D/E:",c["U"],c["D"],c["E"],"cap",cap,"min/avg dscr",o["min_dscr"],o["avg_dscr"],"IRR",o["irr"])
print("MIRROR  div total",sum(o["div"]),"shl paid",sum(o["paid"]),"dsra max",max(o["dsra"]))
print("XL      div total",g("FinStat","H51"),"shl paid",g("SHL","H21"),"dsra max",max((g("DSRA",f"{L(cc)}18") or 0) for cc in range(10,94)))
mxd=0
for t in range(m["N"]):
    col=L(10+t)
    for sh,row,key in (("Debt",45,"bal"),("DSRA",18,"dsra"),("SHL",24,"shl"),("FinStat",39,"cfads"),("FinStat",51,None)):
        x=g(sh,f"{col}{row}")
        if key is None: continue
        mxd=max(mxd,abs((x or 0)-o[key][t]))
print("max abs diff (debt, dsra, shl, cfads) per period:",mxd)
for s in ("Downside","Upside"): run(s)

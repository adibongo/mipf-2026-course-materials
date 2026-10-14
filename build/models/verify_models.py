import json, sys, os, re
sys.path.insert(0,"/private/tmp/claude-501/s/model")
import trainstat as T
T.SRC_OVERRIDE[0]="/private/tmp/claude-501/s/model/stage1.xlsx"
from openpyxl.utils import get_column_letter as L
def load(prefix, fname):
    V=json.load(open(prefix)); return V, (lambda sh,a: V.get(f"'[{fname}]{sh.upper()}'!{a}"))
def errs(V):
    return [(k,v) for k,v in V.items() if isinstance(v,str) and (v.startswith("#") or "Err" in v[:4])]
def irr(m):
    v=[m["sh"][i] if m["sh"][i]!=0 else (-0.001 if i==0 else 0) for i in range(m["N"])]; return T.xirr(v,m["end"])
def check_start(prefix,fname,scn):
    V,g=load(prefix,fname)
    m=T.run(scn,fixed=True)
    e=errs(V); print(f"[{scn}] error cells:",len(e),e[:5])
    print(" checks FinStat F74,F77,F80, Time F120:",[g("FinStat",a) for a in ("F74","F77","F80")],g("Time","F120"))
    chk=[g("FinStat",f"{L(c)}{r}") for r in (74,77,80) for c in range(10,94)]
    print(" max |check flag|:",max(abs(x or 0) for x in chk if isinstance(x,float)))
    print(" NPV xl/py:",g("Val","F39"),m["npv"]," IRR xl/py:",g("Val","F49"),irr(m))
    print(" rev:",g("FinStat","H9"),sum(m["rev"])," ebitda:",g("FinStat","H11"),sum(m["ebitda"])," cfads:",g("FinStat","H38"),sum(m["cfads"])," div:",g("Equity","H39"),sum(m["div"]))
    print(" end deferred tax Tax!CO49:",g("Tax","CO49")," end RE FinStat CO25:",g("FinStat","CO25"))
    print(" min DSCR F92:",g("FinStat","F92")," avg:",g("FinStat","F93"))
    return V,g
if __name__=="__main__":
    kind,prefix,fname,scn=sys.argv[1:5]
    if kind=="start": check_start(prefix,fname,scn)

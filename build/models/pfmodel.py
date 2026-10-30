"""Project-finance extension for the TrainStat teaching model (Days 6-7): Python mirror used to verify slide formulas and produce checkpoints."""
import datetime as dt
from trainstat import run, eom, xirr
PROFILE=[0.05,0.10,0.15,0.20,0.20,0.15,0.10,0.05]
def construction(H=90000.0, g=0.60, facility=60000.0, upfront=0.02, commit=0.0075, rate=0.065, dc=360, method=1,
                 eq_commit=40000.0, cod=dt.date(2021,12,31), nq=8, mpp=3, profile=PROFILE):
    ends=[eom(cod,-mpp*(nq-i)) for i in range(1,nq+1)]
    days=[(ends[i]-eom(ends[i],-mpp)).days for i in range(nq)]
    spend=[H*p for p in profile]
    bal=0.0; out=dict(ends=ends,days=days,spend=spend,upfront=[],idc=[],cfee=[],uses=[],eq=[],debt=[],bal=[],beg=[])
    cumeq=0.0
    for i in range(nq):
        up=upfront*facility if i==0 else 0.0
        cf=(facility-bal)*commit/dc*days[i]
        k=rate/dc*days[i]
        if method==1:
            idc=bal*k
            uses=spend[i]+up+cf+idc
            if True: pass
        else:  # average balance, algebraic (pro-rata only)
            idc=k*(bal+g*(spend[i]+up+cf)/2)/(1-k*g/2)
            uses=spend[i]+up+cf+idc
        if method==2 and False: pass
        eq=uses*(1-g)
        d=uses-eq
        out["beg"].append(bal); out["upfront"].append(up); out["idc"].append(idc); out["cfee"].append(cf)
        out["uses"].append(uses); out["eq"].append(eq); out["debt"].append(d)
        bal+=d; out["bal"].append(bal)
    out["U"]=sum(out["uses"]); out["D"]=sum(out["debt"]); out["E"]=sum(out["eq"])
    return out
def construction_eqfirst(H=90000.0, facility=60000.0, upfront=0.02, commit=0.0075, rate=0.065, dc=360, eq_commit=40000.0,
                         cod=dt.date(2021,12,31), nq=8, mpp=3, profile=PROFILE):
    ends=[eom(cod,-mpp*(nq-i)) for i in range(1,nq+1)]
    days=[(ends[i]-eom(ends[i],-mpp)).days for i in range(nq)]
    spend=[H*p for p in profile]; bal=0.0; cumeq=0.0; out=dict(uses=[],eq=[],debt=[],idc=[],cfee=[],bal=[],ends=ends)
    for i in range(nq):
        up=upfront*facility if i==0 else 0.0
        cf=(facility-bal)*commit/dc*days[i]; idc=bal*rate/dc*days[i]
        uses=spend[i]+up+cf+idc
        eq=min(uses, eq_commit-cumeq); cumeq+=eq; d=uses-eq; bal+=d
        out["uses"].append(uses); out["eq"].append(eq); out["debt"].append(d); out["idc"].append(idc); out["cfee"].append(cf); out["bal"].append(bal)
    out["U"]=sum(out["uses"]); out["D"]=sum(out["debt"]); out["E"]=sum(out["eq"]); return out
if __name__=="__main__":
    for H in (88000,89000,90000,91000,92000):
        c=construction(H=H); print(H, round(c["U"],1), round(c["D"],1), round(c["E"],1), "IDC",round(sum(c["idc"]),1),"cfee",round(sum(c["cfee"]),1))
    c=construction_eqfirst(H=90000); print("eqfirst",round(c["U"],1),round(c["D"],1),round(c["E"],1),"IDC",round(sum(c["idc"]),1))

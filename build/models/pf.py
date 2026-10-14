import datetime as dt
from trainstat import run, eom, xirr
m=run()
N=m["N"]; end=m["end"]; days=m["days"]
cf=m["cfads"]; 
i0=[i for i in range(N) if m["acq"][i]][0]
print("COD col",i0,end[i0])
# CFADS first 12 forecast quarters
print("CFADS q1-q8",[round(x) for x in cf[i0+1:i0+9]])
print("CFADS sum fc",sum(cf), " first 4y avg/yr",sum(cf[i0+1:i0+17])/4)
# sculpting PV at 6.5%, 15y from first quarter after COD
r=m["g"](77)/360
def pv_cap(dscr, ten=60, rate=0.065, first=i0+1):
    # backward recursion
    bal=0.0
    for t in range(first+ten-1, first-1, -1):
        rp=rate/360*days[t]
        bal=(bal+cf[t]/dscr)/(1+rp)
    return bal
for d in (1.2,1.3,1.35,1.5,2.0):
    print("dscr",d,"capacity 15y",round(pv_cap(d)),"10y",round(pv_cap(d,40)))

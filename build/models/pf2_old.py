"""PF extension v2 (corrected model, Base scenario): sizing on CFADS with tax before interest; levered tax includes senior + shareholder-loan interest."""
import sys, datetime as dt
sys.path.insert(0,"/private/tmp/claude-501/s/model")
import trainstat as T
from trainstat import run, xirr
from pfmodel import construction
T.SRC_OVERRIDE[0]="/private/tmp/claude-501/s/model/stage1.xlsx"
H0=94850.0
def capacity(cf, days, i0, dscr, ten, rate, dc=360):
    N=len(cf); first=i0+1; bal=[0.0]*(N+1)
    for t in range(N-1,-1,-1):
        if t+1>=N: bal[t]=0.0; continue
        ds=cf[t+1]/dscr if (first<=t+1<first+ten) else 0.0
        bal[t]=(bal[t+1]+ds)/(1+rate/dc*days[t+1])
    return bal[i0]
def sizing_cf(m):
    g=m["g"]; N=m["N"]
    pre=[m["rec"][i]-m["paid"][i]-m["capex"][i] for i in range(N)]
    unlev=[g(86)*(m["ebitda"][i]-m["tdep"][i]) for i in range(N)]
    return [pre[i]-unlev[i] for i in range(N)], pre, unlev
def solve(scn="Base", dscr=2.25, ten=40, gmax=0.75, H=H0, shl_pct=0.60, shl_rate=0.10, dsra_n=2, verbose=False):
    U=100000.0
    for it in range(40):
        m=run(scn,nca0=U,fixed=True)
        cfs,_,_=sizing_cf(m); i0=[i for i in range(m["N"]) if m["acq"][i]][0]
        cap=capacity(cfs,m["days"],i0,dscr,ten,m["g"](77))
        lo,hi=0.2,0.97
        for _ in range(80):
            gg=(lo+hi)/2; c=construction(H=H,g=gg,facility=round(cap))
            Dst=min(cap,gmax*c["U"])
            if c["D"]>Dst: hi=gg
            else: lo=gg
        c=construction(H=H,g=gg,facility=round(cap))
        if abs(c["U"]-U)<1e-7: break
        U=c["U"]
    return m,c,gg,cap,cfs
def ops(m,c,cfs,dscr=2.25,ten=40,shl_pct=0.60,shl_rate=0.10,dsra_n=2):
    N=m["N"]; days=m["days"]; end=m["end"]; g=m["g"]; rate=g(77); dc=g(79)
    i0=[i for i in range(N) if m["acq"][i]][0]; first=i0+1
    D=c["D"]; U=c["U"]; E=c["E"]
    cap=capacity(cfs,days,i0,dscr,ten,rate); dscr_act=dscr*cap/D
    cnt=[0]*N
    for t in range(N): cnt[t]=(cnt[t-1] if t>0 else 0)+m["fc"][t]
    ebitda=m["ebitda"]; dep=m["dep"]; tdep=m["tdep"]
    pre=[m["rec"][i]-m["paid"][i]-m["capex"][i] for i in range(N)]
    bal=[0.0]*N; intr=[0.0]*N; prin=[0.0]*N; DS=[0.0]*N
    # senior schedule (independent of tax): sculpted on unlevered CFADS
    for t in range(N):
        b=bal[t-1] if t>0 else 0.0
        if t==i0: bal[t]=D; continue
        intr[t]=b*rate/dc*days[t]
        if first<=t<first+ten:
            DS[t]=cfs[t]/dscr_act; prin[t]=DS[t]-intr[t]
        bal[t]=b-prin[t]
    # DSRA targets
    tgt=[sum(DS[u] for u in range(N) if cnt[u]>cnt[t] and cnt[u]<=cnt[t]+dsra_n) if t>=i0 else 0.0 for t in range(N)]
    dsra=[0.0]*N; fund=[0.0]*N; rel=[0.0]*N
    sh0=E*shl_pct; sc0=E-sh0
    shl=[0.0]*N; due=[0.0]*N; paid=[0.0]*N; capz=[0.0]*N; sp=[0.0]*N
    sc=[0.0]*N; red=[0.0]*N; div=[0.0]*N; rcash=[0.0]*N; re=[0.0]*N; pat=[0.0]*N; pbt=[0.0]*N
    taxpaid=[0.0]*N; cfads=[0.0]*N; cf42=[0.0]*N; dtax=[0.0]*N; taxexp=[0.0]*N; cfdiv=[0.0]*N; avail=[0.0]*N
    for t in range(N):
        if t==i0: shl[t]=sh0; sc[t]=sc0; continue
        sb=shl[t-1]; due[t]=sb*shl_rate/360*days[t]
        taxable=ebitda[t]-tdep[t]-intr[t]-due[t]
        taxpaid[t]=g(86)*taxable
        cfads[t]=pre[t]-taxpaid[t]
        cf42[t]=cfads[t]-DS[t]
        b=dsra[t-1]
        f=min(max(tgt[t]-b,0.0),max(cf42[t],0.0)); r=max(b-tgt[t],0.0)
        fund[t]=f; rel[t]=r; dsra[t]=b+f-r
        av=max(cf42[t]+r-f,0.0); avail[t]=av
        paid[t]=min(due[t],av); capz[t]=due[t]-paid[t]
        post=1 if cnt[t]>ten else 0
        sp[t]=post*min(sb+capz[t],av-paid[t])
        shl[t]=sb+capz[t]-sp[t]
        scb=sc[t-1]; red[t]=scb*m["lastf"][t]; sc[t]=scb-red[t]
        cfdiv[t]=cf42[t]+r-f-paid[t]-sp[t]-red[t]
        pbt[t]=ebitda[t]-dep[t]-intr[t]-due[t]
        taxexp[t]=g(86)*pbt[t]; pat[t]=pbt[t]-taxexp[t]
        rcb=rcash[t-1]; reb=re[t-1]
        div[t]=min(max(rcb+cfdiv[t],0.0),max(reb+pat[t],0.0))
        rcash[t]=rcb+cfdiv[t]-div[t]; re[t]=reb+pat[t]-div[t]
        dtax[t]=dtax[t-1]+taxexp[t]-taxpaid[t]
    chk=[]
    for t in range(i0,N):
        A=m["nca"][t]+m["ar"][t]+rcash[t]+dsra[t]; Lb=m["ap"][t]+bal[t]+dtax[t]+shl[t]+sc[t]+re[t]
        chk.append(A-Lb)
    flows=[div[t]+paid[t]+sp[t]+red[t] for t in range(N)]; flows[i0]-=(sc0+sh0)
    ds=[end[i0]]+[end[t] for t in range(i0+1,N)]
    irr=xirr([flows[i0]]+flows[i0+1:],ds)
    dscr_t=[cfads[t]/DS[t] for t in range(N) if DS[t]>1e-3]
    return dict(D=D,U=U,E=E,cap=cap,dscr_act=dscr_act,bal=bal,intr=intr,prin=prin,DS=DS,tgt=tgt,dsra=dsra,fund=fund,rel=rel,shl=shl,due=due,paid=paid,sp=sp,sc=sc,red=red,div=div,rcash=rcash,re=re,pat=pat,pbt=pbt,
                taxpaid=taxpaid,cfads=cfads,cf42=cf42,dtax=dtax,chk=chk,irr=irr,min_dscr=min(dscr_t),avg_dscr=sum(dscr_t)/len(dscr_t),i0=i0,sh0=sh0,sc0=sc0,flows=flows,taxexp=taxexp,cfdiv=cfdiv,avail=avail,cnt=cnt)
if __name__=="__main__":
    m,c,g,cap,cfs=solve()
    o=ops(m,c,cfs)
    print("g",g,"cap",cap,"U",c["U"],"D",c["D"],"E",c["E"],"gearing",c["D"]/c["U"])
    print("bal chk max",max(abs(x) for x in o["chk"]),"IRR blended",o["irr"],"min/avg dscr",o["min_dscr"],o["avg_dscr"])
    print("sum div",sum(o["div"]),"end RE",o["re"][-1],"end dtax",o["dtax"][-1],"dsra max",max(o["dsra"]))
    import json
    allsol = {}
    for scn in ("Base", "Downside", "Upside"):
        mm, cc, gg, cp, cf2 = solve(scn)
        allsol[scn] = dict(g=gg, cap=cp, U=cc["U"], D=cc["D"], E=cc["E"], fac=round(min(cp, 0.75 * cc["U"])))
        print(scn, allsol[scn])
    json.dump(allsol, open("pf2_solution.json", "w"))

import datetime as dt, json
from trainstat import run, xirr
from pfmodel import construction, construction_eqfirst
H0=94850.0
def capacity(m,dscr,ten,rate,first_off=1):
    N=m["N"]; days=m["days"]; cf=m["cfads"]; i0=[i for i in range(N) if m["acq"][i]][0]
    first=i0+first_off; bal=[0.0]*(N+1)
    for t in range(N-1,-1,-1):
        inloan = 1 if (t>=first and t<first+ten) else 0
        nxt_ds=(cf[t+1]/dscr if (t+1<N and (t+1)>=first and (t+1)<first+ten) else 0.0)
        r1=(rate/360*days[t+1]) if t+1<N else 0.0
        bal[t]=(bal[t+1]+nxt_ds)/(1+r1) if t+1<N else 0.0
    return bal[i0], bal
def solve_g(m, dscr=2.0, ten=40, gcap=0.75, H=H0, facility=None):
    cap,_=capacity(m,dscr,ten,0.065)
    lo,hi=0.2,0.95
    for _ in range(100):
        g=(lo+hi)/2
        fac=facility if facility else cap
        c=construction(H=H,g=g,facility=fac)
        Dstar=min(cap,gcap*c["U"])
        if c["D"]>Dstar: hi=g
        else: lo=g
    return g,cap
def ops(m, D, U, E, dscr_target=None, ten=40, shl_pct=0.60, shl_rate=0.10, dsra_periods=2, scn="Upside", use_dsra=True, use_shl=True, profile_override=None):
    N=m["N"]; days=m["days"]; end=m["end"]; g=m["g"]; rate=g(77); dc=g(79)
    i0=[i for i in range(N) if m["acq"][i]][0]; first=i0+1
    cf=m["cfads"]
    cap,_=capacity(m,dscr_target or 2.0,ten,rate)
    dscr_act=(dscr_target or 2.0)*cap/D          # sculpt at constant DSCR so that PV(DS)=D
    ds_t=[ (cf[t]/dscr_act if (first<=t<first+ten) else 0.0) for t in range(N)]
    bal=[0.0]*N; intr=[0.0]*N; prin=[0.0]*N
    for t in range(N):
        b=bal[t-1] if t>0 else 0.0
        if t==i0: bal[t]=D; continue
        intr[t]=b*rate/dc*days[t]
        prin[t]=ds_t[t]-intr[t] if first<=t<first+ten else 0.0
        bal[t]=b-prin[t]
    DS=[intr[t]+prin[t] for t in range(N)]
    cnt=[0]*N
    for t in range(N): cnt[t]=(cnt[t-1] if t>0 else 0)+m["fc"][t]
    # DSRA
    dsra=[0.0]*N; fund=[0.0]*N; rel=[0.0]*N; tgt=[0.0]*N
    for t in range(N):
        tgt[t]=sum(DS[u] for u in range(N) if cnt[u]>cnt[t] and cnt[u]<=cnt[t]+dsra_periods) if use_dsra and t>=i0 else 0.0
    shl=[0.0]*N; due=[0.0]*N; paid=[0.0]*N; capz=[0.0]*N; sp=[0.0]*N
    sh0=(E*shl_pct) if use_shl else 0.0; sc0=E-sh0
    sc=[0.0]*N; red=[0.0]*N; div=[0.0]*N; rcash=[0.0]*N; re=[0.0]*N; pat=[0.0]*N; pbt=[0.0]*N; dtax=[0.0]*N
    cf42=[0.0]*N; avail=[0.0]*N; cfdiv=[0.0]*N
    for t in range(N):
        b=dsra[t-1] if t>0 else 0.0
        cf42[t]=cf[t]-DS[t]
        if t==i0: dsra[t]=0.0; shl[t]=sh0; sc[t]=sc0; continue
        f=min(max(tgt[t]-b,0.0),max(cf42[t],0.0)) if use_dsra else 0.0
        r=max(b-tgt[t],0.0) if use_dsra else 0.0
        fund[t]=f; rel[t]=r; dsra[t]=b+f-r
        net=r-f
        av=max(cf42[t]+net,0.0); avail[t]=av
        sb=shl[t-1] if t>0 else 0.0
        due[t]=sb*shl_rate/360*days[t] if use_shl else 0.0
        paid[t]=min(due[t],av); capz[t]=due[t]-paid[t]
        post=1 if cnt[t]>ten else 0
        sp[t]=post*min(sb+capz[t],av-paid[t]) if use_shl else 0.0
        shl[t]=sb+capz[t]-sp[t]
        scb=sc[t-1]; red[t]=scb*m["lastf"][t]; sc[t]=scb-red[t]
        cfdiv[t]=cf42[t]+net-paid[t]-sp[t]-red[t]
        pbt[t]=m["ebitda"][t]-m["dep"][t]-intr[t]-due[t]
        pat[t]=pbt[t]*(1-g(86))
        rcb=rcash[t-1]; reb=re[t-1]
        div[t]=min(max(rcb+cfdiv[t],0.0),max(reb+pat[t],0.0))
        rcash[t]=rcb+cfdiv[t]-div[t]; re[t]=reb+pat[t]-div[t]
        dtax[t]=(dtax[t-1] if t>0 else 0.0)+g(86)*pbt[t]-m["taxpaid"][t]
    # balance check
    chk=[]
    for t in range(i0,N):
        A=m["nca"][t]+m["ar"][t]+rcash[t]+dsra[t]; L=m["ap"][t]+bal[t]+dtax[t]+shl[t]+sc[t]+re[t]
        # NCA initial must be U, not 100000: adjust
        chk.append((end[t],A-L))
    return dict(D=D,dscr_act=dscr_act,cap=cap,ds=DS,intr=intr,prin=prin,bal=bal,tgt=tgt,dsra=dsra,fund=fund,rel=rel,shl=shl,due=due,paid=paid,sp=sp,sc=sc,red=red,div=div,
                rcash=rcash,re=re,pat=pat,pbt=pbt,cf42=cf42,sh0=sh0,sc0=sc0,i0=i0,first=first,cnt=cnt,cfdiv=cfdiv,avail=avail,dtax=dtax,chk=chk)
def irr_blend(m,o,U):
    N=m["N"]; end=m["end"]; i0=o["i0"]
    flows=[0.0]*N
    for t in range(N):
        flows[t]=o["div"][t]+o["paid"][t]+o["sp"][t]+o["red"][t]
    flows[i0]-= (o["sc0"]+o["sh0"])
    ef=[0.0]*N
    for t in range(N): ef[t]=o["div"][t]+o["red"][t]
    ef[i0]-=o["sc0"]
    ds=[end[i0]]+[end[t] for t in range(i0+1,N)]
    return xirr([flows[i0]]+flows[i0+1:],ds), xirr([ef[i0]]+ef[i0+1:],ds), flows
if __name__=="__main__":
    m=run()
    g,cap=solve_g(m); c=construction(H=H0,g=g,facility=cap)
    print("g",round(g,5),"cap",round(cap),"U",round(c["U"]),"D",round(c["D"]),"E",round(c["E"]),"gearing",round(c["D"]/c["U"],4))
    o=ops(m,c["D"],c["U"],c["E"],2.0)
    print("dscr act",o["dscr_act"],"min/max balance check", max(abs(x[1]) for x in o["chk"]))

def full_solve(gcap=0.75, dscr=2.0, ten=40, H=H0, verbose=False):
    U=100000.0
    for it in range(30):
        m=run(nca0=U)
        g,cap=solve_g(m,dscr,ten,gcap,H)
        c=construction(H=H,g=g,facility=cap)
        if abs(c["U"]-U)<1e-6: break
        U=c["U"]
    m=run(nca0=c["U"]); o=ops(m,c["D"],c["U"],c["E"],dscr,ten)
    return m,c,o,g,cap

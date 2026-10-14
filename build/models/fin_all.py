import json, sys, time
sys.path.insert(0,".")
from finalize_models import finalize
from inject_cache import inject
from dump_model import dump
t=time.time()
for kind in ("pf","start"):
    src=f"{kind}_formulas.xlsx"
    runs={s:(f"{kind}_{s}.json",src) for s in ("Base","Downside","Upside")}
    finalize(src,f"{kind}_fin.xlsx",runs); print(kind,"finalized",round(time.time()-t),flush=True)
    V=json.load(open(f"{kind}_Base.json"))
    print(kind,inject(f"{kind}_fin.xlsx",V,src,f"{kind}_cached.xlsx"),round(time.time()-t),flush=True)
    d=dump(src,f"{kind}_Base.json",f"{kind}_rows.json"); print(kind,"rows",{k:len(v) for k,v in list(d.items())[:2]},round(time.time()-t),flush=True)
print("ALLDONE")

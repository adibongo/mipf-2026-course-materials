import formulas, sys, time, json, warnings
warnings.filterwarnings("ignore")
src=sys.argv[1]; prefix=sys.argv[2]
scen=sys.argv[3].split(",")
t=time.time()
xl=formulas.ExcelModel().loads(src).finish()
print("loaded",round(time.time()-t),flush=True)
base=src.split("/")[-1].upper()
key=f"'[{src.split('/')[-1]}]INPC'!F3"
for s in scen:
    sol=xl.calculate(inputs={key:s})
    out={}
    for k,v in sol.items():
        try: val=v.value[0,0]
        except Exception: continue
        try: out[k]=float(val)
        except Exception: out[k]=str(val)
    json.dump(out,open(f"{prefix}_{s}.json","w"))
    print("scenario",s,len(out),round(time.time()-t),flush=True)

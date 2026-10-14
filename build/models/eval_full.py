import formulas, sys, time, json, warnings
warnings.filterwarnings("ignore")
src=sys.argv[1]; dst=sys.argv[2]
t=time.time()
xl=formulas.ExcelModel().loads(src).finish()
print("loaded",time.time()-t,flush=True)
sol=xl.calculate()
print("calc",time.time()-t,flush=True)
out={}
for k,v in sol.items():
    try: val=v.value[0,0]
    except Exception: continue
    try: out[k]=float(val)
    except Exception: out[k]=str(val)
json.dump(out,open(dst,"w")); print("cells",len(out),time.time()-t)

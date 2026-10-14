import formulas, sys, time, json, pickle
t=time.time()
xl=formulas.ExcelModel().loads("pf_test.xlsx").finish()
sol=xl.calculate()
print("calc secs",time.time()-t)
out={}
for k,v in sol.items():
    try:
        val=v.value[0,0]
    except Exception:
        continue
    try: out[k]=float(val)
    except Exception: out[k]=str(val)
json.dump(out,open("pf_test_vals.json","w")); print(len(out))

import sys, re, datetime as dt
sys.path.insert(0,"/private/tmp/claude-501/s/model")
import openpyxl
from openpyxl.utils import get_column_letter as L, column_index_from_string as CI
from openpyxl.formula.translate import Translator
from pflayout import *
from pfops import full_solve
m,c,o,g,cap=full_solve()
wb=openpyxl.Workbook(); wb.remove(wb.active)
S={n:wb.create_sheet(n) for n in ["InpC","Time","FinStat","Debt","Constr","Sculpt","Ratios","DSRA","SHL"]}
fix=lambda f: f.replace("CHK_TOL","InpC!$F$101") if isinstance(f,str) else f
def put_block(ws,spec,ncols):
    for (r,E,F,G,Hf,Jf,key) in spec:
        if isinstance(E,str): ws.cell(r,5).value=E
        if F is not None: ws.cell(r,6).value=fix(F)
        if G is not None: ws.cell(r,7).value=G
        if Hf: ws.cell(r,8).value=fix(Hf)
        if Jf:
            for k in range(ncols):
                col=10+k
                ws.cell(r,col).value=fix(Translator(Jf,origin=f"J{r}").translate_formula(f"{L(col)}{r}")) if k>0 else fix(Jf)
# SMU replacement: units "=SMU" -> text
for ws in S.values():
    pass
ic=S["InpC"]
base={10:dt.date(2021,12,31),12:3,72:g,77:0.065,79:360,99:4,101:0.001}
for r,v in base.items(): ic.cell(r,6).value=v
for r,(lab,val,u) in INPC_NEW.items(): ic.cell(r,5).value=lab; ic.cell(r,6).value=val; ic.cell(r,7).value=u
ic["F131"].value=cap
for i,p in enumerate(SPEND): ic.cell(118+i,5).value=i+1; ic.cell(118+i,6).value=p
ic["F115"].value=94850
N=m["N"]
t=S["Time"]
for i in range(N):
    col=10+i
    t.cell(25,col).value=m["end"][i]; t.cell(30,col).value=m["days"][i]; t.cell(45,col).value=m["acq"][i]; t.cell(69,col).value=m["fc"][i]; t.cell(58,col).value=1 if m['end'][i]<=dt.date(2021,12,31) else 0
fs=S["FinStat"]
for i in range(N):
    col=10+i; cl=L(col)
    fs.cell(38,col).value=m["cfads"][i]
    fs.cell(40,col).value=f"=-Debt!{cl}32"; fs.cell(41,col).value=f"=-Debt!{cl}21"
    fs.cell(42,col).value=f"={cl}38+SUM({cl}40:{cl}41)"
db=S["Debt"]
db["F19"].value="=Constr!F53"
for i in range(N):
    col=10+i; cl=L(col); pc=L(col-1)
    db.cell(20,col).value=f"=Sculpt!{cl}40"
    db.cell(21,col).value=f"=$F19*{cl}20"
    db.cell(27,col).value=f"=Time!{cl}30"
    db.cell(28,col).value=f"=InpC!$F$77/InpC!$F$79*{cl}27"
    db.cell(32,col).value=f"={cl}41*{cl}28"
    db.cell(41,col).value=f"={pc}44" if i>0 else 0
    db.cell(44,col).value=f"=IF(Time!{cl}45=1,$F19,{cl}41-{cl}21)"
for nme,spec,nc in (("Constr",CONSTR,8),("Sculpt",SCULPT,N),("Ratios",RATIOS,N),("DSRA",DSRA,N),("SHL",SHL,N)):
    put_block(S[nme],spec,nc)
# SMU units as text
for ws in S.values():
    for row in ws.iter_rows(min_col=7,max_col=7):
        for cell in row:
            if cell.value=="=SMU": cell.value="$ 000s"
wb.save("pf_test.xlsx"); print("saved")

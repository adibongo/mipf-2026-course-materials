import json, sys, warnings
warnings.filterwarnings("ignore")
import openpyxl
from openpyxl.worksheet.formula import ArrayFormula
def finalize(src, out, runs):
    """runs: {'Base':(json,fname),'Downside':..., 'Upside':...}"""
    wb = openpyxl.load_workbook(src)
    tr = wb["Track"]
    cols = {"Base": "M", "Downside": "N", "Upside": "O"}
    for scn, (js, fname) in runs.items():
        V = json.load(open(js))
        for r in range(8, 70):
            if tr[f"H{r}"].value is None: continue
            v = V.get(f"'[{fname}]TRACK'!H{r}")
            if isinstance(v, float): tr[f"{cols[scn]}{r}"].value = v
    wb.calculation.fullCalcOnLoad = True
    wb.active = 0
    wb.save(out)
    return out
if __name__ == "__main__":
    pass

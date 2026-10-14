import zipfile, json, re, sys, shutil
from lxml import etree
NS={"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main","r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
def inject(xlsx, V, fname, out):
    zin=zipfile.ZipFile(xlsx)
    wbx=etree.fromstring(zin.read("xl/workbook.xml"))
    rels=etree.fromstring(zin.read("xl/_rels/workbook.xml.rels"))
    rid2t={r.get("Id"):r.get("Target") for r in rels}
    sheets={}
    for s in wbx.find("m:sheets",NS):
        rid=s.get("{%s}id"%NS["r"]); t=rid2t[rid]; t=t.lstrip("/")
        if not t.startswith("xl/"): t="xl/"+t
        sheets[t]=s.get("name")
    zout=zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED); n=0; miss=0
    for item in zin.infolist():
        data=zin.read(item.filename)
        if item.filename in sheets:
            name=sheets[item.filename].upper()
            root=etree.fromstring(data)
            for c in root.iter("{%s}c"%NS["m"]):
                f=c.find("m:f",NS)
                if f is None: continue
                key=f"'[{fname}]{name}'!{c.get('r')}"
                val=V.get(key)
                v=c.find("m:v",NS)
                if val is None:
                    miss+=1; continue
                if v is None: v=etree.SubElement(c,"{%s}v"%NS["m"])
                if isinstance(val,float):
                    if val!=val: continue
                    v.text=repr(val); 
                    if "t" in c.attrib: del c.attrib["t"]
                else:
                    sval=str(val)
                    if sval.startswith("#"): continue
                    v.text=sval; c.set("t","str")
                n+=1
            data=etree.tostring(root,xml_declaration=True,encoding="UTF-8",standalone=True)
        zout.writestr(item,data)
    zout.close(); return n,miss
if __name__=="__main__":
    xlsx,js,fname,out=sys.argv[1:5]
    V=json.load(open(js)); print(inject(xlsx,V,fname,out))

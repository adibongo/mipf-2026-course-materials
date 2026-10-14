import sys, os, html
sys.path.insert(0, os.path.dirname(__file__))
from mipf_data import *
OUT=sys.argv[1]+"/website"; E=html.escape
def tm(x): return x.replace(".",":")

CSS = """
:root{--navy:#141B4D;--blue:#0B5E82;--teal:#1C7293;--gold:#D99A2B;--gold-t:#A8700F;--ink:#1A2233;--slate:#5C6B7A;--mist:#F3F6F9;--rule:#E1E7EE;--bg:#fff;--card:#fff}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--ink:#E6EBF2;--slate:#9AA8B8;--mist:#10162F;--rule:#26305A;--bg:#0B1030;--card:#121A3F;--navy:#C9D3F5;--gold-t:#E9B24E}}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;font-family:Lato,Calibri,"Segoe UI",system-ui,sans-serif;color:var(--ink);background:var(--bg);line-height:1.6;font-size:17px}
h1,h2,h3,h4{font-family:"Source Serif 4",Cambria,Georgia,serif;color:var(--navy);line-height:1.2;margin:0 0 .5em}
a{color:var(--blue)}@media (prefers-color-scheme:dark){a{color:#7FC4E0}}
.wrap{max-width:1080px;margin:0 auto;padding:0 16px}
header.site{position:sticky;top:0;z-index:20;background:#141B4D;color:#fff;border-bottom:3px solid var(--gold)}
header.site .wrap{display:flex;align-items:center;gap:14px;min-height:62px;flex-wrap:wrap;padding-top:6px;padding-bottom:6px}
.brand{display:flex;align-items:center;gap:12px;text-decoration:none;color:#fff}
.brand .lbs{background:#fff;border-radius:6px;padding:4px 8px;height:44px;display:flex;align-items:center}
.brand .lbs img{height:34px;width:auto;display:block}
.brand .hex{height:46px;width:46px}
.brand span{font-family:"Source Serif 4",Georgia,serif;font-weight:600;font-size:1.05rem;line-height:1.15}
.brand small{display:block;font-family:Lato,sans-serif;font-weight:400;font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;color:#D8DEF5}
nav.main{margin-left:auto;display:flex;gap:2px;flex-wrap:wrap}
nav.main a{color:#fff;text-decoration:none;padding:7px 11px;border-radius:6px;font-size:.92rem}
nav.main a:hover,nav.main a[aria-current=page]{background:rgba(255,255,255,.14)}
nav.main a[aria-current=page]{box-shadow:inset 0 -2px 0 var(--gold)}
.hero{background:linear-gradient(135deg,#141B4D 0%,#0B5E82 100%);color:#fff;padding:44px 0 40px}
.hero h1{color:#fff;font-size:clamp(1.9rem,4.6vw,3rem)}
.hero p{color:#E4EAF8;max-width:46em}
.hero .row{display:flex;gap:28px;align-items:center;flex-wrap:wrap}
.hero .stamp{width:150px;height:150px;flex:none}
.kicker{font-weight:700;font-size:.82rem;letter-spacing:.12em;text-transform:uppercase;color:var(--gold)}
.hero .kicker{color:#F0C06A}
.btn{display:inline-block;background:var(--gold);color:#141B4D;font-weight:700;text-decoration:none;padding:10px 18px;border-radius:8px;margin:6px 8px 0 0}
.btn.ghost{background:transparent;color:#fff;border:2px solid rgba(255,255,255,.6)}
main{padding:30px 0 50px}
h2.sec{border-bottom:3px solid var(--gold);padding-bottom:.25rem;margin-top:2.2rem}
.grid{display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(240px,1fr))}
.card{background:var(--card);border:1px solid var(--rule);border-radius:12px;padding:16px;text-decoration:none;color:inherit;display:block}
a.card:hover{border-color:var(--teal);box-shadow:0 4px 14px rgba(20,27,77,.12)}
.card .top{display:flex;gap:12px;align-items:center;margin-bottom:8px}
.card .top svg{width:54px;height:54px;flex:none}
.card h3{font-size:1.02rem;margin:0}
.card .d{font-size:.84rem;color:var(--slate);font-weight:700;letter-spacing:.03em}
.card p{margin:.3rem 0 0;font-size:.92rem;color:var(--slate)}
.rest{border:2px dashed var(--rule);border-radius:12px;display:flex;align-items:center;justify-content:center;text-align:center;color:var(--slate);padding:16px;font-size:.92rem}
.chip{display:inline-block;font-size:.76rem;font-weight:700;padding:2px 9px;border-radius:999px;background:var(--mist);color:var(--blue);border:1px solid var(--rule);margin:2px 4px 2px 0}
.chip.gold{background:#FBF0D9;color:#7A4E06;border-color:#EBCB86}.chip.sheet{font-family:ui-monospace,Menlo,monospace;background:#E7F1F6;color:#0B5E82}
.chip.pack{background:#EEF0FA;color:#2F3A7A}
.hero-sub{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));margin-top:22px}
.stat{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.22);border-radius:10px;padding:10px 14px}
.stat b{display:block;font-size:1.05rem}.stat span{font-size:.82rem;color:#D8DEF5}
.timeline{margin:20px 0;padding:0;list-style:none}
.slot{display:grid;grid-template-columns:118px 1fr;gap:14px;margin:0 0 14px}
.slot .t{font-weight:800;color:var(--navy);padding-top:14px;font-variant-numeric:tabular-nums;font-size:.95rem}
.slot .t small{display:block;font-weight:400;color:var(--slate)}
.slot .b{background:var(--card);border:1px solid var(--rule);border-left:5px solid var(--teal);border-radius:10px;padding:14px 16px}
.slot.break .b{background:var(--mist);border-left-color:var(--gold);padding:10px 16px;color:var(--slate)}
.slot.break h3{font-size:.98rem;margin:0;font-family:Lato,sans-serif;font-weight:700;color:var(--slate)}
.slot h3{font-size:1.12rem;margin:0 0 6px}
.meta{font-size:.86rem;color:var(--slate);margin-bottom:6px}
.slot dl{margin:8px 0 0}.slot dt{font-weight:800;font-size:.76rem;letter-spacing:.07em;text-transform:uppercase;color:var(--gold-t);margin-top:9px}
.slot dd{margin:2px 0 0;font-size:.95rem}
details{margin-top:10px;border-top:1px dashed var(--rule);padding-top:8px}summary{cursor:pointer;font-weight:700;color:var(--blue);font-size:.92rem}
ul.rd{list-style:none;padding:0;margin:8px 0 0}ul.rd li{padding:5px 0;font-size:.93rem;border-bottom:1px solid var(--rule)}ul.rd li:last-child{border:0}
.pager{display:flex;justify-content:space-between;gap:12px;margin-top:30px;flex-wrap:wrap}
.pager a{background:var(--mist);border:1px solid var(--rule);padding:10px 16px;border-radius:8px;text-decoration:none;font-weight:700}
table{border-collapse:collapse;width:100%;font-size:.93rem}th{background:#141B4D;color:#fff;text-align:left;padding:8px 10px}td{border-bottom:1px solid var(--rule);padding:8px 10px;vertical-align:top}
td.m{font-family:ui-monospace,Menlo,monospace;font-weight:700;color:var(--blue)}
.note{background:#FBF0D9;border-left:5px solid var(--gold);padding:10px 14px;border-radius:6px;color:#4A3004;font-size:.93rem}
@media (prefers-color-scheme:dark){.note{background:#2A2210;color:#F2DCA8}.chip.gold{background:#2A2210;color:#F2DCA8}.chip.sheet{background:#0E2A38;color:#8FD0EA}.chip.pack{background:#1B2255;color:#B9C4F3}}
.faculty{display:grid;gap:20px;grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}
.person{background:var(--card);border:1px solid var(--rule);border-radius:12px;padding:18px}
.person img{width:96px;height:96px;object-fit:cover;border-radius:50%;float:left;margin:0 14px 6px 0;border:3px solid var(--gold)}
.person .ph{width:96px;height:96px;border-radius:50%;float:left;margin:0 14px 6px 0;background:#141B4D;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;border:3px solid var(--gold)}
footer.site{background:#141B4D;color:#D8DEF5;padding:26px 0;font-size:.88rem;border-top:3px solid var(--gold)}
footer.site .wrap{display:flex;gap:20px;align-items:center;flex-wrap:wrap}footer.site .lbs{background:#fff;padding:5px 9px;border-radius:6px}footer.site img{height:36px;display:block}footer.site img.fhex{height:46px}
footer.site a{color:#F0C06A}
@media (max-width:640px){.slot{grid-template-columns:1fr;gap:4px}.slot .t{padding-top:0}nav.main{margin-left:0}body{font-size:16px}}
"""
def hexsvg(label, sub=None, size=54, mono=False):
    cols=["#D99A2B","#1C7293","#0B5E82","#1F2A66","#0B5E82","#141B4D"]
    pts=["512,25.6 90.77,268.8 212.92,339.33 512,166.66","90.77,268.8 90.77,755.2 212.92,684.67 212.92,339.33",
         "90.77,755.2 512,998.4 512,857.34 212.92,684.67","512,998.4 933.23,755.2 811.08,684.67 512,857.34",
         "933.23,755.2 933.23,268.8 811.08,339.33 811.08,684.67","933.23,268.8 512,25.6 512,166.66 811.08,339.33"]
    s=f'<svg viewBox="0 0 1024 1024" role="img" aria-label="{E(label)}" xmlns="http://www.w3.org/2000/svg"><polygon points="512,166.66 212.92,339.33 212.92,684.67 512,857.34 811.08,684.67 811.08,339.33" fill="#fff"/>'
    for p,c in zip(pts,cols): s+=f'<polygon points="{p}" fill="{c}"/>'
    s+='<polygon points="512,25.6 90.77,268.8 90.77,755.2 512,998.4 933.23,755.2 933.23,268.8" fill="none" stroke="#141B4D" stroke-width="3"/>'
    if sub:
        s+=f'<text x="512" y="440" text-anchor="middle" fill="#0B5E82" font-family="Lato,Arial,sans-serif" font-weight="800" font-size="120" letter-spacing="8">{sub}</text>'
        s+=f'<text x="512" y="700" text-anchor="middle" fill="#141B4D" font-family="Lato,Arial,sans-serif" font-weight="800" font-size="290">{label}</text>'
    else:
        s+=f'<text x="512" y="578" text-anchor="middle" fill="#141B4D" font-family="Lato,Arial,sans-serif" font-weight="800" font-size="196" letter-spacing="-6">{label}</text>'
    return s+'</svg>'

REPO='https://github.com/adibongo/mipf-2026-course-materials'
GH_SVG='<svg viewBox="0 0 16 16" width="20" height="20" fill="currentColor" aria-hidden="true"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82a7.6 7.6 0 0 1 4 0c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8z"/></svg>'
NAV=[("index.html","Programme"),("day1.html","Timetable"),("slides.html","Slides"),("readings.html","Readings"),("model.html","TrainStat model"),("faculty.html","Faculty"),("info.html","Practical info")]
def page(fn,title,body,cur=None,desc=""):
    nav="".join(f'<a href="{h}"{" aria-current=page" if (cur==h) else ""}>{t}</a>' for h,t in NAV)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)} · MIPF October 2026</title><meta name="description" content="{E(desc or 'Mastering Infrastructure and Project Finance Boot Camp, Lagos Business School, 14–21 October 2026')}">
<link rel="icon" href="assets/logo/mipf_hex.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="assets/logo/bongo_ai_hex_256.png"><link rel="stylesheet" href="assets/css/mipf.css"></head><body>
<header class="site"><div class="wrap"><a class="brand" href="index.html"><span class="lbs"><img src="assets/logo/lbs-logo.png" alt="Lagos Business School, Pan-Atlantic University"></span>
<img class="hex" src="assets/logo/mipf_hex_256.png" alt="MIPF hex"><img class="hex" src="assets/logo/bongo_ai_hex_dark_256.png" alt="bongo.ai hex"><span>Mastering Infrastructure &amp; Project Finance<small>Boot Camp · October 2026</small></span></a><nav class="main" aria-label="Main">{nav}<a href="{REPO}" target="_blank" rel="noopener" aria-label="GitHub repository" title="GitHub repository" style="display:flex;align-items:center">{GH_SVG}</a></nav></div></header>
{body}
<footer class="site"><div class="wrap"><span class="lbs"><img src="assets/logo/lbs-logo.png" alt="Lagos Business School"></span><img class="fhex" src="assets/logo/mipf_hex_256.png" alt="MIPF"><img class="fhex" src="assets/logo/bongo_ai_hex_dark_256.png" alt="bongo.ai">
<div>Lagos Business School, Pan-Atlantic University · Ajah, Lagos<br><a href="{REPO}/blob/main/course-materials/website/{fn}.html" target="_blank" rel="noopener">View source</a> · <a href="{REPO}/issues/new" target="_blank" rel="noopener">Report an issue</a> · <a href="{REPO}" target="_blank" rel="noopener">GitHub repository</a><br>Mastering Infrastructure and Project Finance Boot Camp · 14–21 October 2026 · Prof Bongo Adi · <a href="tel:+2347061648699">+234 706 164 8699</a> · <a href="mailto:badi@lbs.edu.ng">badi@lbs.edu.ng</a> · <a href="mailto:bongo.adi@fulbrightmail.org">bongo.adi@fulbrightmail.org</a></div></div></footer></body></html>'''
def write(fn,s): open(os.path.join(OUT,fn),"w",encoding="utf8").write(s)
open(OUT+"/assets/css/mipf.css","w").write(CSS)

def rlist(keys):
    out=[]
    for k in keys:
        r=R[k]
        if r["kind"]=="web": out.append(f'<li><a href="{r["u"]}" target="_blank" rel="noopener">{E(r["t"])}</a> <span class="chip">link</span><br><small>{E(r["s"])}</small></li>')
        elif r["kind"]=="hosted": out.append(f'<li><a href="materials/{r["f"]}" download>{E(r["t"])}</a> <span class="chip gold">download</span><br><small>{E(r["s"])}</small></li>')
        elif r.get("od"):
            links="".join(f'<br><a href="{u}" target="_blank" rel="noopener">{E(l)}</a>' for l,u in r["od"])
            out.append(f'<li><b>{E(r["t"])}</b> <span class="chip pack">OneDrive</span>{links}<br><small>{E(r["s"])}</small></li>')
        else: out.append(f'<li>{E(r["t"])} <span class="chip pack">in class (Harvard)</span><br><small>{E(r["s"])}</small></li>')
    return '<ul class="rd">'+"".join(out)+"</ul>"

# ---------------------------------------------------------------- index
cards=[]
for dy in DAYS:
    cards.append(f'<a class="card" href="day{dy["n"]}.html"><div class="top">{hexsvg(str(dy["n"]),"DAY")}<div><div class="d">{E(dy["short"].upper())}</div><h3>{E(dy["mtitle"])}</h3></div></div><p>{E(dy["fac"])}</p></a>')
    if dy["n"]==4: cards.append('<div class="rest"><div><b>Sunday 18 October</b><br>Rest day: no sessions</div></div>')
mods="".join(f'<div class="card"><h3>{E(h)}</h3><p>{E(t)}</p></div>' for h,t in MODULES)
body=f'''<section class="hero"><div class="wrap"><div class="row"><div class="stamp">{hexsvg("MIPF")}</div><div class="stamp"><img src="assets/logo/bongo_ai_hex_dark.png" alt="bongo.ai" style="width:150px;height:150px"></div><div>
<div class="kicker">Open enrolment · Lagos Business School</div><h1>Mastering Infrastructure and Project Finance Boot Camp</h1>
<p>Structure, negotiate and model limited-recourse infrastructure financings. Seven teaching days, four modules and one running Excel model, led by Lagos Business School faculty and project-finance practitioners.</p>
<a class="btn" href="day1.html">See the timetable</a><a class="btn ghost" href="info.html">Practical information</a></div></div>
<div class="hero-sub"><div class="stat"><b>14–21 October 2026</b><span>Wednesday to Wednesday (rest day Sunday 18th)</span></div><div class="stat"><b>{E(VENUE)}</b><span>{E(PLACE)}</span></div><div class="stat"><b>7 teaching days</b><span>Cases, legal, finance and hands-on modelling</span></div></div></div></section>
<main><div class="wrap"><h2 class="sec">The week at a glance</h2><div class="grid">{"".join(cards)}</div>
<h2 class="sec">Four modules</h2><div class="grid">{mods}</div>
<h2 class="sec">Who it is for</h2><p>{E(PROFILE)}</p>
<h2 class="sec">What you leave with</h2><p>{E(OBJECTIVE)}</p>
<p class="note"><b>After the boot camp:</b> {E(CAPSTONE)}</p><p class="note">All course materials (syllabus, website, tutorial decks and Excel models) are on <a href="{REPO}" target="_blank" rel="noopener">GitHub</a>.</p></div></main>'''
write("index.html",page("index","Programme",body,"index.html"))

# ---------------------------------------------------------------- day pages
for idx,dy in enumerate(DAYS):
    items=[]; sn=0
    for s in dy["sessions"]:
        t=f'{tm(s["start"])} – {tm(s["end"])}'
        if s["kind"]=="break": items.append(f'<li class="slot break"><div class="t">{t}</div><div class="b"><h3>{E(s["title"])}</h3></div></li>'); continue
        dl=""
        if s["desc"]: dl+=f'<dt>Focus</dt><dd>{E(s["desc"])}</dd>'
        if s["exercise"]: dl+=f'<dt>Exercise</dt><dd>{E(s["exercise"])}</dd>'
        if s["sheets"]: dl+='<dt>TrainStat sheets</dt><dd>'+"".join(f'<span class="chip sheet">{x}</span>' for x in s["sheets"])+'</dd>'
        if s["note"]: dl+=f'<dt>Note</dt><dd>{E(s["note"])}</dd>'
        sn+=1
        det=""
        sd=SESSION_DECKS.get((dy["n"],sn),[])
        if sd:
            det+="<details open><summary>Slides for this session</summary><ul class=\"rd\">"+"".join(f'<li><a href="{DECKS[k]["f"]}" download>{E(DECKS[k]["t"])}</a> <span class="chip gold">slides {a} to {b}</span><br><small>{E(w)}</small></li>' for k,a,b,w in sd)+"</ul></details>"
        if s["read"]: det+=f'<details><summary>Reading materials ({len(s["read"])})</summary>{rlist(s["read"])}</details>'
        if s["alt"]: det+=f'<details><summary>Alternative reading: cases ({len(s["alt"])})</summary>{rlist(s["alt"])}</details>'
        items.append(f'<li class="slot"><div class="t">{t}</div><div class="b"><h3>{E(s["title"])}</h3><div class="meta"><span class="chip">{E(s["mode"])}</span> Facilitator: <b>{E(s["fac"])}</b></div><dl>{dl}</dl>{det}</div></li>')
    prev=f'<a href="day{idx}.html">← Day {idx}</a>' if idx>0 else '<span></span>'
    nxt=f'<a href="day{idx+2}.html">Day {idx+2} →</a>' if idx<len(DAYS)-1 else '<a href="readings.html">Reading list →</a>'
    extra=""
    extra+='<h2 class="sec">Tutorial decks for this day</h2><div class="grid">'+"".join(f'<div class="card"><p><b>{E(DECKS[k]["t"])}</b></p><p>{DECKS[k]["n"]} slides · <a href="{DECKS[k]["f"]}" download>Download .pptx</a></p></div>' for k in DAY_DECKS[dy["n"]])+'</div>'
    if dy["n"]==1:
        extra='<h2 class="sec">Day 1 pack</h2><div class="grid">'+"".join(f'<div class="card"><p><b>{E(R[k]["t"])}</b></p><p><a href="materials/{R[k]["f"]}" download>Download</a></p></div>' for k in ("primer","workbook","deck1","sahel"))+'</div><p class="note">Please read the pre-read primer (about 15 minutes) before Day 1. The Harvard cases from earlier editions are listed under <i>Alternative reading</i> in each session.</p>'
    if dy["n"]>=3 and dy["n"]<=7:
        extra+=f'<p class="note">Bring a laptop with desktop Excel and the <a href="materials/{R["trainstat"]["f"]}" download>TrainStat start model</a> open. See the <a href="model.html">model guide</a>.</p>'
    body=f'''<section class="hero" style="padding:28px 0"><div class="wrap"><div class="row"><div class="stamp" style="width:110px;height:110px">{hexsvg(str(dy["n"]),"DAY")}</div><div><div class="kicker">Module {dy["module"]} · {E(dy["date"])}</div><h1 style="font-size:clamp(1.5rem,3.6vw,2.3rem)">{E(dy["mtitle"])}</h1><p>{E(dy["blurb"])}</p></div></div></div></section>
<main><div class="wrap"><ol class="timeline">{"".join(items)}</ol>{extra}<div class="pager">{prev}{nxt}</div></div></main>'''
    write(f'day{dy["n"]}.html',page(f'day{dy["n"]}',f'Day {dy["n"]}: {dy["mtitle"]}',body,"day1.html",desc=dy["blurb"][:150]))

# ---------------------------------------------------------------- slides page
rows=""
for k,dk in DECKS.items():
    ses=[(d_,i_,a,b,w) for (d_,i_),lst in SESSION_DECKS.items() for (kk,a,b,w) in lst if kk==k]
    li="".join(f'<li><a href="day{d_}.html">Day {d_}, session {i_}</a>: slides {a} to {b} ({E(w)})</li>' for d_,i_,a,b,w in sorted(ses))
    rows+=f'<div class="card" style="margin-bottom:14px"><h3>{E(dk["t"])}</h3><p>{dk["n"]} slides · <a href="{dk["f"]}" download>Download .pptx</a></p><ul>{li}</ul></div>'
body=f'<section class="hero" style="padding:28px 0"><div class="wrap"><div class="kicker">Slides</div><h1 style="font-size:2rem">Tutorial decks, session by session</h1><p>Each deck is attached to its day and to the sessions it supports, with the slide range. Open the files in PowerPoint, Keynote or Google Slides. These are the participants' editions: exercise answers and speaker notes are withheld and are reviewed together in class.</p></div></section><main><div class="wrap">{rows}</div></main>'
write("slides.html",page("slides","Slides",body,"slides.html"))

# ---------------------------------------------------------------- readings
secs=""
for kind,ttl,sub in (("hosted","Provided on this site","Download and read before the day indicated."),
                     ("web","Public links","External sites; wording and versions may change."),
                     ("od","Course readings on OneDrive","Each item opens in OneDrive. Access follows the sharing settings of the course folder: if a link asks you to sign in, contact the course office."),
                     ("pack","Harvard cases","Taught in class from the licensed course pack; not available online.")):
    keys=[k for k,r in R.items() if (r["kind"]=="pack" and r.get("od"))] if kind=="od" else [k for k,r in R.items() if r["kind"]==kind and not r.get("od")]
    secs+=f'<h2 class="sec">{ttl}</h2><p>{sub}</p>'+rlist(keys)
body=f'<section class="hero" style="padding:28px 0"><div class="wrap"><div class="kicker">Reading list</div><h1 style="font-size:2rem">Readings, cases and files</h1><p>Each session page lists its own readings; this page collects everything in one place. The Harvard cases from earlier editions (Argentina Power, Chad-Cameroon, BP Amoco) are retained as alternative reading.</p></div></section><main><div class="wrap">{secs}</div></main>'
write("readings.html",page("readings","Readings",body,"readings.html"))

# ---------------------------------------------------------------- model
import json as _json
chlog="".join(f'<li>{E(x)}</li>' for x in _json.load(open(os.path.join(os.path.dirname(__file__),'changes1.json'))))
facts="".join(f'<tr><td class="m">{E(a)}</td><td>{E(b)}</td></tr>' for a,b in MODEL["facts"])
sheets="".join(f'<tr><td class="m">{a}</td><td>{E(b)}</td><td>{E(c)}</td></tr>' for a,b,c in MODEL["sheets"])
bysheet={}
for dy in DAYS:
    for s in dy["sessions"]:
        for sh in s.get("sheets",[]): bysheet.setdefault(sh,set()).add(dy["n"])
usage="".join(f'<tr><td class="m">{a}</td><td>'+(" ".join(f'<a class="chip" href="day{n}.html">Day {n}</a>' for n in sorted(bysheet.get(a,[]))) or "–")+'</td></tr>' for a,_,_ in MODEL["sheets"])
body=f'''<section class="hero" style="padding:28px 0"><div class="wrap"><div class="kicker">Days 3 to 7</div><h1 style="font-size:2rem">The TrainStat start model</h1><p>One workbook carries the whole modelling track. Days 4 and 5 complete the operating three-statement model. Days 6 and 7 extend it into a project finance model with construction, funding, cover ratios and debt sculpting.</p><a class="btn" href="materials/{R["trainstat"]["f"]}" download>Download TrainStat_StartModel.xlsx</a></div></section>
<main><div class="wrap"><h2 class="sec">What is in the model</h2><table><tbody>{facts}</tbody></table>
<p class="note">Values read from the start model as supplied (constants sheet InpC). Participants change them during the exercises.</p>
<h2 class="sec">Prompt book and interactive model</h2><div class="grid"><div class="card"><p><b>Model Prompt Book</b></p><p>Everything that builds the model: 24 build blocks, each with the specification, five ready-to-paste prompts (tutor, formula generator, script builder, independent replica, auditor), checkpoints, options and failure modes.</p><p><a class="btn" href="materials/promptbook/MIPF_Model_Prompt_Book.html">Open the book</a> <a href="materials/promptbook/MIPF_Model_Prompt_Book.qmd" download>QMD source</a></p></div><div class="card"><p><b>MIPF Model Builder (interactive)</b></p><p>Runs the whole model in your browser. Change any input or option and see the statements, cover ratios, checks, scenarios and sensitivities; export prompts tailored to your inputs.</p><p><a class="btn" href="materials/promptbook/mipf_model_builder.html">Open the app</a></p></div></div>
<h2 class="sec">Workbook map</h2><table><thead><tr><th>Sheet</th><th>Purpose</th><th>Contents</th></tr></thead><tbody>{sheets}</tbody></table>
<h2 class="sec">Where each sheet is used</h2><table><thead><tr><th>Sheet</th><th>Sessions</th></tr></thead><tbody>{usage}</tbody></table>
<h2 class="sec">What we corrected in the supplied workbook</h2><p>The workbook distributed as <b>TrainStat_StartModel.xlsx</b> is the corrected version. Changes from the original file supplied to the course:</p><ol>{chlog}</ol><h2 class="sec">Modelling conventions</h2><ul><li>Inputs, workings, outputs and checks on separate sheets; one formula per row, copied across the timeline.</li><li>Every run is logged on <b>Track</b> so scenarios can be compared.</li><li>The balance-sheet check on FinStat must be zero before moving on.</li></ul>
<p>Further guidance: <a href="{R["w_fast"]["u"]}" target="_blank" rel="noopener">the FAST Standard</a>.</p></div></main>'''
write("model.html",page("model","TrainStat model",body,"model.html"))

# ---------------------------------------------------------------- faculty
ph={"Prof. Bongo Adi":"assets/img/adi.png","Promise Godbold":"assets/img/godbold.jpg","Michelle Chikezie, LLB, LLM":"assets/img/chikezie.jpg"}
fc=""
for f in FACULTY:
    im=f'<img src="{ph[f["name"]]}" alt="{E(f["name"])}">' if f["name"] in ph else '<div class="ph">MC</div>'
    bio=f["bio"] if f["name"]!="Prof. Bongo Adi" else f["bio"][:1]+f["bio"][2:]
    fc+=f'<article class="person">{im}<h3>{E(f["name"])}</h3><div class="meta">{E(f["role"])}</div>'+"".join(f'<p>{E(t)}</p>' for t in bio[:3])+"</article>"
body=f'<section class="hero" style="padding:28px 0"><div class="wrap"><div class="kicker">Faculty</div><h1 style="font-size:2rem">Who teaches the boot camp</h1></div></section><main><div class="wrap"><div class="faculty">{fc}</div></div></main>'
write("faculty.html",page("faculty","Faculty",body,"faculty.html"))

# ---------------------------------------------------------------- info
body=f'''<section class="hero" style="padding:28px 0"><div class="wrap"><div class="kicker">Practical information</div><h1 style="font-size:2rem">Before you come</h1></div></section>
<main><div class="wrap"><h2 class="sec">When and where</h2><table><tbody>
<tr><td class="m">Dates</td><td>Wednesday 14th to Wednesday 21st October 2026, including Saturday 17th. Sunday 18th is a rest day.</td></tr>
<tr><td class="m">Venue</td><td>{E(VENUE)}, {E(PLACE)}</td></tr>
<tr><td class="m">Format</td><td>Open enrolment. Lectures, case discussion, group sessions and hands-on Excel modelling.</td></tr>
<tr><td class="m">Daily rhythm</td><td>Start 09:00. A coffee break mid-morning and lunch from 14:00 to 14:45. Finish 16:30 on Days 1–2 and 17:00 on Days 3–7 (see each day page).</td></tr></tbody></table>
<h2 class="sec">What to bring</h2><ul><li>A laptop with desktop Excel (Windows or Mac) and the <a href="materials/{R["trainstat"]["f"]}" download>TrainStat start model</a>, from Day 3.</li><li>The Day 1 <a href="materials/{R["primer"]["f"]}" download>pre-read primer</a>, read in advance.</li></ul>
<h2 class="sec">Contact</h2><p><b>Prof Bongo Adi</b>, Course Director, Lagos Business School<br>Phone / WhatsApp: <a href="tel:+2347061648699">+234 706 164 8699</a><br>Email: <a href="mailto:badi@lbs.edu.ng">badi@lbs.edu.ng</a><br>Fulbright email: <a href="mailto:bongo.adi@fulbrightmail.org">bongo.adi@fulbrightmail.org</a></p></div></main>'''
write("info.html",page("info","Practical information",body,"info.html"))
os.makedirs(OUT+"/assets/img",exist_ok=True)
print("site ok")

"""Assemble the standalone interactive app: engine + data + UI + logos in one HTML file (works offline)."""
import json, base64, sys, os
ROOT = sys.argv[1]
rd = lambda p: open(f"{ROOT}/{p}", encoding="utf-8").read()
b64 = lambda f: "data:image/png;base64," + base64.b64encode(open(f"{ROOT}/assets/{f}", "rb").read()).decode()
J = lambda f: json.load(open(f"{ROOT}/data/{f}", encoding="utf-8"))
data = dict(inputs=J("inputs.json"), pb=J("promptbook.json"), numbers=J("numbers.json"), atlasPF=J("atlas_pf.json"), atlasStart=J("atlas_start.json"))
for a in (data["atlasPF"], data["atlasStart"]):
    for x in a:
        for k in ("lv",):
            if isinstance(x.get(k), str) and len(x[k]) > 40: x[k] = x[k][:40]
import re
def with_auto_theme(css):
    """Every :root[data-theme=dark] rule is mirrored for data-theme=auto inside prefers-color-scheme:dark, so a computer in dark mode gets the same palette as the forced dark theme. Hand-written auto blocks are dropped and regenerated, so the two can never drift apart."""
    css = re.sub(r"@media \(prefers-color-scheme:dark\)\{(?:[^{}]|\{[^{}]*\})*\}\n?", "", css)
    out = []
    for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        sel = sel.strip()
        if sel.startswith("@"): continue
        parts = [x.strip() for x in sel.split(",")]
        if all(x.startswith(":root[data-theme=dark]") for x in parts):
            out.append(",".join(x.replace("data-theme=dark", "data-theme=auto") for x in parts) + "{" + body + "}")
    return css + "\n@media (prefers-color-scheme:dark){" + "".join(out) + "}\n"
html = rd("app/app.html")
html = html.replace("/*CSS*/", with_auto_theme(rd("app/app.css"))).replace("/*ENGINE*/", rd("src/engine.js")).replace("/*APP*/", rd("app/app.js"))
html = html.replace("/*DATA*/", json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))
for k, f in (("LBS", "lbs-logo.png"), ("MIPF", "mipf_hex_256.png"), ("BONGO", "bongo_ai_hex_256.png")): html = html.replace(f"/*{k}*/", b64(f))
open(f"{ROOT}/mipf_model_builder.html", "w", encoding="utf-8").write(html)
print("app written", len(html) // 1024, "KB")

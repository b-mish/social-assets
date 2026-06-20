# -*- coding: utf-8 -*-
import os
BASE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(BASE, "img").replace("\\", "/")

ACCENT = "#E08A3C"   # warm terracotta/gold
slides = [
    # (file, image, layout, eyebrow, title, subtitle)
    ("slide1", "25252514.jpg", "cover", "קיץ 2026 · יולי–אוגוסט", "3 אירועים<br>בגיאורגיה", "ששווה לתכנן סביבם טיול"),
    ("slide2", "16330998.jpg", "event", "01", "פסטיבל הג'אז<br>של הים השחור", "בטומי · 10–12 ביולי"),
    ("slide3", "29682410.jpg", "event", "02", "ארט-ג'ין", "טביליסי · יולי"),
    ("slide4", "26556152.jpg", "event", "03", "טושטובה", "חבל טושטי · סביב 21 ביולי"),
    ("slide5", "17550887.jpg", "cta",   "", "מתכננים טיול<br>לגיאורגיה?", "georgia-travel.co.il"),
]

TPL = """<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Rubik:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1080px;overflow:hidden}}
.stage{{position:relative;width:1080px;height:1080px;font-family:'Rubik',Arial,sans-serif}}
.bg{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.shade{{position:absolute;inset:0;background:linear-gradient(to top,rgba(15,12,10,.82) 0%,rgba(15,12,10,.30) 45%,rgba(15,12,10,.10) 70%,rgba(15,12,10,.45) 100%)}}
.brand{{position:absolute;top:54px;right:60px;color:#fff;font-weight:700;font-size:30px;letter-spacing:.5px;text-shadow:0 2px 8px rgba(0,0,0,.5)}}
.brand span{{color:{accent}}}
.wrap{{position:absolute;right:60px;left:60px;bottom:70px;text-align:right}}
.eyebrow{{display:inline-block;color:{accent};font-weight:900;font-size:34px;letter-spacing:2px;margin-bottom:14px}}
.num{{font-size:120px;line-height:.9;font-weight:900;color:{accent};text-shadow:0 4px 18px rgba(0,0,0,.5)}}
.title{{color:#fff;font-weight:900;font-size:88px;line-height:1.08;text-shadow:0 4px 20px rgba(0,0,0,.55)}}
.sub{{color:#f3ece2;font-weight:500;font-size:46px;margin-top:18px;text-shadow:0 2px 12px rgba(0,0,0,.5)}}
.rule{{width:120px;height:6px;background:{accent};border-radius:3px;margin:0 0 28px auto}}
/* cover */
.cover .wrap{{bottom:auto;top:50%;transform:translateY(-50%)}}
.cover .title{{font-size:104px}}
.cover .eyebrow{{font-size:38px}}
/* cta */
.cta .title{{font-size:92px}}
.cta .sub{{color:{accent};font-weight:700;font-size:52px;direction:ltr;text-align:right}}
</style></head>
<body><div class="stage {layout}">
<img class="bg" src="file:///{img}">
<div class="shade"></div>
<div class="brand">georgia<span>-travel</span>.co.il 🇬🇪</div>
<div class="wrap">{inner}</div>
</div></body></html>"""

for fn, img, layout, eyebrow, title, sub in slides:
    if layout == "event":
        inner = f'<div class="num">{eyebrow}</div><div class="rule"></div><div class="title">{title}</div><div class="sub">{sub}</div>'
    elif layout == "cover":
        inner = f'<div class="eyebrow">{eyebrow}</div><div class="title">{title}</div><div class="sub">{sub}</div>'
    else:  # cta
        inner = f'<div class="title">{title}</div><div class="rule" style="margin-top:24px"></div><div class="sub">{sub}</div>'
    html = TPL.format(accent=ACCENT, layout=layout, img=f"{IMG}/{img}", inner=inner)
    with open(os.path.join(BASE, fn + ".html"), "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", fn + ".html")

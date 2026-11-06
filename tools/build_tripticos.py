"""Genera los trípticos en PDF, color y blanco y negro.

Uso: python3 tools/build_tripticos.py [dieta ...]   (sin argumentos: todas)
Lee src/tripticos/<dieta>.html y escribe site/tripticos/<dieta>.pdf y <dieta>-bn.pdf.
Usa fuentes estáticas (tools/fonts) para que los PDF pesen ~100 KB.
"""
import asyncio, os, sys, subprocess, glob
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC, OUT, FONTS = os.path.join(ROOT, "src/tripticos"), os.path.join(ROOT, "site/tripticos"), os.path.join(ROOT, "tools/fonts")
FACES = [("BricoStatic", w) for w in (600, 700, 800)] + [("NunitoStatic", w) for w in (400, 600, 700, 800)]
FONT_CSS = "".join(f"@font-face{{font-family:'{f}';src:url('file://{FONTS}/{f}-{w}.ttf');font-weight:{w}}}" for f, w in FACES)
FONT_CSS += f"@font-face{{font-family:'IBM Plex Mono';src:url('file://{FONTS}/IBMPlexMono-Medium.ttf');font-weight:500}}"
FONT_CSS += ":root{--f-display:'BricoStatic',sans-serif!important;--f-body:'NunitoStatic',sans-serif!important}body{font-family:'NunitoStatic',sans-serif}"

async def main(slugs):
    bn = open(os.path.join(SRC, "bn.css")).read()
    async with async_playwright() as pw:
        br = await pw.chromium.launch(executable_path="/usr/bin/google-chrome" if os.path.exists("/usr/bin/google-chrome") else None)
        pg = await br.new_page()
        for slug in slugs:
            src = open(os.path.join(SRC, slug + ".html")).read().replace('font-family="Bricolage Grotesque"', 'font-family="BricoStatic"')
            for suffix, extra in (("", ""), ("-bn", bn)):
                html = src.replace("</head>", f"<style>{FONT_CSS}{extra}</style></head>")
                tmp = os.path.join(SRC, f".tmp-{slug}{suffix}.html")
                open(tmp, "w").write(html)
                await pg.goto("file://" + tmp); await pg.wait_for_timeout(600)
                raw = tmp.replace(".html", ".pdf")
                await pg.pdf(path=raw, prefer_css_page_size=True, print_background=True)
                out = os.path.join(OUT, f"{slug}{suffix}.pdf")
                subprocess.run(["qpdf", "--object-streams=generate", "--recompress-flate", "--compression-level=9", raw, out], check=True)
                os.remove(tmp); os.remove(raw)
                print(out, os.path.getsize(out))
        await br.close()

slugs = sys.argv[1:] or sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(SRC, "*.html")))
asyncio.run(main(slugs))

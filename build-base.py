"""Inline CSS / JS / images into base-template.html for BASE upload."""
import re
from pathlib import Path

ROOT = Path(__file__).parent
CDN_BASE = "https://cdn.jsdelivr.net/gh/piste-boss/ishikawa-kaitai-LP@main/assets"

html = (ROOT / "base-template.html").read_text(encoding="utf-8")
styles = (ROOT / "styles.css").read_text(encoding="utf-8")
sections = (ROOT / "sections.css").read_text(encoding="utf-8")
script = (ROOT / "script.js").read_text(encoding="utf-8")

# Rewrite asset URL inside CSS (brush-red.png).
styles = styles.replace("url('assets/", f"url('{CDN_BASE}/")
styles = styles.replace('url("assets/', f'url("{CDN_BASE}/')

# Combine CSS into one <style> block.
combined_css = styles + "\n\n/* === sections.css === */\n\n" + sections
style_block = f"<style>\n{combined_css}\n</style>"

# Replace the two <link> stylesheet tags with the inlined <style>.
html = re.sub(
    r'\s*<link rel="stylesheet" href="styles\.css"[^>]*>\s*<link rel="stylesheet" href="sections\.css"[^>]*>',
    "\n  " + style_block,
    html,
)

# Replace <script src="script.js"></script> with inline JS.
html = html.replace(
    '<script src="script.js"></script>',
    f"<script>\n{script}\n</script>",
)

# Rewrite every assets/ image reference.
html = re.sub(r'src="assets/', f'src="{CDN_BASE}/', html)
html = re.sub(r'content="assets/', f'content="{CDN_BASE}/', html)

(ROOT / "base-template.inline.html").write_text(html, encoding="utf-8")
print("Wrote base-template.inline.html — size:", len(html), "bytes")

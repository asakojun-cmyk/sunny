#!/usr/bin/env python3
"""「授業できく」で、聞き終わったら次に進むページの順番(audio/playlist.json)を作る。

順番は、理論家図鑑・ことば図鑑・理論家とピクニックの一覧ページに並んでいる順。
音声(audio/<ページ>/lesson.json)があるページだけを入れる。ページを足したら作り直す。
  ~/voicevox-engine/venv/bin/python scripts/make-lesson-playlist.py
"""
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
out = {}
for section in ("theorists", "terms", "obento"):
    html = (ROOT / section / "index.html").read_text(encoding="utf-8").replace("<wbr>", "")
    seen, items = set(), []
    for slug in re.findall(r'href="[^"]*?%s/([a-z0-9-]+)/"' % section, html):
        if slug in seen or not (ROOT / "audio" / section / slug / "lesson.json").exists():
            continue
        seen.add(slug)
        page = BeautifulSoup((ROOT / section / slug / "index.html").read_text(encoding="utf-8").replace("<wbr>", ""), "html.parser")
        title = page.h1.get_text(" ", strip=True) if section == "obento" else page.select_one(".term-header__name").get_text(strip=True)
        items.append({"u": f"/{section}/{slug}/", "t": title})
    out[section] = items
    print(section, len(items))
(ROOT / "audio" / "playlist.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

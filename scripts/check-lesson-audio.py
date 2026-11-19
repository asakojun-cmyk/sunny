"""授業の音声が、いまのページの本文と合っているかを見る（音声は作らない・VOICEVOX はいらない）。
使い方: ~/voicevox-engine/venv/bin/python scripts/check-lesson-audio.py .
- ok          ＝本文も段落の数も同じ（作り直し不要）
- text_changed＝段落の数は同じで文が変わった（プレーヤーは出るが、音声が古い）→ make-lesson-audio.py で作り直す
- count_off   ＝段落の数がちがう（js/lesson-player.js がプレーヤーを出さない）→ 作り直す
新しい型に入れかえたあと、push の前に必ず回す。2026-11-19 の本番では ok 197・text_changed 17・count_off 22。
"""
import importlib.util, json, sys, hashlib
from pathlib import Path
from bs4 import BeautifulSoup

root = Path(sys.argv[1]).resolve()
spec = importlib.util.spec_from_file_location("mla", str(root / "scripts" / "make-lesson-audio.py"))
mla = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mla)
yomi = json.loads((root / "scripts" / "lesson-yomi.json").read_text(encoding="utf-8"))

res = {"ok": [], "text_changed": [], "count_off": [], "no_page": [], "no_mount": []}
for meta in sorted((root / "audio").glob("*/*/lesson.json")):
    page = str(meta.parent.relative_to(root / "audio"))
    f = root / page / "index.html"
    if not f.exists():
        res["no_page"].append(page); continue
    soup = BeautifulSoup(f.read_text(encoding="utf-8"), "html.parser")
    for w in soup.find_all("wbr"):
        w.decompose()
    els = soup.select(mla.SELECTOR)
    lines = [(mla.who(el, page), mla.spoken_text(el, yomi), "term-section-title" in (el.get("class") or []) or el.name == "h2") for el in els]
    digest = hashlib.sha1(json.dumps([lines, mla.VOICES], ensure_ascii=False).encode()).hexdigest()[:12]
    data = json.loads(meta.read_text(encoding="utf-8"))
    if not soup.select_one("[data-lesson]"):
        res["no_mount"].append(page)
    if len(els) != len(data["segs"]):
        res["count_off"].append(f"{page} (ページ{len(els)}・音声{len(data['segs'])})")
    elif data.get("h") != digest:
        res["text_changed"].append(page)
    else:
        res["ok"].append(page)
for k, v in res.items():
    print(f"{k}: {len(v)}")
    for p in v[:80]:
        print("   ", p)

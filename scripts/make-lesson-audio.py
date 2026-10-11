#!/usr/bin/env python3
"""ページの本文から「授業の音声」を作る(サニー先生=九州そら / モヤン=ずんだもん)。

使い方:
  1. VOICEVOX のエンジンを起動しておく(http://127.0.0.1:50021)
  2. ~/voicevox-engine/venv/bin/python scripts/make-lesson-audio.py theorists/holland
     ページはいくつ並べてもよい。本文が前回と同じページは飛ばす(--force で作り直す)。
     --dry をつけると、音声は作らずに読み方だけ表示する。

できるもの:
  audio/<ページ>/lesson.m4a  … 授業1本ぶんの音声
  audio/<ページ>/lesson.json … どの段落が何秒から何秒までかの表(js/lesson-player.js が読む)

読む場所と順番は SELECTOR で決める。js/lesson-player.js の SELECTOR と必ず同じにすること。
読みまちがいは scripts/lesson-yomi.json に「書き方 → 読み方」を足して直す。
"""
import hashlib
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
import wave
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
ENGINE = "http://127.0.0.1:50021"

# js/lesson-player.js の SELECTOR と同じにする
SELECTOR = ", ".join([
    ".picnic-intro__line p",
    ".episode > h2", ".line__msg", ".okawari > h2", ".okawari__card > p",
    ".term-oneliner .term-section-title", ".term-oneliner .chara-guide__bubble", ".term-oneliner .term-prose p",
    ".term-kids .term-section-title", ".term-kids .term-prose p",
    ".term-analogy .term-section-title", ".term-analogy .term-prose p",
    ".term-life .term-section-title", ".term-life .term-prose p",
    ".term-formal .term-section-title", ".term-formal__box > p:not(.term-update)", ".term-kakomon li",
    ".term-stages .term-section-note:first-of-type", ".term-formal dl > div", ".term-riasec .term-section-note",
    ".term-try .term-section-title", ".term-try .mini-say__bubble",
    ".kw-talk .mini-say__bubble",
    ".term-exam-points .term-section-title", ".term-exam-points li",
    ".term-exam-advice .chara-guide__bubble", ".term-exam-advice .exam-advice__list li",
    ".term-oboekata .term-section-title", ".term-oboekata .term-prose p",
    ".term-pitfall .term-section-title", ".term-pitfall__box p",
    ".term-similar .term-section-title", ".term-similar dl > div",
    ".term-episode .term-section-title", ".term-episode .term-section-note", ".term-episode .episode-list li",
])

# 声。style は VOICEVOX の「ノーマル」
VOICES = {
    "sunny": {"speaker": "九州そら", "style": "ノーマル", "speed": 1.0},
    "moyan": {"speaker": "ずんだもん", "style": "ノーマル", "speed": 1.0},
    # 理論家本人のセリフ(ピクニックのはじまりの2つめの吹き出し)
    "guest_m": {"speaker": "麒ヶ島宗麟", "style": "ノーマル", "speed": 0.88},
    "guest_f": {"speaker": "冥鳴ひまり", "style": "ノーマル", "speed": 1.0},
}
# 女性の理論家のページ(ここにないページは男性の声)。ド・シャザーとバーグは、セリフの口調に合わせて女性の声
FEMALE = {"anna-freud", "buhler", "deshazer-berg", "gottfredson", "hansen", "kubler-ross", "roe", "schlossberg"}

GAP = 0.35          # 段落と段落のあいだ(秒)
GAP_HEADING = 0.8   # 見出しの前


def who(el, page):
    """この段落を読むのはだれか。見出しとモヤンの吹き出しはモヤン、理論家のセリフは理論家、ほかはサニー先生。"""
    cls = el.get("class") or []
    parent = el.parent.get("class") or []
    guest = "guest_f" if page.split("/")[-1] in FEMALE else "guest_m"
    if "line__msg" in cls:                               # 「理論家とピクニック」の会話
        line = el.find_parent(class_=["line", "farewell__line"]).get("class")
        return "moyan" if "line--moyan" in line else "sunny" if "line--sunny" in line else guest
    if "picnic-intro__line--guest" in parent:
        return guest
    if "term-section-title" in cls or "mini-say--moyan" in parent or "chara-guide--moyan" in parent:
        return "moyan"
    return "sunny"


def spoken_text(el, yomi):
    intro = {"picnic-intro__line", "mini-say"} & set(el.parent.get("class") or []) or "line__msg" in (el.get("class") or [])
    el = BeautifulSoup(str(el), "html.parser")
    if intro and el.find("b"):                                  # 「サニー先生」などの名前の札は読まない
        el.find("b").decompose()
    for label in el.select("dt") + ([el.p.b] if el.p and "term-bridge" in (el.p.get("class") or []) and el.p.b else []):     # 用語名や小見出しのあとで一拍おく
        label.append("。")
    for br in el.find_all("br"):                        # 行がえの所で一拍おく
        br.replace_with("、")
    text = el.get_text()
    for src in sorted(yomi, key=len, reverse=True):     # 長い書き方から先に置きかえる
        text = text.replace(src, yomi[src])
    text = re.sub(r"[🌈☀️📚🌥️▶︎]", "", text)
    text = re.sub(r"[(（]([A-Z])[)）]", r"\1", text)             # 現実的(R) → 現実的R
    text = re.sub(r"[(（](?=[^)）]*[a-z])(?=[^)）]*[ ,.])[A-Za-z][A-Za-z .,'\-]*[)）]", "", text)  # (Schein, E. H.) は読まない
    # 記号の読み方
    for i, n in enumerate(["いち", "に", "さん", "よん", "ご", "ろく", "なな", "はち", "きゅう", "じゅう"]):
        text = text.replace("①②③④⑤⑥⑦⑧⑨⑩"[i], "、" + n + "、")
    text = re.sub(r"[〇○]×", "まるばつ", text)
    text = re.sub(r"[〇○]{2}", "まるまる", text)
    text = re.sub(r"[〇○]", "マル", text)
    text = re.sub(r"×(?=[。、にとだがでもを)）]|$)|(?<=は)×", "バツ", text)  # 「記述は×」。かけ算の × はそのまま
    text = re.sub(r"(?<![平均同高対初中上劣優差何])等(?![しい級身分価式号質々])", "トウ", text)  # 「休業等」の等
    text = text.replace("⇔", "と")
    text = re.sub(r"([0-9])〜([0-9])", r"\1から\2", text)
    text = re.sub(r"(^|(?<=[(（、。\s]))〜([0-9]+歳(?:ごろ)?)", r"\2まで", text)
    text = re.sub(r"([0-9]+歳(?:ごろ)?)〜", r"\1から", text)
    text = re.sub(r"〜(?=でなければ|すべき|ねば|べき|に違いない)", "なになに", text)
    text = text.replace("〜", "から")
    # 区切り
    text = re.sub(r"[」』]\s*[「『]", "、", text)                  # 「A」「B」→ A、B
    text = re.sub(r"[(（]", "、", text)
    text = re.sub(r"[)）]", "、", text)
    text = re.sub(r"[—―]+", "、", text)
    text = re.sub(r"[・/／:：]", "、", text)
    text = re.sub(r"[「」『』]", "", text)
    text = text.replace("法って", "ホウ、って")                    # 「のっとって」と読ませない
    text = re.sub(r"([ぁ-ん])方です", r"\1かたです", text)        # 働き方です(「ほうです」と読ませない)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"、\s*([、。！？])", r"\1", text)
    text = re.sub(r"、{2,}", "、", text)
    text = re.sub(r"(^|(?<=[。！？]))\s*、", "", text)
    return text


def api(path, params, body=None):
    url = f"{ENGINE}{path}?{urllib.parse.urlencode(params)}"
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method="POST", headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as res:
        return res.read()


def style_ids():
    with urllib.request.urlopen(f"{ENGINE}/speakers", timeout=30) as res:
        speakers = json.load(res)
    ids = {}
    for key, v in VOICES.items():
        sp = next(s for s in speakers if s["name"] == v["speaker"])
        ids[key] = next(st["id"] for st in sp["styles"] if st["name"] == v["style"])
    return ids


def synth(text, style_id, speed, dry=False):
    query = json.loads(api("/audio_query", {"text": text, "speaker": style_id}))
    print("   読み:", re.sub(r"[/_']", "", query["kana"]))
    if dry:
        return None
    query["speedScale"] = speed
    query["prePhonemeLength"] = 0.05
    query["postPhonemeLength"] = 0.05
    query["outputSamplingRate"] = 24000
    query["outputStereo"] = False
    return api("/synthesis", {"speaker": style_id}, query)


def build(page, yomi, ids, dry, force):
    html = (ROOT / page / "index.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    for w in soup.find_all("wbr"):
        w.decompose()
    els = soup.select(SELECTOR)
    if not soup.select_one("[data-lesson]") and not dry:
        print(f"{page}: ページに data-lesson の置き場所がないので飛ばす")
        return
    lines = [(who(el, page), spoken_text(el, yomi), "term-section-title" in (el.get("class") or []) or el.name == "h2") for el in els]
    digest = hashlib.sha1(json.dumps([lines, VOICES], ensure_ascii=False).encode()).hexdigest()[:12]

    out_dir = ROOT / "audio" / page
    meta = out_dir / "lesson.json"
    if not dry and not force and meta.exists() and json.loads(meta.read_text(encoding="utf-8")).get("h") == digest:
        print(f"{page}: 本文が前回と同じなので飛ばす")
        return

    print(f"== {page}")
    rate = 24000
    pcm = bytearray()
    segs = []
    for i, (speaker, text, heading) in enumerate(lines):
        print(f"{i:02d} {speaker} {text}")
        wav = synth(text, ids[speaker], VOICES[speaker]["speed"], dry)
        if dry:
            continue
        if i:
            pcm += b"\x00\x00" * int(rate * (GAP_HEADING if heading else GAP))
        with wave.open(io.BytesIO(wav)) as w:
            assert w.getframerate() == rate and w.getnchannels() == 1 and w.getsampwidth() == 2
            frames = w.readframes(w.getnframes())
        start = len(pcm) / 2 / rate
        pcm += frames
        segs.append({"s": speaker.split("_")[0], "t": round(start, 2), "e": round(len(pcm) / 2 / rate, 2)})
    if dry:
        return

    out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "lesson.wav"
        with wave.open(str(wav), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(rate)
            w.writeframes(bytes(pcm))
        # いったん別の名前で書いてから置きかえる(書いている途中のファイルを読ませない)
        m4a = Path(tmp) / "lesson.m4a"
        subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", "-b", "48000", str(wav), str(m4a)], check=True)
        shutil.move(str(m4a), str(out_dir / "lesson.m4a"))

    total = round(len(pcm) / 2 / rate, 2)
    used = dict.fromkeys(VOICES[k]["speaker"] for k in VOICES if any(l[0] == k for l in lines))
    credit = " / ".join("VOICEVOX:" + name for name in used)
    meta.write_text(
        json.dumps({"credit": credit, "total": total, "h": digest, "segs": segs}, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8")
    size = (out_dir / "lesson.m4a").stat().st_size
    print(f"→ {len(segs)}段落 / {total:.0f}秒 / {size / 1024:.0f}KB")


def main():
    args = sys.argv[1:]
    dry = "--dry" in args
    force = "--force" in args
    pages = [a.strip("/") for a in args if not a.startswith("--")]
    yomi = json.loads((ROOT / "scripts" / "lesson-yomi.json").read_text(encoding="utf-8"))
    ids = style_ids()
    for page in pages:
        build(page, yomi, ids, dry, force)


if __name__ == "__main__":
    main()

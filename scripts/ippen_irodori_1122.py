#!/usr/bin/env python3
"""白い段が続く所を「段の扉」にする（2026-11-22）。

ちゃん 11/22「ずっと白が続くから、途中で段を切り替えたり、可愛いイラストや画像を入れたりできる？」
→ ナデシコ案1（段の扉）を見本に→「水色が多すぎる。ベージュが多い方が読みやすいかも」→「見出しのイラストは半分くらいに」
→「いいと思います。他のページも統一し、本番にあげてください」。
- 段の地：目次の続きの段のあと〜出典の前で、白い段（迷った人の声のスタンプの段も白として数える）の前もうしろも
  色の段でなければ、ベージュ（cream）にする。説明会の予約先（id=apply-h）は緑。足した段には class="ir"。
  11/22 ちゃんのOKで、統一の決まり（11/19）の段の地に「ベージュ」を足した。
- 段の扉：見出しの段（hb・よくある質問・予約先・ほかの学校）の頭を、小さな絵→「くわしく N」→見出し の順にまん中へ。
  絵は見出しの言葉から、サイトにある絵を選ぶ（そのページで使っていない絵だけ）。絵はスマホ66px・PC84px。
- ベージュの段の中の白いはずのカード・表・箱は白にする。
- 何度かけても同じ（印 ir・tobira がある段はさわらない・<style id="ir1122"> は入れかえ）。
使い方: python3 scripts/ippen_irodori_1122.py [ページ …]
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ippen_brk_1122 import PAGES  # noqa: E402

SKIP_PAGES = {"index.html", "exam/index.html"}  # 作りが別（目次の段がない）
STOP_IDS = {"shutten", "tsugi"}
NO_COLOR_IDS = {"matome", "tool"}
DOOR_IDS = {"faq", "apply-h", "hoka"}

# 見出しの言葉 → 絵（上から順に見る）
E = [
    (r"予約先|申込み先|予約", "img/top/hito_5_mada.webp"),
    (r"よくある質問", "img/top/kumo_usagi.webp"),
    (r"質問と答え|聞いた|メール", "img/parts/18_bulletin_board.webp"),
    (r"説明会", "img/top/hito_2_donichi.webp"),
    (r"振替|休んだ", "img/top/nayami_furikae.webp"),
    (r"日程|期間|流れ|順番|ステップ|ペース|受け方|1日", "img/top/fuan_tsuzuku.webp"),
    (r"試験|学科|論述|面接|対策|勉強", "img/top/fuan_shiken.webp"),
    (r"費用|お金|いくら|万円|円|給付金|安い|受講料|割合|戻る", "img/top/fuan_okane.webp"),
    (r"いつ|時間|日は", "img/top/fuan_tsuzuku.webp"),
    (r"体験|受けて|わたし|両立|子育て|働きながら|よかった|大変", "img/top/hito_honne.webp"),
    (r"公式|確かめ|情報|比較表|リスト|チェック|一覧|わかって|知っておき|確認|わからない", "img/parts/09_blue_notebook.webp"),
    (r"オンライン|在宅|家から|家で|家に|自宅|ロールプレイ|環境", "img/kata/school_chiiki.webp"),
    (r"向いて|向く|向か|価値|やめ|理由|本人|守り", "img/top/kumo_hiyoko.webp"),
    (r"資格|登録|なるには|道|ルート|結論|とは|何を|仕事|場所|修了", "img/top/fuan_daijoubu.webp"),
    (r"学校|選び|選ぶ|くらべ|比較|講座", "img/parts/04_book_wagon.webp"),
]
# 合う絵が残っていないときに使う絵（同じタッチの小物）
SPARE = ["img/top/sora_niji.webp", "img/parts/10_yellow_pencil.webp", "img/parts/08_blue_backpack.webp",
         "img/parts/29_potted_plant.webp", "img/parts/11_lunchbox.webp", "img/parts/12_beach_ball.webp",
         "img/parts/05_pinwheel.webp", "img/top/nayami_mada.webp"]

GREEN_FILL = "%23ECF0D8"
WAVE = ("url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 40' "
        "preserveAspectRatio='none'%3E%3Cpath d='M0 24 Q100 6 200 24 T400 24 T600 24 T800 24 T1000 24 T1200 24 "
        f"V40 H0 Z' fill='{GREEN_FILL}'/%3E%3C/svg%3E\")")
NOTCOL = "section.sec2:not(.sky):not(.cream):not(.green)"
CSS = (
    '<style id="ir1122">'
    "/* 11/22 段の扉＋ベージュと白の交互（scripts/ippen_irodori_1122.py）。"
    "11/22 ちゃんのOKで、統一の決まり（11/19）の段の地に「ベージュ（cream）」を足した */"
    "body.kata section.sec2.ir.cream,body.kata section.sec2.ir.green{padding-top:104px!important;padding-bottom:104px!important}"
    f"body.kata {NOTCOL}+section.sec2.ir.green::before{{content:\"\"!important;position:absolute;left:0;right:0;height:40px;z-index:2;"
    f"pointer-events:none;top:-39px;bottom:auto;transform:none;background:no-repeat {WAVE}!important;background-size:100% 40px!important}}"
    "body.kata section.sec2.cream :is(.ft-row>span,.tblw,.tbl,.ofc-g,details.more,.faq details,.card,.box,.zu-box){background:#fff!important}"
    "body.kata .tobira{display:flex;flex-direction:column;align-items:center;text-align:center;margin:0 auto 28px}"
    "body.kata .tobira>img{width:84px;height:84px;object-fit:contain;margin:0 0 10px}"
    "body.kata .tobira .eye{margin:0 0 6px!important;letter-spacing:.12em}"
    "body.kata .tobira h2{font-size:26px!important;line-height:1.5!important;text-align:center!important;text-wrap:balance;"
    "margin:0!important;padding-left:0!important;background:none!important}"
    "body.kata .tobira h2 img,body.kata .tobira h2::before{display:none!important}"
    "@media (max-width:760px){"
    "body.kata section.sec2.ir.cream,body.kata section.sec2.ir.green{padding-top:68px!important;padding-bottom:68px!important}"
    f"body.kata {NOTCOL}+section.sec2.ir.green::before{{height:24px;background-size:100% 24px!important;top:-23px}}"
    "body.kata .tobira>img{width:66px;height:66px}"
    "body.kata .tobira h2{font-size:22px!important}"
    "}"
    "</style>"
)

SEC = re.compile(r'<section\b([^>]*)>.*?</section>', re.S)


def attrs(m):
    """段の class と id（書く順番はページによってちがう）"""
    a = m.group(1)
    c = re.search(r'class="([^"]*)"', a)
    i = re.search(r'id="([^"]*)"', a)
    return (c.group(1) if c else ""), (i.group(1) if i else "")
HEAD = re.compile(r'(<p class="eye">.*?</p>\s*)?(<h2\b[^>]*>.*?</h2>)', re.S)


def text(h):
    return re.sub(r"<[^>]+>|\s", "", h)


def colored(cls):
    return any(c in cls.split() for c in ("sky", "green", "cream", "gara"))


def apply(html, depth):
    secs = list(SEC.finditer(html))
    start = next((i for i, m in enumerate(secs) if "mokuji-tsuzuki" in attrs(m)[0]), None)
    if start is None:
        return html, 0, 0
    body = []
    for m in secs[start + 1:]:
        if attrs(m)[1] in STOP_IDS:
            break
        body.append(m)
    col = [colored(attrs(m)[0]) for m in body]
    used = {os.path.basename(u) for u in re.findall(r'<img[^>]+src="([^"]+)"', html[html.find("<body"):])}
    pre = "../" * depth
    edits, nc, nd = [], 0, 0
    for i, m in enumerate(body):
        cls, sid = attrs(m)
        part = new = m.group(0)
        cl = cls.split()
        # 地の色
        if "ir" not in cl and not col[i] and sid not in NO_COLOR_IDS and "plain" not in cl and sid != "nayami" and HEAD.search(part):
            prev_ok = i == 0 or not col[i - 1]
            next_ok = i + 1 >= len(body) or not col[i + 1]
            color = None
            if sid == "apply-h":
                color = "green"
            elif prev_ok and next_ok and i > 0:
                color = "cream"
            if color:
                head_end = new.find(">")
                new = new[:head_end].replace(f'class="{cls}"', f'class="{cls} {color} ir"', 1) + new[head_end:]
                col[i] = True
                nc += 1
        # 段の扉
        if 'class="tobira"' not in new and ("hb" in cl or sid in DOOR_IDS) and "plain" not in cl:
            hm = HEAD.search(new)
            if hm:
                title = text(hm.group(2))
                img = next((src for pat, src in E if re.search(pat, title) and os.path.basename(src) not in used), None)
                if not img:
                    img = next((s for s in SPARE if os.path.basename(s) not in used), None)
                img_tag = ""
                if img:
                    used.add(os.path.basename(img))
                    img_tag = f'<img src="{pre}{img}" alt="" loading="lazy" decoding="async">'
                eye = (hm.group(1) or "").rstrip()
                if os.environ.get("IR_SHOW"):
                    print("   ", sid or "-", title[:28], "→", os.path.basename(img) if img else "なし")
                door = f'<div class="tobira">{img_tag}{eye}{hm.group(2)}</div>'
                new = new[:hm.start()] + door + new[hm.end():]
                nd += 1
        if new != part:
            edits.append((m.start(), m.end(), new))
    for a, b, new in reversed(edits):
        html = html[:a] + new + html[b:]
    return html, nc, nd


def main():
    for f in sys.argv[1:] or PAGES:
        if f in SKIP_PAGES:
            print(f"{f}: 外す（作りが別）")
            continue
        p = os.path.join(ROOT, f)
        s = open(p, encoding="utf-8").read()
        new, nc, nd = apply(s, f.count("/"))
        if 'id="ir1122"' in new:
            new = re.sub(r'<style id="ir1122">.*?</style>', lambda _: CSS, new, count=1, flags=re.S)
        elif nc or nd:
            new = new.replace("</head>", CSS + "\n</head>", 1)
        if new != s:
            open(p, "w", encoding="utf-8").write(new)
        print(f"{f}: 地の色 +{nc}・扉 +{nd}{'（変わりなし）' if new == s else ''}")


if __name__ == "__main__":
    main()

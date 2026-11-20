#!/usr/bin/env python3
"""いっぺん 11/20 出す前の直し（確認役リンドウ・美雨ちゃんの×と△、ちゃんの決定）を、1か所で持つ道具。

- 組み立ての道具（ippen_from_rough・ippen_build_guides・ippen_build_gimon・ippen_build_top）が、
  書き出す直前に apply(path, html) を通す。組み直しても直しが消えない
- いまのページに当てるとき：python3 scripts/ippen_kotei_1120.py（何回かけても同じ）
- REPL：ページごとの言葉の置きかえ（前の言葉がなく、あとの言葉があれば「済み」）
- NOWRAP：日付・言葉の途中で折れないように、本文の文字（タグの外・script/style の外）だけを
  <span style="white-space:nowrap"> でくるむ
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NW = '<span style="white-space:nowrap">'

KIKAN = "雇用保険に入っていた期間が足りなくて"  # 11/20 ちゃん：給付金が使えなかった本当の理由

REPL = {
    "schools/lec/index.html": [
        # ×3 早期割引は終わっている（11/1 から 330,000円一律。1119_トップ_募集と特典の確かめ.md）
        ('<span class="tx">入学金・教材費は0円。早めの申込みで割引</span>', '<span class="tx">入学金・教材費は0円</span>'),
        ("受講料の中に、入学金も教材費も入っています。早めに申し込むと割引があります。</figcaption>",
         "受講料の中に、入学金も教材費も入っています。</figcaption>"),
        ("  <p>早めに申し込むと割引があり、金額は時期で変わります。</p>\n", ""),
        ("入学金と教材費は0円です。早めに申し込むと割引があり、金額は時期で変わります。", "入学金と教材費は0円です。"),
        # ×2 作業メモ
        ("2026-11-15〜16。出す前に、公式で確かめ直します</p>", "2026-11-15〜16</p>"),
    ],
    "schools/compare/index.html": [
        # ちゃん決定 B：説明会の予約先は文字のリンクに（行き先・PR・計測はそのまま）
        ('class="cta apply__go"', 'class="tl apply__go"'),
        # 振替：日本マンパワーはトップと同じ言い方（data/schools.json「無料・回数の制限なしの振替制度あり」）
        ('<b class="fz-n">日本マンパワー</b><span class="fz-k">無料</span>',
         '<b class="fz-n">日本マンパワー</b><span class="fz-k">回数の制限なし・無料</span>'),
        # 終わった回（11月開講）の曜日の例は外す。2月開講のクラスの曜日は公式の日程ページに書いていない（11/20 確認）
        ("<td>土・日・水の昼（11月開講の例）</td>", "<td>曜日は開講の回ごとに公式で</td>"),
        ("オンラインは<wbr>土曜・<wbr>日曜・<wbr>水曜(昼)の<wbr>クラス(11月開講の例)。<wbr>平日夜は<wbr>記載なし",
         "オンラインの<wbr>クラスあり。<wbr>曜日は<wbr>開講の回ごとに<wbr>公式で。<wbr>平日夜は<wbr>記載なし"),
        # 金額を確かめた日はページの出典の行（2026-11-15〜16）のとおり
        ('<th scope="row">情報確認日</th>', '<th scope="row">情報確認日<small>（金額は2026年11月15〜16日）</small></th>'),
        # ちゃん決定 A：LEC の公式サイトは講座説明のページへ、ふつうのリンク
        ('<a href="https://px.a8.net/svt/ejp?a8mat=4BCMO3+2VLGT6+1G62+BW8O2&amp;a8ejpredirect=https%3A%2F%2Fonline.lec-jp.com%2Fdisp%2FNSfKeywordSearch.jsp%3FdispNo%3D%26selkwd%3D%2583L%2583%2583%2583%258A%2583A%2583R%2583%2593%2583T%2583%258B%2583%255E%2583%2593%2583g%26isSearchBar%3D1%26cpp%3D%26srt%3D" rel="sponsored noopener nofollow" target="_blank">公式サイト</a>',
         '<a href="https://www.lec-jp.com/caricon/kouza/yousei/" rel="noopener" target="_blank">公式サイト</a>'),
    ],
    "index.html": [
        ('<p class="dnote">土・日・水の昼（11月開講の例）</p>', '<p class="dnote">曜日は、開講の回ごとに公式で確かめてね</p>'),
        ("わたしは扶養内の勤務で、給付金は使えなかったよ（笑）。", f"わたしは{KIKAN}、給付金は使えなかったよ（笑）。"),
        # PR の札は名前のすぐあと（「プラットフォーム PR に、」と読めないように）→ 文の終わりへ
        ('<span class="nb">地域連携<wbr>プラットフォーム<span class="pr">PR</span></span>に、給付金を使えない人向けの27,000円引きがあったよ。見てみてね</p>',
         '<span class="nb">地域連携<wbr>プラットフォーム</span>に、給付金を使えない人向けの27,000円引きがあったよ。見てみてね<span class="pr">PR</span></p>'),
        ("<p class=\"after\">説明会の予約先は、ページの下の「説明会で雰囲気を見てみよう」から</p>",
         "<p class=\"after\"><a href=\"/schools/compare/#apply-h\">説明会の予約先は、ページの下の「説明会で雰囲気を見てみよう」から</a></p>"),
        ("やめたほうがいい人・向いている人", f"やめたほうがいい人・{NW}向いている人</span>"),
        # 11/20 ちゃん「トップの地域連携プラットフォームは運営者の母校にして」
        ('<p class="forwho">費用をおさえたい人・夜間に受けたい人</p>',
         '<p class="forwho"><b class="bogo">運営者の母校</b><br>費用をおさえたい人・夜間に受けたい人</p>'),
    ],
    "schools/index.html": [
        ("<p>受けられる日：土・日・水の昼（11月開講の例）</p>", "<p>受けられる日：曜日は開講の回ごとに公式で</p>"),
    ],
    "schools/nippon-manpower/index.html": [
        ("<b>答え</b>オンラインは土曜・日曜・水曜（昼）のクラスがあるよ（11月開講の例）。",
         "<b>答え</b>オンラインのクラスがあるよ。曜日は、開講の回ごとに公式で確かめてね。"),
        ("オンラインのクラスは、土曜・日曜・水曜（昼）の例があります（11月開講の例）。",
         "オンラインのクラスがあります。曜日は、開講の回ごとに公式ページで確かめてね。"),
    ],
    "shikaku-guide/gimon/index.html": [
        ("運営者は、<wbr>扶養内で<wbr>働いていたので<wbr>対象外でした。",
         "運営者は、<wbr>雇用保険に<wbr>入っていた<wbr>期間が<wbr>足りず、<wbr>対象外でした。"),
    ],
    "school-guides/kyufukin-tetsuzuki/index.html": [
        ("@運営者より：わたしは扶養内の勤務で、給付金は使えなかったよ（笑）。", f"@運営者より：わたしは{KIKAN}、給付金は使えなかったよ（笑）。"),
    ],
    "school-guides/yasui/index.html": [
        ("わたしは<wbr/>扶養内で<wbr/>働いていたので、<wbr/>給付金は",
         "わたしは<wbr/>雇用保険に<wbr/>入っていた<wbr/>期間が<wbr/>足りなくて、<wbr/>給付金は"),
    ],
    "school-guides/kyufukin/index.html": [
        ("わたしが<wbr/>まさに<wbr/>それでした。<wbr/>扶養内で<wbr/>働いていたので、<wbr/>給付金は<wbr/>受けられなかったんです。",
         "わたしは<wbr/>雇用保険に<wbr/>入っていた<wbr/>期間が<wbr/>足りなくて、<wbr/>給付金は<wbr/>受けられなかったんです。"),
    ],
    "school-reviews/chiiki-renkei-platform/index.html": [
        ("扶養内で働いていて、教育訓練給付金を受けられなかったためです。", "雇用保険に入っていた期間が足りず、教育訓練給付金を受けられなかったためです。"),
    ],
}
# 書いた人の欄：試験は「受けました（合格発表は2026年12月16日）」にそろえる（比較表・学校ページと同じ）
for g in ("how-to-choose", "online", "working-mothers", "training-and-exam-preparation"):
    REPL.setdefault(f"school-guides/{g}/index.html", []).append((
        "2026年11月の<wbr/>試験に<wbr/>挑戦中の<wbr/>初学者と<wbr/>して、",
        "2026年11月の<wbr/>第33回<wbr/>キャリアコンサルタント試験を<wbr/>受けました<wbr/>（合格発表は<wbr/>2026年12月16日）。<wbr/>初学者と<wbr/>して、"))

NOWRAP = {
    "index.html": ["2月12日（金）", "3月12日（金）", "第36回", "第35回"],
    "schools/compare/index.html": ["ちがいます。", "載っている", "最後に確かめる", "協会", "あれば）", "体験記"],
    "schools/lec/index.html": ["70%以上"],
    "school-guides/how-to-choose/index.html": ["(?<!コ)コツ(?!コ)", "しぼれます"],
    "school-guides/kyufukin/index.html": ["確かめてね。"],
    "school-guides/kyufukin-tetsuzuki/index.html": ["確かめてね。"],
}
SKIP_TAGS = ("script", "style", "title", "textarea", "option")


def nowrap(html, pats):
    i = html.find("<body")
    if i < 0:
        return html
    head, body = html[:i], html[i:]
    parts = re.split(r"(<[^>]+>)", body)
    skip = None
    for k, p in enumerate(parts):
        if p.startswith("<"):
            m = re.match(r"<(/?)([a-zA-Z0-9]+)", p)
            if m:
                name = m.group(2).lower()
                if not m.group(1) and name in SKIP_TAGS:
                    skip = name
                elif m.group(1) and name == skip:
                    skip = None
            continue
        if skip or not p:
            continue
        for pat in pats:
            p = re.sub(rf"({pat})", NW + r"\1</span>", p)
        parts[k] = p
    out = head + "".join(parts)
    # 2回目以降のくるみをはがす（何回かけても同じ）
    while True:
        o2 = re.sub(re.escape(NW) + re.escape(NW) + r"([^<]*)</span></span>", NW + r"\1</span>", out)
        if o2 == out:
            break
        out = o2
    return out


def _unwrap_prev(html, pats):
    """前にくるんだものを一度はがしてから、くるみ直す（同じ所が二重にならないように）"""
    return re.sub(re.escape(NW) + r"([^<]*)</span>", lambda m: m.group(1) if any(re.fullmatch(p, m.group(1)) for p in pats) else m.group(0), html)


def apply(path, html, report=None):
    for old, new in REPL.get(path, []):
        n = html.count(old)
        if n:
            html = html.replace(old, new)
        if report is not None:
            report.append((path, old[:40], n, new in html))
    pats = NOWRAP.get(path)
    if pats:
        html = nowrap(_unwrap_prev(html, pats), pats)
    return html


if __name__ == "__main__":
    rep = []
    for path in sorted(set(REPL) | set(NOWRAP)):
        f = os.path.join(ROOT, path)
        s = open(f, encoding="utf-8").read()
        t = apply(path, s, rep)
        if t != s:
            open(f, "w", encoding="utf-8").write(t)
        print(f"{path}: {'書きかえ' if t != s else '変化なし'}  くるみ {t.count(NW)}")
    bad = [r for r in rep if r[2] == 0 and not r[3]]
    for r in rep:
        print("  ", "置きかえ" if r[2] else ("済み" if r[3] else "見つからない"), r[2], r[0], r[1])
    if bad:
        sys.exit("見つからない置きかえがあります")

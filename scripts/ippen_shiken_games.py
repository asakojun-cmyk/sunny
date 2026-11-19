#!/usr/bin/env python3
"""いっぺんの入れかえ（2026-11-20）：試験の側の 06 一問一答（/games/quiz/）・07 論述（/games/ronjutsu/）・
08 ミニゲームの一覧（/games/）を、ラフ_1119 の型で組む道具。

- 見た目と流れはラフ（範囲を選ぶ→問題→正誤→解説→次へ／型を選ぶ→事例→マス→型ノート）
- 動きは本番のまま：js/quiz-drill.js（問題のデータ #quiz-data と data-quiz-*）、js/ronjutsu.js（data-ron-*・data-rb-*）。
  ラフのボタン（範囲・時間・型）は、本番のしくみを動かすだけの小さなスクリプト（js/quiz-kata.js・js/ronjutsu-kata.js）でつなぐ
- 文は本番のページのまま。ラフの見本の問題・作り文は使わない。数（問題の数など）は本番のデータで数える
- 頭（計測・title・説明文・canonical・構造化データ）は本番から引きつぐ（scripts/ippen_shiken.py）

使い方: /Users/iwawakiasako/voicevox-engine/venv/bin/python scripts/ippen_shiken_games.py [quiz] [ronjutsu] [games]
"""
import json
import os
import re
import shutil
import sys

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ippen_parts as P  # noqa: E402
import ippen_shiken as S  # noqa: E402

ROOT = P.ROOT
OMAMORI_SRC = S.ROUGH + "/1119_論述のお守り1枚.pdf"


def read(path):
    """本番のページ（組みかえる前）。組んだあとに回し直しても同じになるよう、git の記録から読む。
    PROD_REF（いまは 7d8c7f3ea の上に共通の部品を入れた ac71b1714）の版を使う"""
    import subprocess
    return subprocess.run(["git", "-C", ROOT, "show", f"{PROD_REF}:{path}"], capture_output=True, text=True, check=True).stdout


PROD_REF = "ac71b1714"


def soup_of(html):
    s = BeautifulSoup(html, "html.parser")
    for w in s.find_all("wbr"):
        w.decompose()
    return s


def text(el):
    return el.get_text("", strip=True) if el else ""


def cut(body, start, end, new):
    """body の start（を含む）から end（を含む）までを new にする"""
    i = body.index(start)
    j = body.index(end, i) + len(end)
    return body[:i] + new + body[j:]


def crumb_ld(path, crumb):
    def fix(ld):
        out = []
        for j in ld:
            if '"BreadcrumbList"' in j:
                items = []
                for i, (n, h) in enumerate(crumb):
                    item = h or (P.url_of(path) if i == len(crumb) - 1 else None)
                    items.append('{"@type":"ListItem","position":%d,"name":"%s"%s}' % (
                        i + 1, n, (',"item":"https://carepicnic.com%s"' % item) if item else ""))
                j = ('<script type="application/ld+json">{"@context":"https://schema.org","@type":"BreadcrumbList",'
                     f'"itemListElement":[{",".join(items)}]}}</script>')
            out.append(j)
        return out
    return fix


def finish(path, prod, body, cat, crumb, extra_css, js):
    r = P.rel_root(path)
    body, rough_js = S.split_scripts(body)  # ラフの見本の動き（見本の問題つき）は使わない
    body = body.rstrip() + "\n"
    scripts = "\n".join(f'<script src="{r}js/{j}" defer></script>' for j in js)
    body = body.replace("@@END@@\n", "@@END@@\n" + scripts + "\n")
    out = S.page(path, prod, body, cat=cat, crumb=crumb, extra_css=extra_css, ld_fix=crumb_ld(path, crumb))
    S.check(path, out)
    return out


def lost_sentences(prod, out, skip=()):
    """本番の <main> の文のうち、新しいページに見つからないもの（空白・記号を除いてくらべる）"""
    def norm(t):
        return re.sub(r"[\s　、。・「」『』()（）！？!?…▶︎→←✓✗☀️🌥️🌞🏁🚩📄🔒📝⚾🌈🧱🃏🗃️🧩🎮]", "", t)
    a = soup_of(prod).select_one("main")
    for sc in a.find_all(["script", "style"]):
        sc.decompose()
    b = norm(soup_of(out).get_text(""))
    lost = []
    for el in a.find_all(["p", "li", "h1", "h2", "h3", "h4", "button", "span", "dd", "dt", "option", "summary"]):
        if el.find(["p", "li", "div", "button", "span"]):
            continue
        t = el.get_text("", strip=True)
        if len(norm(t)) < 4 or any(k in t for k in skip):
            continue
        if norm(t) not in b:
            lost.append(t)
    return lost


# ======================================================================= 06 一問一答
def quiz_counts(data):
    """本番の js/quiz-drill.js と同じ決まりで、範囲ごとの問題の数を数える"""
    def n(f):
        return sum(1 for x in data if f(x))
    c = {"all": len(data), "honban": n(lambda x: x.get("h") == 1), "freq3": n(lambda x: x.get("f") == 3),
         "theorist": n(lambda x: x.get("t") == 1), "choice": n(lambda x: bool(x.get("o"))),
         "theory": n(lambda x: x.get("c") in ("キャリア理論", "カウンセリング理論")), "shiryo": n(lambda x: x.get("s") == 1),
         "mock": 50}
    for d in range(1, 11):
        c[f"dom:{d}"] = n(lambda x, d=d: x.get("d") == d)
    for x in data:
        c["cat:" + x.get("c", "")] = c.get("cat:" + x.get("c", ""), 0) + 1
    return c


def build_quiz():
    path = "games/quiz/index.html"
    prod = read(path)
    ps = soup_of(prod)
    r = P.rel_root(path)
    data_el = re.search(r'<script type="application/json" id="quiz-data">.*?</script>', prod, re.S).group(0)
    data = json.loads(ps.select_one("#quiz-data").string)
    cnt = quiz_counts(data)
    gsel = ps.select_one("[data-quiz-genre]")
    tsel = ps.select_one("[data-quiz-timesel]")
    opts = {o["value"]: text(o) for o in gsel.find_all("option")}
    # ラフの並び：よく使う8つ＋「分野・テーマで選ぶ」
    main_v = ["all", "honban", "freq3", "theorist", "choice", "mock", "wrong", "unseen"]
    more_v = [v for v in opts if v not in main_v]
    diffs = []

    def btn(v, pressed):
        label = opts[v]
        m = re.match(r"^(.*?)\((.*)\)$", label)
        name, small = (m.group(1), m.group(2)) if m else (label, "")
        if v in cnt and v != "mock":
            num = re.search(r"(\d+)問", small)
            if num and int(num.group(1)) != cnt[v]:
                diffs.append(f"{name}: 札{num.group(1)}・データ{cnt[v]}")
            small = re.sub(r"\d+問", f"{cnt[v]}問", small) if num else small
        return (f'<button class="opt" type="button" aria-pressed="{"true" if pressed else "false"}" data-v="{v}">'
                f'{name}{f" <small>{small}</small>" if small else ""}</button>')
    main_btns = "\n            ".join(btn(v, v == "all") for v in main_v)
    more_btns = "\n              ".join(btn(v, False) for v in more_v)
    tbtns = []
    for o in tsel.find_all("option"):
        label = text(o)
        m = re.match(r"^(.*?)\((.*)\)$", label)
        name, small = (m.group(1), m.group(2)) if m else (label, "")
        tbtns.append(f'<button class="opt" type="button" aria-pressed="{"true" if o["value"] == "5" else "false"}" data-v="{o["value"]}">'
                     f'{name}{f" <small>{small}</small>" if small else ""}</button>')
    bub = [b.decode_contents() for b in ps.select(".chara-guide__bubble")]
    sunny_txt = re.sub(r"<wbr/?>", "", bub[0]).strip()
    moyan_txt = re.sub(r"<wbr/?>", "", bub[1]).strip()
    k = sunny_txt.find("まちが")
    sun1, sun2 = sunny_txt[:k].strip(), sunny_txt[k:].strip()
    sun2 = sun2.replace("まちが えても", "まちがえても").replace("強くなる からね", "強くなるからね")
    sun1 = re.sub(r"\s+", "", sun1)
    sun2 = re.sub(r"\s+", "", sun2)
    moyan_txt = re.sub(r"\s+", "", moyan_txt)
    lede = re.sub(r"\s+", "", re.sub(r"<wbr/?>", "", ps.select_one(".section-header__lede").decode_contents()))
    sel_hidden = (f'<div class="qz-sel" hidden>{str(gsel)}{str(tsel)}</div>')

    dcard = f"""<div class="dcard" id="dcard">
      <div id="s-pick" class="quiz-drill__start" data-quiz-start>
        <div class="sguide"><img src="{r}img/kata/sunny.webp" alt="サニー先生"><p><span class="who">サニー先生</span>{sun1}</p></div>
        <div class="grp">
          <p class="lbl">ジャンル</p>
          <div class="opts" data-g="genre">
            {main_btns}
          </div>
          <details class="more2"><summary>分野・テーマで選ぶ（{len(more_v)}）</summary>
            <div class="opts" data-g="genre">
              {more_btns}
            </div>
          </details>
        </div>
        <div class="grp">
          <p class="lbl">学習時間</p>
          <div class="opts" data-g="time">
            {"".join(tbtns)}
          </div>
        </div>
        {sel_hidden}
        <p class="howmany quiz-drill__count"><b class="num" data-quiz-pool>{cnt["all"]}</b>問の中から、<b class="num" data-quiz-count>10</b>問出題されます</p>
        <button class="x-start2" type="button" data-quiz-begin>この条件で始める</button>
        <p class="quiz-drill__zero" data-quiz-zero hidden></p>
        <p class="alt"><button class="tl linkb" type="button" data-quiz-random>おまかせランダム10問(ジャンル・時間不問)</button></p>
      </div>
      <div class="quiz-drill quiz-drill--stage" data-quiz-drill hidden>
        <div class="quiz-drill__card" data-quiz-card hidden>
          <div class="qhead"><span class="qno">Q<span data-quiz-no>1</span><small> / <span data-quiz-total>0</span></small></span><span class="qtag" data-quiz-cat></span><span class="qsc">正解 <span data-quiz-score>0</span></span><span class="dots" aria-hidden="true" data-qk-dots></span></div>
          <p class="qtext" data-quiz-q></p>
          <div class="ox" data-quiz-ox><button class="ans" type="button" data-quiz-ans="true"><b>○</b><span>正しい</span></button><button class="ans" type="button" data-quiz-ans="false"><b>×</b><span>まちがい</span></button></div>
          <div class="four" data-quiz-choices hidden></div>
          <div class="fb" data-quiz-result aria-live="polite" hidden>
            <p class="fh quiz-drill__verdict" data-quiz-verdict></p>
            <p class="kl">解説</p>
            <p class="ke" data-quiz-exp></p>
            <p class="rv"><a class="tl" data-quiz-link href="/terms/">用語ページで復習する</a></p>
            <div class="nextw"><button class="cta" type="button" data-quiz-next>次の問題へ</button></div>
          </div>
        </div>
        <div class="quiz-drill__end" data-quiz-end aria-live="polite" hidden>
          <div class="rtop"><p class="rk">おつかれさま！</p><p class="rs"><span data-quiz-final></span></p></div>
          <p class="rnote" data-quiz-endnote></p>
          <p class="nextw c"><button class="cta" type="button" data-quiz-retry>もう一回(シャッフル)</button></p>
          <p class="rmore"><a class="tl" href="/exam-guide/shutsudai-hani/">分野ごとの理解度を見る</a><a class="tl" href="/exam-guide/moshi/">模擬試験に挑戦する(50問・100分)</a></p>
          <p class="rshare">きょうの成果をシェア：<a data-quiz-share-x href="https://twitter.com/intent/tweet" rel="noopener" target="_blank">Xで報告</a><a data-quiz-share-line href="https://line.me/R/share" rel="noopener" target="_blank">LINEで報告</a></p>
        </div>
      </div>
    </div>

    <aside class="dside" aria-label="きょうの進み具合">
      <p class="lbl">きょうの進み具合</p>
      <p class="st"><b class="num" data-qk-ok>0</b>問 正解 <span data-qk-done style="color:var(--sub);font-size:13.5px">／ まだ解いていません</span></p>
      <div class="dots" data-qk-dots aria-hidden="true"></div>
      <p class="keep">まちがえた問題は、次から「まちがえた問題だけ」で解き直せます。</p>
      <div class="sguide"><img src="{r}img/kata/sunny.webp" alt="サニー先生"><p><span class="who">サニー先生</span>{sun2}</p></div>
    </aside>"""

    body = S.rough_body("06", path)
    body = cut(body, '<div class="dcard" id="dcard"', "</aside>", dcard)
    # 頭の段
    body = body.replace('○×と4択 全1152問', f'○×と4択 全{cnt["all"]}問')
    # 頭の段は短く（ラフのとおり）。本番の説明の文は、ドリルの段の頭にそのまま置く
    body = re.sub(r'<p class="sub">.*?</p>', '<p class="sub">すきま時間に、テンポよく。</p>', body, count=1, flags=re.S)
    body = body.replace('<ol class="dflow" id="dflow"', f'<p class="dlede">{lede}</p>\n  <ol class="dflow" id="dflow"', 1)
    body = body.replace('<ul class="facts"><li>無料・登録なし</li>', '<ul class="facts"><li class="x-free">無料・登録なし</li>')
    body = body.replace('<button class="cta qstart" type="button" id="qstart">1分でスタート（3問）</button>',
                        '<button class="cta qstart" type="button" data-qk-quick>1分でスタート（3問）</button>')
    body = re.sub(r'(<p class="bub"><span class="who">モヤン</span>).*?(</p>)', lambda m: m.group(1) + moyan_txt + m.group(2), body, count=1, flags=re.S)
    # 次の一歩（STEP5）
    body = body.replace('<a class="ncard" href="#"><span class="nn"><span class="x-step-tag">勉強の道 STEP5 論述と面接</span>50分・自動採点</span>',
                        '<a class="ncard" href="/exam-guide/ronjutsu-moshi/"><span class="nn"><span class="x-step-tag">勉強の道 STEP5 論述と面接</span>50分・自動採点</span>')
    body = body.replace('<a class="ncard" href="#"><span class="nn"><span class="x-step-tag">勉強の道 STEP5 論述と面接</span>無料PDF</span>',
                        '<a class="ncard" href="/exam-guide/ronjutsu-kata/"><span class="nn"><span class="x-step-tag">勉強の道 STEP5 論述と面接</span>無料PDF</span>')
    body = body.replace('<a class="ncard" href="#"><span class="nn"><span class="x-step-tag">勉強の道 STEP5 論述と面接</span>面接の応答を素振り</span>',
                        '<a class="ncard" href="/games/catchball/"><span class="nn"><span class="x-step-tag">勉強の道 STEP5 論述と面接</span>面接の応答を素振り</span>')
    # 問題のデータ（本番のまま）を本文の終わりに
    body = body.replace("@@END@@\n", data_el + "\n@@END@@\n", 1)
    crumb = [("ホーム", "/"), ("試験対策", "/exam/"), ("1問1答", None), ("1問1答ドリル", None)]
    out = finish(path, prod, body, "06", crumb, ("shiken/06-plus.css"),
                 ["quiz-drill.js?v=2026.1018q", "quiz-kata.js?v=2026.1120", "reveal.js?v=2026.1018b"])
    if diffs:
        print("   札の数とデータの数がちがう：", diffs)
    lost = lost_sentences(prod, out)
    print("   本番の文で見つからないもの：", len(lost))
    for t in lost:
        print("     -", t[:90])


# ======================================================================= 07 論述
def build_ronjutsu():
    path = "games/ronjutsu/index.html"
    prod = read(path)
    ps = BeautifulSoup(prod, "html.parser")
    r = P.rel_root(path)
    shutil.copyfile(OMAMORI_SRC, os.path.join(ROOT, "games/ronjutsu/ronjutsu-omamori.pdf"))
    main = ps.select_one("main")
    case = main.select_one(".ron-case")
    rb = main.select_one(".rb")
    board = main.select_one(".ron-board")
    guide = main.select_one(".ron-guide")
    lede = re.sub(r"<wbr/?>", "", main.select_one(".section-header__lede").decode_contents())
    bubbles = [re.sub(r"<wbr/?>", "", b.decode_contents()) for b in main.select(":scope .container > .chara-guide .chara-guide__bubble")]
    gp = guide.find("p", recursive=False)
    lead = re.sub(r"<wbr/?>", "", gp.decode_contents())
    cards = guide.select(".ron-guide__card")
    note = re.sub(r"<wbr/?>", "", guide.select_one(".ron-guide__note").decode_contents())
    note = re.sub(r"\s*[(（][^)）]*転載ではありません[)）]", "", note)  # 「ないこと」を言う一言は出さない（指示書7）

    def card_parts(c):
        ps_ = c.find_all("p")
        return (text(c.select_one(".ron-badge")), re.sub(r"<wbr/?>", "", ps_[0].decode_contents()),
                re.sub(r"<wbr/?>", "", ps_[1].decode_contents()), ps_[2].find("a")["href"])
    cc, jc = card_parts(cards[0]), card_parts(cards[1])

    # 事例（本番の逐語記録のまま。ronjutsu.js が .ron-case を盤の「事例を見る」に写す）
    for el in case.select(".term-section-title"):
        el.name = "h3"
    case_html = str(case).replace('class="ron-case"', 'class="ron-case case" id="case"', 1)
    # 盤（本番の data-rb のまま）とマス（data-ron-* のまま）
    rb_html = str(rb)
    board_html = str(board)
    board_html = board_html.replace('href="../../games/catchball/"', 'href="/games/catchball/"')
    foot = main.select_one(".quiz-drill__foot")
    foot_t = text(foot)

    # 型の札：見本の文で選ぶと、マスのバッジに色がつく（並びと進み方は本番のまま）
    pick = f"""<div class="pick" role="group" aria-label="受ける試験の形式をえらぶ">
    <button type="button" class="pk" data-mode="cc" aria-pressed="true">
      <span class="top"><span class="nm">{cc[0]}</span><span class="on">この型で進む</span></span>
      <span class="org">{cc[1]}</span>
      <span class="ds">{cc[2]}</span>
    </button>
    <button type="button" class="pk" data-mode="jcda" aria-pressed="false">
      <span class="top"><span class="nm">{jc[0]}</span><span class="on">この型で進む</span></span>
      <span class="org">{jc[1]}</span>
      <span class="ds">{jc[2]}</span>
    </button>
  </div>
  <p class="pick-sub"><span>{note}</span><span><a href="{cc[3]}" target="_blank" rel="noopener">協議会の公式サイト</a>　<a href="{jc[3]}" target="_blank" rel="noopener">JCDAの公式サイト</a></span></p>"""

    body = S.rough_body("07", path)
    # 頭の段：本番の言葉
    body = re.sub(r'(<p class="lede">).*?(</p>)', lambda m: m.group(1) + re.sub(r"\s+", "", lede) + m.group(2), body, count=1, flags=re.S)
    body = re.sub(r'(<div class="ps"><img[^>]*><p><span class="who">サニー先生</span>).*?(</p>)',
                  lambda m: m.group(1) + re.sub(r"\s+", "", bubbles[0]) + m.group(2), body, count=1, flags=re.S)
    body = re.sub(r'(<div class="pm"><p><span class="who">モヤン</span>).*?(</p>)',
                  lambda m: m.group(1) + re.sub(r"\s+", "", bubbles[1]) + m.group(2), body, count=1, flags=re.S)
    body = re.sub(r'<p class="go">.*?</p>', '<p class="go"><a class="tl" href="#kata">まず、型をえらぶ</a></p>', body, count=1, flags=re.S)
    # はじめに：本番の文と型の札
    body = re.sub(r'(<section class="sec2 green" id="kata">.*?<p class="lead3">).*?(</p>)', lambda m: m.group(1) + re.sub(r"\s+", "", lead) + m.group(2), body, count=1, flags=re.S)
    body = cut(body, '<div class="pick" role="group"', '</a></span></p>', pick)
    body = body.replace('<h2 class="c pw">論述試験は、2つの形式があるよ</h2>', '<h2 class="c pw">論述試験は2つの形式があるよ</h2>')
    # 事例：本番のもの
    body = cut(body, '<aside class="case" id="case"', '</aside>', case_html)
    body = re.sub(r'<p class="toplay">.*?</p>', '<p class="toplay"><a class="tl" href="#play">読んだら、マス1から解く</a></p>', body, count=1, flags=re.S)
    # 盤とマス：本番のもの
    body = cut(body, '<div class="play">', '<div id="stage" aria-live="polite"></div>\n    </div>\n  </div>',
               f'<div class="play ron-play"><p class="modebar">いまの型：<b data-mode-name>CC協議会型</b>（マスのバッジで、近い問いがわかります）</p>{rb_html}{board_html}</div>')
    body = re.sub(r'<p class="footnote">.*?</p>', f'<p class="footnote">{foot_t.replace("実際の試験問題の転載ではありません。", "").strip()}</p>', body, count=1, flags=re.S)
    # 型ノート：いまの型ノート（/exam-guide/ronjutsu-kata/ の7ページ版）とお守りの1枚
    body = body.replace('<p class="na x-na"><a class="cta" href="#"><span class="x-cta-t">PDFをダウンロード<small>約3MB</small></span></a><a class="tl" href="#">型ノートのページで7ページを見る</a></p>',
                        '<p class="na x-na"><a class="cta" href="/exam-guide/ronjutsu-kata/ronjutsu-kata-note.pdf" download><span class="x-cta-t">PDFをダウンロード<small>約3.5MB</small></span></a><a class="tl" href="/exam-guide/ronjutsu-kata/">型ノートのページで7ページを見る</a></p>')
    body = body.replace('href="1119_論述のお守り1枚.pdf" download', 'href="ronjutsu-omamori.pdf" download="ronjutsu-omamori.pdf"')
    body = body.replace('<a class="tl" href="#">論述の模擬試験（全16回・50分）</a>', '<a class="tl" href="/exam-guide/ronjutsu-moshi/">論述の模擬試験（全16回・50分）</a>')
    body = body.replace('<a class="tl" href="#">ことばのキャッチボール（面接の応答を素振り）</a>', '<a class="tl" href="/games/catchball/">ことばのキャッチボール（面接の応答を素振り）</a>')
    # 出口：面接練習会のページがまだないので、比較表の1つだけ
    body = re.sub(r'<a class="x-ex" href="#">.*?</a>\s*', "", body, count=1, flags=re.S)
    body = body.replace('<div class="in2">', '<div class="in2 one">', 1)
    # 一番下の帯の「次は」（30日の逆算プラン）
    body = re.sub(r'(<p class="go"><a href=")[^"]*(">)', r"\1/exam-guide/last-30days/\2", body)
    crumb = [("ホーム", "/"), ("試験対策", "/exam/"), ("論述", None), ("論述ボードゲーム", None)]
    out = finish(path, prod, body, "07", crumb, ("shiken/07-plus.css"),
                 ["ronjutsu.js?v=2026.1015", "ronjutsu-kata.js?v=2026.1120", "reveal.js?v=2026.1018b"])
    lost = lost_sentences(prod, out)
    print("   本番の文で見つからないもの：", len(lost))
    for t in lost:
        print("     -", t[:90])


# ======================================================================= 08 ミニゲームの一覧
GAMES = [  # (本番の住所, ラフの見出し, 学科/論述/面接, 絵, 量の目安（本番のページで確かめた数だけ）, 身につく（ラフ）)
    ("match", "理論家カードあわせ", "gakka", "img/parts/09_blue_notebook.webp", "1回 約3分・6組", "理論家と理論の結びつき"),
    ("tsumiki", "傾聴のつみきブロック", "gakka mensetsu", "img/parts/04_book_wagon.webp", "4つのタワー", "カウンセリングの技法を積む順番"),
    ("ryuha", "理論家の流派仕分け", "gakka", "img/parts/18_bulletin_board.webp", "6つの流派", "だれの考えが、だれに受けつがれたか"),
    ("anaume", "理論の図 あなうめゲーム", "gakka", "img/parts/10_yellow_pencil.webp", "4つの図", "試験に出る図と「いつ使うか」"),
    ("quiz", "1問1答ドリル", "gakka", "img/parts/12_beach_ball.webp", None, "用語・理論家の○×と4択"),
    ("ronjutsu", "論述ボードゲーム", "ronjutsu", "img/mendan-scene.webp", "1つの事例を1マスずつ", "読む→整理する→書く の型"),
    ("catchball", "ことばのキャッチボール", "mensetsu ronjutsu", "img/parts/13_blue_yellow_tent.webp", "8回のやりとり", "まず受けとめる→それから質問"),
]
TAGJ = {"gakka": "学科", "ronjutsu": "論述", "mensetsu": "面接"}


def build_games():
    path = "games/index.html"
    prod = read(path)
    ps = soup_of(prod)
    r = P.rel_root(path)
    desc = {}
    for a in ps.select(".game-card-link"):
        slug = a["href"].strip("/").split("/")[-1]
        desc[slug] = (text(a.select_one(".game-card-link__title")), text(a.select_one(".game-card-link__desc")))
    qdata = json.loads(soup_of(read("games/quiz/index.html")).select_one("#quiz-data").string)

    def card(g, n):
        slug, title, tags, img, amount, mi = g
        ptitle, pdesc = desc[slug]
        if slug == "quiz":
            amount = f"全{len(qdata)}問から、1分3問〜"
        no = f"ミニゲーム {n:02d}" if tags.startswith("gakka") and slug != "quiz" else {"quiz": "ドリル", "ronjutsu": "ボードゲーム", "catchball": "キャッチボール"}.get(slug, "")
        sub = re.search(r"\((.*?)\)$", ptitle)
        meta = (f'<dt>量の目安</dt><dd>{amount}</dd>' if amount else "") + f'<dt>身につく</dt><dd>{mi}</dd>'
        return f"""<a class="gcard" href="/games/{slug}/" data-t="{tags}">
        <span class="thumb"><img src="{r}{img}" alt="" loading="lazy"></span>
        <div>
          <p class="gno">{no}{f"｜{sub.group(1)}" if sub else ""}</p>
          <p class="gt">{title}</p>
          <p class="gd">{pdesc}</p>
          <dl class="meta">{meta}</dl>
          <ul class="tags">{"".join(f"<li>{TAGJ[t]}</li>" for t in tags.split())}</ul>
          <span class="gogo">あそぶ</span>
        </div>
      </a>"""
    gakka = [g for g in GAMES if g[2].startswith("gakka")]
    other = [g for g in GAMES if not g[2].startswith("gakka")]
    n = {"all": len(GAMES)}
    for t in TAGJ:
        n[t] = sum(1 for g in GAMES if t in g[2].split())
    filt = f"""<div class="filt" role="group" aria-label="試験のどこに効くかで絞りこむ">
    <p class="lbl">試験のどこに効く？</p>
    <button class="opt" type="button" aria-pressed="true" data-f="all">すべて <small>{n["all"]}</small></button>
    <button class="opt" type="button" aria-pressed="false" data-f="gakka">学科 <small>{n["gakka"]}</small></button>
    <button class="opt" type="button" aria-pressed="false" data-f="ronjutsu">論述 <small>{n["ronjutsu"]}</small></button>
    <button class="opt" type="button" aria-pressed="false" data-f="mensetsu">面接 <small>{n["mensetsu"]}</small></button>
  </div>"""
    k = [0]

    def cards(lst):
        out = []
        for g in lst:
            if g[2].startswith("gakka") and g[0] != "quiz":
                k[0] += 1
            out.append(card(g, k[0]))
        return "\n      ".join(out)
    lst = f"""{filt}

  <div class="grp" data-grp>
    <h2 class="gh">学科：ことばと理論を覚える</h2>
    <p class="gl">理論家・理論・図・技法の順番を、手を動かして覚えます。</p>
    <div class="gcards">
      {cards(gakka)}
    </div>
  </div>

  <div class="grp" data-grp>
    <h2 class="gh">論述・面接：型をつかむ</h2>
    <p class="gl">相談の事例と、相談者役のモヤンとのやりとりで、書く型・返す型を体で覚えます。</p>
    <div class="gcards">
      {cards(other)}
    </div>
  </div>
  <p class="more3"><a class="tl" href="/exam/#daily">きょうの3分学習(用語・理論家・1問)もどうぞ</a></p>"""

    body = S.rough_body("08", path)
    # 遊ぶ画面（/games/match/ の見本）はこのページに入れない
    i = body.index("\n</div>\n\n") if "\n</div>\n\n" in body else None
    body = re.sub(r'\n</div>\n\n<div id="v-match" hidden>.*?\n</div>\n(?=\n<section class="x-exit")', "\n", body, count=1, flags=re.S)
    body = body.replace('<div id="v-list">\n', "", 1)
    body = cut(body, '<div class="filt" role="group"', '</div>\n  </div>\n</div></section>', lst + "\n</div></section>")
    # 次の一歩
    body = body.replace('<a class="ncard" href="#"><span class="nn">覚えたかを確かめるなら</span><span class="tl">1問1答ドリル</span></a>',
                        '<a class="ncard" href="/games/quiz/"><span class="nn">覚えたかを確かめるなら</span><span class="tl">1問1答ドリル</span></a>')
    body = S.link_items(body)
    # 出口：面接練習会のページがまだないので、比較表の1つだけ
    body = re.sub(r'<a class="x-ex" href="#">.*?</a>\s*', "", body, count=1, flags=re.S)
    body = re.sub(r'(<section class="x-exit"[^>]*><div class="w">\s*<p class="tt">勉強とあわせて</p>\s*)<div class="in2">', r'\1<div class="in2 one">', body, count=1)
    crumb = [("ホーム", "/"), ("試験対策", "/exam/"), ("ミニゲーム", None)]
    out = finish(path, prod, body, "08", crumb, ("shiken/08-plus.css"), ["games-kata.js?v=2026.1120", "reveal.js?v=2026.1018b"])
    lost = lost_sentences(prod, out, skip=("養成講座を選んでいない方へ",))
    print("   本番の文で見つからないもの：", len(lost))
    for t in lost:
        print("     -", t[:90])


if __name__ == "__main__":
    pass
    todo = sys.argv[1:] or ["quiz", "ronjutsu", "games"]
    for t in todo:
        {"quiz": build_quiz, "ronjutsu": build_ronjutsu, "games": build_games}[t]()

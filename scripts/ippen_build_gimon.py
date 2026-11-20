#!/usr/bin/env python3
"""いっぺんの入れかえ（2026-11-20）：/shikaku-guide/gimon/（キャリコンって何？よくある質問40問）を
ラフ05「資格を知る」の型（careers/index.html と同じ組み）で組みなおす道具。

- 40問の問い・答え・出典・確かめた日・リンク・id（#t01〜#t40・#k-◯◯・#you・#kw）・data-ev はそのまま写す
- 並び：ヒーロー（小山に悩んでいる人）→ 答え（芝生）→ 目次 → さがす道具（あお）→ まとまりごとの段（10）→ 次の一歩 → ピクニックの絵 → 次の段
- 新しく書いたのは、頭の段の悩み・答えの1行・目次の答えの1行・このページの説明の1行だけ（NEW_ で始まる文字）
- 頭（title・説明文・canonical・OGP・構造化データ）は本番のまま。CSS は kata.css＋このページの部品の見た目
- 何度流しても同じ結果になるよう、元のページは scratchpad の ippen_moto/ の控えから読む

使い方: python3 scripts/ippen_build_gimon.py
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ippen_parts as P  # noqa: E402
import ippen_from_rough as R  # noqa: E402
import ippen_yomiyasu as Y  # noqa: E402
import ippen_kotei_1120 as K  # noqa: E402  11/20 出す前の直し（組み直しても消えない）

PATH = "shikaku-guide/gimon/index.html"
MOTO = "/private/tmp/claude-501/-Users-iwawakiasako/b0ab8e18-46b0-4dd4-a73e-3ba79d54a7bf/scratchpad/ippen_moto/shikaku-guide_gimon_index.html"

# ---- 新しく書いた文（ここだけ） ----
NEW_QB = '<span class="lb">このページで答える悩み</span>気になることが多すぎて、<br>何から聞けばいいの？<small>なるには・費用・稼げる？</small>'
NEW_ANSWER_H2 = "何から読めばいい？"
NEW_ANSWER = '<b class="mark">知りたい言葉でさがす</b>か、10のまとまりから選べば、気になる答えだけ1分で読めるよ。'
NEW_WHO_FOR = "このページは、キャリアコンサルタントの資格が気になりはじめた人が、「なるには・費用・稼げる？・やめとけって本当？」の気になることを、1問ずつ確かめるためのページです。"
NEW_TOC = {  # まとまりごとの答えの1行
    "k-what": "働く人の仕事選びを支える国家資格",
    "k-yametoke": "使う場所がある人には価値がある",
    "k-muki": "「聴くのが好き」が出発点",
    "k-kasegu": "いまの仕事に足すと活きる",
    "k-naru": "養成講習→試験→登録の順",
    "k-okane": "最初は35〜55万円前後。給付金で下がる",
    "k-ryoritsu": "土曜だけ・オンラインのクラスもある",
    "k-koshu": "聴く力は、練習で身につく",
    "k-erabu": "2〜3校にしぼって説明会へ",
    "k-shiken": "学科と実技。片方ずつ受け直せる",
}

# このページの部品（さがす道具・開く問い・キャラの吹き出し）を、新しい型の色と字にそろえる
STYLE = """<style id="gimon-kata">
body.kata main{display:block}
body.kata .visually-hidden{position:absolute!important;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
body.kata [hidden]{display:none!important}
body.kata .kwbox{background:#fff;border-radius:22px;padding:22px 20px;margin:18px 0;box-shadow:none;border:1.5px solid var(--line)}
body.kata .kwfind__label{display:block;font-weight:700;font-size:15px;margin:14px 0 6px}
body.kata .kwfind input,body.kata .kwfind select{width:100%;font:inherit;font-size:16px;padding:12px 14px;border:1.5px solid #BFD3EA;border-radius:14px;background:#fff;color:var(--ink)}
body.kata .kwfind input:focus,body.kata .kwfind select:focus{outline:3px solid var(--hat);border-color:var(--link)}
body.kata .kwfind__count{color:var(--link);font-weight:700;min-height:1.4em;margin:12px 0 0}
body.kata .pdrop{border:0!important}
body.kata .pdrop summary{display:block;padding:12px 40px 12px 14px;border:1.5px solid #BFD3EA;border-radius:14px;background:#fff;font-weight:500;font-size:16px}
body.kata .pdrop summary::after{content:"";position:absolute;right:16px;top:50%;width:8px;height:8px;border-right:2px solid var(--ink);border-bottom:2px solid var(--ink);transform:translateY(-70%) rotate(45deg)}
body.kata .pdrop[open] summary{border-color:var(--link)}
body.kata .pdrop__panel{border:1.5px solid var(--link);border-top:0;border-radius:0 0 14px 14px;background:#fff;padding:6px 14px 14px}
body.kata label.pcheck{border-bottom:1px dashed var(--line)}
body.kata .pcheck input{accent-color:var(--link)}
body.kata .pgo{background:var(--link);box-shadow:none;letter-spacing:.08em}
body.kata .pgo:hover,body.kata .pgo:focus{background:#1F5A99}
body.kata .pdrop__ok{color:var(--link)!important;border-color:var(--link)!important}
body.kata .pmsg.is-ok{color:var(--link)}
body.kata .prec{background:var(--pale)}
body.kata .prec__title{color:var(--ink)}
body.kata .gimon-none{margin:18px 0}
body.kata .gimon-note{margin:14px 0 0;font-size:13.5px;line-height:1.85;color:var(--sub)}
body.kata .mini-say{display:grid;grid-template-columns:52px minmax(0,1fr);gap:12px;align-items:start;margin:12px 0}
body.kata .mini-say__avatar img{width:52px;height:52px;object-fit:contain}
body.kata .mini-say__bubble{margin:0;padding:10px 16px;border-radius:16px;background:#fff;border:1.5px solid #BFD3EA;font-size:15px;line-height:1.85}
body.kata .mini-say--moyan .mini-say__bubble{background:#FFF1C9;border-color:#FFF1C9}
body.kata .mini-say__bubble>b{display:block;font-size:12px;font-weight:500;color:var(--sub);letter-spacing:.1em}
body.kata .mini-say__bubble strong{font-weight:500;background:linear-gradient(transparent 60%,#FFEDA6 60%,#FFEDA6 94%,transparent 94%)}
body.kata .kwsec{scroll-margin-top:12px;margin-top:0}
body.kata .kwsec>.w>.mini-say{margin:6px 0 18px}
body.kata .kwsec__back{text-align:right;font-size:13.5px;margin:16px 0 0}
body.kata .gimon{background:#fff;border:1.5px solid var(--line)!important;border-radius:18px;margin:14px 0;box-shadow:none;scroll-margin-top:12px}
body.kata .gimon summary{display:flex;gap:14px;align-items:flex-start;padding:18px 46px 18px 16px;font-weight:500;position:relative;justify-content:flex-start}
body.kata .gimon__qt{flex:1;min-width:0}
body.kata .gimon__cta .button{margin:0 8px}
body.kata .gimon summary::after{content:"＋";position:absolute;right:18px;top:18px;color:var(--link)}
body.kata .gimon[open] summary::after{content:"－"}
body.kata .gimon__mark{flex:none;width:30px;height:30px;border-radius:50%;background:var(--hat);color:var(--ink);font-family:Outfit,sans-serif;font-weight:500;display:grid;place-items:center}
body.kata .gimon__q{display:block;font-weight:700;font-size:16px;line-height:1.7}
body.kata .gimon__a{display:block;margin-top:6px;color:var(--sub);font-weight:500;font-size:14.5px;line-height:1.7}
body.kata .gimon__a::before{content:"→ "}
body.kata .gimon__points{list-style:none;margin:0;padding:12px 20px 6px;border-top:1.5px dashed var(--line)}
body.kata .gimon__points li{position:relative;padding:6px 0 6px 26px;line-height:1.8;font-size:15px}
body.kata .gimon__points li::before{content:"";position:absolute;left:4px;top:.95em;width:12px;height:6px;border-left:3px solid var(--link);border-bottom:3px solid var(--link);transform:rotate(-45deg)}
body.kata .gimon__detail{padding:4px 20px 22px;font-size:15px}
body.kata .gimon__detail h4{margin:28px 0 10px;font-size:15.5px;font-weight:700;color:var(--ink);padding-left:12px;border-left:4px solid var(--hat)}
body.kata .gimon__detail p{margin:0 0 14px;line-height:1.95}
body.kata .gimon__you,body.kata .gimon__todo{margin:0;padding-left:1.2em;line-height:1.9}
body.kata .gimon__you li,body.kata .gimon__todo li{margin-bottom:8px}
body.kata .gimon__you li.is-you{list-style:none;margin-left:-1.2em;background:var(--pale);border-radius:14px;padding:10px 14px}
body.kata .gimon__you li.is-you::before{content:"あなた向け";display:inline-block;background:var(--link);color:#fff;font-size:12px;font-weight:700;border-radius:999px;padding:0 10px;margin-right:8px}
body.kata .gimon__src{font-size:12.5px;color:var(--sub);margin:22px 0 0!important;line-height:1.8!important}
body.kata .gimon__cta{margin:28px 0 0;padding:18px 16px;background:var(--pale);border-radius:18px;text-align:center}
body.kata .gimon__cta p{margin:0 0 10px!important;font-weight:700}
body.kata .gimon__cta2{display:inline-block;margin-top:10px;font-size:14px}
body.kata a.button{display:inline-flex;align-items:center;justify-content:center;gap:6px;padding:11px 22px;border-radius:999px;border:1.5px solid var(--link);background:#fff;color:var(--link);text-decoration:none;font-weight:700;font-size:15px;letter-spacing:.06em}
body.kata mark.mk{background:linear-gradient(transparent 58%,#FFEDA6 58%);color:inherit;font-weight:500;padding:0 2px}
body.kata .disclosure{margin:14px 0 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
body.kata .disclosure__title{font-size:13.5px;font-weight:500}
body.kata .disclosure__tag{display:inline-block;margin-right:8px;padding:0 8px;border:1px solid #9FB3CE;border-radius:4px;font-size:12px}
body.kata .disclosure__more{margin-left:auto;font-size:12.5px;color:var(--sub)}
body.kata .disclosure__list{margin:0 0 12px;font-size:13.5px}
body.kata .disclosure__list div{display:grid;grid-template-columns:8em minmax(0,1fr);gap:8px;padding:4px 0}
body.kata .disclosure__list dt{color:var(--sub)}body.kata .disclosure__list dd{margin:0}
body.kata .updated-date{display:flex;flex-wrap:wrap;gap:4px 16px;margin:6px 0 0;font-size:12.5px;color:var(--sub)}
body.kata .shikaku-steps{margin:8px 0 0;padding-left:1.4em;line-height:2}
body.kata .hero__actions{display:flex;flex-wrap:wrap;gap:12px}
body.kata .next-compare{font-size:15px}
body.kata .setsumei-box{margin:28px auto 0;max-width:640px;padding:20px 22px;border-radius:18px;background:var(--pale);text-align:center}
body.kata .setsumei-box p{margin:0 0 10px}
body.kata .setsumei-box__t{font-weight:700;font-size:16px}
@media (max-width:760px){body.kata .mini-say{grid-template-columns:44px minmax(0,1fr)}body.kata .mini-say__avatar img{width:44px;height:44px}
body.kata .gimon__detail{padding:4px 14px 18px}body.kata .disclosure__list div{grid-template-columns:1fr;gap:0}}
</style>"""


def strip_tags(t):
    return re.sub(r"<[^>]+>", "", t)


def main():
    if not os.path.exists(MOTO):
        os.makedirs(os.path.dirname(MOTO), exist_ok=True)
        with open(os.path.join(P.ROOT, PATH), encoding="utf-8") as fh:
            src = fh.read()
        with open(MOTO, "w", encoding="utf-8") as fh:
            fh.write(src)
    src = open(MOTO, encoding="utf-8").read()
    head, body = src.split("</head>", 1)
    r = P.rel_root(PATH)

    # ---- 頭：本番のまま（計測・メタ・構造化データ）＋新しい型の CSS ----
    meta = R.head_from_prod(src)
    ld = re.findall(r'<script type="application/ld\+json">.*?</script>', head, re.S)
    page_style = re.search(r"<style>\s*\.kwbox\{.*?</style>", head, re.S).group(0)  # 元のページの部品の見た目
    new_head = "\n".join([
        '<!doctype html>\n<html lang="ja">\n<head>\n<meta charset="utf-8">', R.ANALYTICS, meta, R.FONTS,
        f'<link rel="stylesheet" href="{r}css/kata.css?v=2026.1120">', *ld, page_style, STYLE, R.H1_SP,
        P.css_link(PATH), "</head>",
    ])

    # ---- 本文のかたまりを取り出す ----
    def grab(rx):
        m = re.search(rx, body, re.S)
        if not m:
            raise SystemExit("見つからない: " + rx[:60])
        return m.group(0)

    h1_inner = re.search(r"<h1>(.*?)</h1>", body, re.S).group(1)
    lede = grab(r'<p class="article-header__lede">.*?</p>')
    updated = grab(r'<p class="updated-date">.*?</p>')
    disclosure = grab(r'<details class="disclosure".*?</details>')
    moyan_q = re.search(r'chara-guide--moyan.*?<p class="chara-guide__bubble">(.*?)</p>', body, re.S).group(1)
    sunny_a = re.search(r'chara-guide--sunny.*?<p class="chara-guide__bubble">(.*?)</p>', body, re.S).group(1)
    kw_you = grab(r'<div class="kwbox" id="you">.*?\n  </div>\n')
    kw_kw = grab(r'<div class="kwbox" id="kw">.*?\n  </div>\n')
    note = grab(r'<p class="gimon-note">.*?</p>')
    none = grab(r'<div class="gimon-none" id="gn" hidden>.*?</div></div>')
    secs = re.findall(r'<section id="(k-[a-z]+)" class="kwsec">(.*?)</section>', body, re.S)
    scripts = re.findall(r"\n  <script>\n.*?\n  </script>\n", body, re.S)
    nxt = grab(r'<section id="next" class="shikaku-next">.*?</section>')
    next_compare = grab(r'<p class="next-compare".*?</p>')
    setsumei = grab(r'<aside class="setsumei-box".*?</aside>')

    # ---- 組む ----
    hero = f"""<section class="hero1"><div class="w">
  <p class="eye">はじめての方へ</p>
  <h1>{h1_inner.replace('</span>', '</span><br>', 1)}</h1>
  <div class="hstage">
    <img class="garl" src="{r}img/kata/sora_garland.webp" alt="" aria-hidden="true">
    <img class="cld c1" src="{r}img/parts/01_sky_cloud_left.webp" alt="" aria-hidden="true">
    <img class="cld c2" src="{r}img/parts/03_sky_cloud_right.webp" alt="" aria-hidden="true">
    <p class="qb">{NEW_QB}</p>
    <div class="who1" aria-hidden="true">
      <span class="hm m1">？</span><span class="hm m2">？</span>
      <span class="mpic"><img class="hito" src="{r}img/kata/hito_5_mada.webp" alt=""></span>
    </div>
    <img class="deco tent" src="{r}img/parts/t/13_blue_yellow_tent-136.webp" alt="" aria-hidden="true">
    <img class="deco fl1" src="{r}img/parts/t/23_flowers_left_group-180.webp" alt="" aria-hidden="true">
    <img class="deco fl2" src="{r}img/parts/t/25_flowers_right_group-180.webp" alt="" aria-hidden="true">
    <img class="deco bu1" src="{r}img/parts/t/24_bush_lower_left-136.webp" alt="" aria-hidden="true">
    <img class="deco bu2" src="{r}img/parts/t/26_bush_lower_right-136.webp" alt="" aria-hidden="true">
  </div>
  <i class="oka" aria-hidden="true"></i>
</div></section>"""

    kotae = f"""<section class="sec2 green" id="kotae"><div class="w nar">
  <p class="eye c">答え</p>
  <h2 class="c">{NEW_ANSWER_H2}</h2>
  <div class="guide-mo solo"><p><span class="who">モヤン</span>{moyan_q}</p><img src="{r}img/parts/t/moyan_school_hat_smile-200.webp" alt="モヤン" loading="lazy" decoding="async"></div>
  <div class="sun2 rise">
    <img src="{r}img/kata/sunny.webp" alt="サニー先生" loading="lazy" decoding="async">
    <p class="sb"><span class="who">サニー先生</span>{sunny_a}<br>{NEW_ANSWER}</p>
  </div>
</div></section>"""

    toc_items = []
    for i, (sid, inner) in enumerate(secs, 1):
        toc_items.append(f'<li><a href="#{sid}"><span class="tn">{i}</span><span class="tx">{NEW_TOC[sid]}</span></a></li>')
    mokuji = f"""<section class="sec2" id="mokuji"><div class="w nar">
  <nav class="toc toc3" aria-label="このページの目次"><p class="tt">このページでわかること（40問）</p><ol>{''.join(toc_items)}</ol><p class="tsub"><a href="#kw">ことばでさがす</a>・<a href="#tsugi">次の一歩</a></p></nav>
  <div class="lead2">
    <p class="who-for"><b>{NEW_WHO_FOR}</b></p>
    {lede.replace('class="article-header__lede"', 'class="lede"')}
    {updated}
    {note}
  </div>
  {disclosure}
</div></section>"""

    tool = f"""<section class="sec2 sky" id="tool"><div class="w nar">
  <p class="eye c">さがす</p>
  <h2 class="c">知りたいことから、さがす</h2>
  {kw_you.strip()}
  {kw_kw.strip()}
  {none}
</div></section>"""

    parts = []
    for i, (sid, inner) in enumerate(secs, 1):
        inner = inner.strip("\n")
        inner = re.sub(r"^\s*<h2>", f'<p class="eye">くわしく {i}</p>\n    <h2>', inner, count=1)
        parts.append(f'<section id="{sid}" class="kwsec sec2 hb"><div class="w nar">\n{inner}\n</div></section>')
    kwsecs = '<div id="faq">\n' + "\n\n".join(parts) + "\n</div>"

    tsugi = nxt.replace('<section id="next" class="shikaku-next">', '<section class="sec2" id="tsugi"><div class="w nar">', 1)
    tsugi = tsugi.replace("<h2>", '<p class="eye c">次の一歩</p>\n    <h2 class="c">', 1)
    tsugi = tsugi[: tsugi.rfind("</section>")] + f"  {next_compare}\n  {setsumei}\n</div></section>"

    picnic = f"""<section class="picnic" aria-hidden="true"><div class="kscene">
  <img class="flags2" src="{r}img/kata/sora_garland.webp" alt="" loading="lazy" decoding="async">
  <img class="pic" src="{r}img/kata/hero_picnic.webp" alt="" loading="lazy" decoding="async">
</div></section>
<section class="nxt"><div class="w">
  <div class="box"><img src="{r}img/kata/sunny.webp" alt="" loading="lazy" decoding="async"><div><p class="now">いまは 段1「知る」。次は</p><p class="go"><span class="stepno">2</span><a href="/schools/compare/">学校選び（6校の比較表）</a> →</p></div><p class="more" style="margin:0;font-size:13.5px"><a class="tl" href="#sitemap">キャリコンへの道を、ぜんぶ見る</a></p></div>
  <p class="back"><a href="/careers/">← キャリコンとは（仕事と資格）にもどる</a></p>
</div></section>"""

    sticker = re.search(r"<svg width=\"0\".*?</svg>", open(os.path.join(P.ROOT, "careers/index.html"), encoding="utf-8").read(), re.S).group(0)
    crumb = P.crumb_html([("ホーム", "/"), ("資格まるわかりガイド", "/shikaku-guide/"), ("資格Q&amp;A 40問", None)])
    tail_scripts = [f'<script src="{r}js/reveal.js?v=2026.1018b" defer></script>',
                    f'<script src="{r}js/term-hints.js?v=v2026.1018" defer></script>',
                    "<script>(function(){var r=document.querySelectorAll('.rise');if(!('IntersectionObserver' in window)){r.forEach(function(e){e.classList.add('on')});return;}var o=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('on');o.unobserve(e.target);}});},{threshold:.3});r.forEach(function(e){o.observe(e)});})();</script>"]
    out = "\n".join([
        new_head, '<body class="kata">', sticker, P.top_parts(PATH, crumb).rstrip(),
        '<main data-lb="1" id="main">', hero, "", kotae, "", mokuji, "", tool, "", kwsecs, "", tsugi,
        "".join(scripts).rstrip(), "</main>", picnic, P.end_parts(PATH).rstrip(), *tail_scripts, "</body>\n</html>\n",
    ])
    out = K.apply(PATH, Y.apply(out))   # 11/20 K＝出す前の直し。 見出し・問いを文節で折る印（scripts/ippen_yomiyasu.py）
    with open(os.path.join(P.ROOT, PATH), "w", encoding="utf-8") as fh:
        fh.write(out)
    print(f"{PATH}: {len(out)//1024}KB・まとまり {len(secs)}・問い {out.count('class=\"gimon\"')}")


if __name__ == "__main__":
    main()

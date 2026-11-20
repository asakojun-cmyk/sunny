#!/usr/bin/env python3
"""いっぺんの入れかえ（2026-11-20）：学校ページ3つ（地域連携プラットフォーム・日本マンパワー・リカレント）と
養成学校一覧（/schools/）を、ラフ02（LEC が見本・schools/lec/index.html）と同じ型で組む。

- 中身の元は、入れかえる前の各ページ（控え：MOTO）・data/schools.json・比較表（schools/compare/）だけ。
  新しい数字・声は作らない。確かめた日はそのまま書く
- 紹介リンク（A8）・計測の画像・PR の印は、入れかえる前のページのとおり
- 組み立ては scripts/ippen_from_rough.py の build(dict)（頭・共通の部品・絵の住所）
使い方: python3 scripts/ippen_build_schools.py [chiiki nm rec index]
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ippen_from_rough as R  # noqa: E402
import ippen_parts as P  # noqa: E402

MOTO = "/private/tmp/claude-501/-Users-iwawakiasako/b0ab8e18-46b0-4dd4-a73e-3ba79d54a7bf/scratchpad/ippen_moto"
ROUGH02 = os.path.join(R.ROUGH, "02_学校ページ.html")

SVG = open(ROUGH02, encoding="utf-8").read().split("<body", 1)[1]
SVG = re.search(r"<svg.*?</svg>", SVG, re.S).group(0)
STYLES = re.findall(r"<style\b.*?</style>", open(ROUGH02, encoding="utf-8").read().split("</head>")[0], re.S)
SCRIPTS = re.search(r"(<script>\s*document\.documentElement.*)</body>",
                    open(ROUGH02, encoding="utf-8").read(), re.S).group(1)

KAKITE_KATA = ('<div class="kakite" id="kakite"><p class="kk-t">この記事を書いた人</p><p class="kk-n">キャリコン学びピクニック運営者</p>'
               '<p class="kk-d">3児の母。2026年に、地域連携プラットフォームの養成講習（オンライン・土曜クラス）を修了し、'
               '第33回キャリアコンサルタント試験を受けました（合格発表は2026年12月16日）。<br>数字や日付は、公式の案内で確かめて、確かめた日をつけています。</p></div>')

HERO_DECO = """    <img class="garl" src="{R}img/kata/sora_garland.webp" alt="" aria-hidden="true">
    <img class="cld c1" src="{R}img/parts/01_sky_cloud_left.webp" alt="" aria-hidden="true">
    <img class="cld c2" src="{R}img/parts/03_sky_cloud_right.webp" alt="" aria-hidden="true">
    {qb}
    <div class="who1" aria-hidden="true">
      <span class="hm m1">？</span><span class="hm m2">？</span>
      <span class="mpic"><img class="hito" src="{R}img/kata/{hito}.webp" alt=""></span>
    </div>
    <img class="deco tent" src="{R}img/parts/t/13_blue_yellow_tent-136.webp" alt="" aria-hidden="true">
    <img class="deco fl1" src="{R}img/parts/t/23_flowers_left_group-180.webp" alt="" aria-hidden="true">
    <img class="deco fl2" src="{R}img/parts/t/25_flowers_right_group-180.webp" alt="" aria-hidden="true">
    <img class="deco bu1" src="{R}img/parts/t/24_bush_lower_left-136.webp" alt="" aria-hidden="true">
    <img class="deco bu2" src="{R}img/parts/t/26_bush_lower_right-136.webp" alt="" aria-hidden="true">"""

MOYAN = '{R}img/parts/t/moyan_school_hat_smile-200.webp'
SUNNY = '{R}img/kata/sunny.webp'


def hero(eye, h1, worry, sub, hito):
    qb = f'<p class="qb"><span class="lb">このページで答える悩み</span>{worry}<br><small>{sub}</small></p>'
    return (f'<section class="hero1"><div class="w">\n  <p class="eye">{eye}</p>\n  <h1>{h1}</h1>\n  <div class="hstage">\n'
            + HERO_DECO.replace("{qb}", qb).replace("{hito}", hito) + '\n  </div>\n  <i class="oka" aria-hidden="true"></i>\n</div></section>\n')


def kotae(h2, say, src):
    return (f'<section class="sec2 green" id="kotae"><div class="w nar">\n  <p class="eye c">答え</p>\n  <h2 class="c">{h2}</h2>\n'
            f'  <div class="sun2 rise">\n    <img src="{SUNNY}" alt="サニー先生">\n    <p class="sb"><span class="who">サニー先生</span>{say}</p>\n  </div>\n'
            f'  <p class="src c">{src}</p>\n</div></section>\n')


def toc(items, faq_n, lead, has_voice=True):
    lis = "".join(f'<li><a href="#{i}"><span class="tn">{n}</span><span class="tx">{t}</span></a></li>' for n, (i, t) in enumerate(items, 1))
    sub = (['<a href="#nayami">困った人の声</a>'] if has_voice else []) + ([f'<a href="#faq">よくある質問（{faq_n}問）</a>'] if faq_n else []) + ['<a href="#shutten">出典</a>']
    return (f'<section class="sec2" id="mokuji"><div class="w nar">\n  <nav class="toc toc3" aria-label="このページの目次"><p class="tt">このページでわかること</p>'
            f'<ol>{lis}</ol><p class="tsub">{"・".join(sub)}</p></nav>\n  <div class="lead2">\n{lead}\n  </div>\n</div></section>\n')


def voices(title, aria, items):
    arts = "".join(
        f'<article class="vcase"><div class="vtop"><img src="{{R}}img/kata/{h}.webp" alt=""><p class="vq">{q}</p></div>\n'
        f'<p class="vnote">{note}</p><p class="vans"><b>答え</b>{a}</p></article>' for h, q, note, a in items)
    return (f'<section class="sec2 plain" id="nayami"><div class="w">\n  <div class="gw"><p class="eye c">よくあるお悩み</p><h2 class="c">{title}</h2></div>\n</div>\n'
            f'<div class="vwrap"><div class="vcases hs" id="vcases" tabindex="0" aria-label="{aria}（横に送れます）">{arts}</div></div>\n'
            '<div class="vnav"><button class="varr prev" type="button" aria-label="前の声へ">‹</button><p class="vhint">横にスクロールすると、ほかの声も読めます</p>'
            '<button class="varr next" type="button" aria-label="次の声へ">›</button></div></section>\n')


def pair(moyan, sunny, who="サニー先生の解説"):
    return (f'  <div class="pair"><div class="pm"><p><span class="who">モヤン</span>{moyan}</p><img src="{MOYAN}" alt="モヤン"></div>\n'
            f'  <div class="ps"><img src="{SUNNY}" alt="サニー先生"><p><span class="who">{who}</span>{sunny}</p></div></div>\n')


def table(rows):
    trs = "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in rows)
    return f'  <div class="tblw"><table class="tbl"><tbody>{trs}</tbody></table></div>\n'


def sec(id_, n, h2, inner):
    return (f'<section class="sec2 hb" id="{id_}"><div class="w nar">\n  <p class="eye">くわしく {n}</p>\n  <h2>{h2}</h2>\n{inner}</div></section>\n')


def faq(h2, qas):
    ds = "".join(f'<details><summary><b class="qn">Q{i}.</b>{q}</summary><div class="in">{a}</div></details>' for i, (q, a) in enumerate(qas, 1))
    return (f'<section class="sec2" id="faq"><div class="w nar">\n  <p class="eye c">よくある質問</p>\n  <h2 class="c">{h2}</h2>\n'
            f'  <div class="faq">{ds}</div>\n</div></section>\n')


def shutten(src_note, groups):
    gs = "".join(f'<p class="sh">{t}</p><ul class="srcl">{"".join(f"<li>{x}</li>" for x in xs)}</ul>' for t, xs in groups)
    return (f'<section class="sec2" id="shutten"><div class="w nar">\n  {KAKITE_KATA}\n\n  <p class="eye">出典</p>\n'
            f'  <p class="src">{src_note}</p>\n  {gs}\n</div></section>\n')


def tsugi(h2, cards):
    cs = "".join(f'<a class="ncard" href="{h}"><span class="nn">{a}</span><span class="tl">{b}</span></a>' for h, a, b in cards)
    return (f'<section class="sec2" id="tsugi"><div class="w">\n  <p class="eye c">次の一歩</p>\n  <h2 class="c">{h2}</h2>\n'
            f'  <div class="next3">{cs}</div>\n</div></section>\n')


END = f"""<section class="picnic" aria-hidden="true"><div class="kscene">
  <img class="flags2" src="{{R}}img/kata/sora_garland.webp" alt="">
  <img class="pic" src="{{R}}img/kata/hero_picnic.webp" alt="">
</div></section>
<section class="nxt"><div class="w">
  <div class="box"><img src="{SUNNY}" alt=""><div><p class="now">いまは 段2「学校選び」。次は</p><p class="go"><span class="stepno">3</span><a href="#">入学が決まったら、試験までの勉強の道へ</a> →</p></div><p class="more" style="margin:0"><a class="tl" href="#">キャリコンへの道を、ぜんぶ見る</a></p></div>
  <p class="back"><a href="#">← 前の段「知る」にもどる</a></p>
</div></section>
<footer class="ft"></footer>
"""

APPLY_STYLE = ('<style>/* このページだけ：説明会の段の並び */\nbody.kata #apply-h .ctaw{margin:26px 0 0}\nbody.kata #apply-h .prnote{margin:0}\n'
               'body.kata .tblw .tbl th{width:9.5em}</style>')


def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>"


AUTHOR = {"@type": "Person", "name": "キャリコン学びピクニック運営者",
          "description": "3児の母。2026年に養成講習（オンライン・土曜クラス）を修了し、第33回キャリアコンサルタント試験を受験。"}


def article(headline, desc):
    return ld({"@context": "https://schema.org", "@type": "Article", "headline": headline, "description": desc,
               "dateModified": "2026-11-20", "inLanguage": "ja", "author": AUTHOR,
               "publisher": {"@type": "Organization", "name": "キャリコン学びピクニック"}})


def faq_ld(qas):
    strip = lambda t: re.sub(r"<[^>]+>", "", t)  # noqa: E731
    return ld({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": strip(q), "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in qas]})


def moto_ld(name, typ):
    s = open(os.path.join(MOTO, name), encoding="utf-8").read()
    for j in re.findall(r'<script type="application/ld\+json">.*?</script>', s, re.S):
        if f'"@type":"{typ}"' in j.replace(" ", "")[:200]:
            return j
    return ""


def page_html(head_extra, body, path):
    r = P.rel_root(path)
    head = "<!doctype html>\n<html lang=\"ja\">\n<head>\n" + "\n".join(head_extra) + "\n" + "\n".join(STYLES) + "\n" + APPLY_STYLE + "\n</head>\n"
    b = f'<body class="kata">\n{SVG}\n' + body + END + SCRIPTS + "</body>\n</html>\n"
    return (head + b).replace("{R}", r)


def cta(href, label, ev, img=""):
    return (f'  <p class="ctaw"><a class="cta" data-ev="{ev}" href="{href}" rel="sponsored noopener noreferrer" target="_blank">{label}</a>{img}</p>\n')


# ------------------------------------------------------------------ 地域連携プラットフォーム
def chiiki():
    path = "schools/chiiki-renkei-platform/index.html"
    A8 = "https://px.a8.net/svt/ejp?a8mat=459JRK+G3ASDU+59PG+60OXE"
    IMG = '<img border="0" width="1" height="1" src="https://www10.a8.net/0.gif?a8mat=459JRK+G3ASDU+59PG+60OXE" alt="" style="position:absolute" loading="lazy" decoding="async">'
    SETSU = "https://px.a8.net/svt/ejp?a8mat=459JRK+G3AT5M+59PG+BW8O2&amp;a8ejpredirect=https%3A%2F%2Fcareerjp.work%2Fcc1%2Fsetsumeikai"
    OFFICIAL = "https://px.a8.net/svt/ejp?a8mat=459JRK+G3AT5M+59PG+BW8O2&amp;a8ejpredirect=https%3A%2F%2Fcareerjp.work%2Fcc1%2F"
    MEIJI = "https://px.a8.net/svt/ejp?a8mat=459JRK+G3AT5M+59PG+BW8O2&amp;a8ejpredirect=https%3A%2F%2Fcareerjp.work%2Fcc1%2Fpdf%2Fmeijisho_r7.pdf"
    qas = [
        ("地域連携プラットフォームの受講料は、いくらですか？", "297,000円(税込)です。入学金はなく、テキスト代もこみです。キャンペーンや特典で変わることがあります。"),
        ("オンラインだけで修了できますか？", "できます。運営者が説明会の前にメールで聞いたところ、「すべてオンラインで完結します」という答えでした。通学5日間＋オンライン5日間のハイブリッドコースもあります。"),
        ("休んだときは、振替できますか？", "Zoom講習80時間のうち16時間まで、無料で振り替えられます。説明会では、2時間単位で、同じ期のほかの曜日のコースに振り替えられると説明がありました。"),
        ("試験対策講座は、受講料に入っていますか？", "入っていません。国家試験の対策講座は養成講習とは別の講座で、受講生・卒業生価格で受けられます。"),
        ("説明会のあとに、勧誘はありますか？", "運営者が参加したときは、ありませんでした。電話もメールも来ていません。"),
    ]
    desc = "運営者が受けて修了した、地域連携プラットフォームのキャリアコンサルタント養成講習。受講料29万7,000円（入学金なし・テキスト代こみ）、すべてオンラインで修了。説明会に出た話・メールで聞いた答えと、公式の情報をまとめました。"
    body = hero("地域連携プラットフォームのキャリアコンサルタント養成講習",
                '<span class="nw">地域連携プラットフォーム<span class="pr">PR</span>は</span><br>実質14.85万円（総額29.7万円）',
                "受けた人は、どうだった？<br>説明会って、どんな感じ？", "家から、最後まで続けられる？", "hito_1_cost")
    body += kotae("地域連携プラットフォームは、全部でいくら？",
                  '入学金なし・テキスト代こみで<b class="mark">29万7,000円</b>。給付金で半分戻ると、実質<b class="mark">148,500円</b>だよ。運営者のちゃんが、ここで受けて修了したんだ。',
                  "実質＝給付金で半分戻ったときの額。各校の明示書・厚生労働省の講座検索システム（2026年11月15〜16日に確かめました）")
    body += toc([("kotae", "総額29.7万円。半分戻ると実質14.85万円"), ("why", "運営者が選んだのは、費用・オンライン・日程・説明会"),
                 ("kai", "説明会は少人数。勧誘の電話もメールもなし"), ("mailqa", "メールで聞いたら、12の質問に答えてくれた"),
                 ("after", "受けてみて、もっと聞きたかったこともあった"), ("official", "公式サイトで確かめた13項目"),
                 ("apply-h", "説明会では、カメラと振替と試験対策の費用を聞く")], 5,
                '    <p class="who-for"><b>このページは、地域連携プラットフォームの養成講習が気になる人が、「受けた人はどうだった？ 全部でいくら？」を確かめるためのページです。</b></p>\n'
                '    <p>運営者は、この講習を実際に受けて修了しました。受けた本人の話と、公式サイトで確かめた情報を分けて載せています。<br>ほかの学校とくらべたいときは、<a class="tl" href="/schools/compare/#tool">30秒で合う学校をしぼる</a></p>')
    body += ('<section class="sec2 sky" id="why"><div class="w nar">\n  <p class="eye c">受けた本人が選んだ理由</p>\n  <h2 class="c">選んだ理由は、4つ</h2>\n'
             '  <div class="two">\n'
             '    <div class="tcard"><p class="tk">費用</p><p class="tn">申し込んだ当時、わたしが調べた範囲では、金額がいちばん安い学校でした。</p></div>\n'
             '    <div class="tcard"><p class="tk">オンライン</p><p class="tn">オンラインで修了まで完了できるので、子育て中の家庭でも通いやすそうだと思いました。</p></div>\n'
             '    <div class="tcard"><p class="tk">日程</p><p class="tn">授業の日程は選択肢が豊富で、曜日や時間帯をたくさんのパターンから選べます。</p></div>\n'
             '    <div class="tcard"><p class="tk">説明会</p><p class="tn">説明会があったので、安心して申し込めました。</p></div>\n'
             '  </div>\n  <p class="c" style="margin-top:18px">気になった点もあります。卒業後のサポートは別料金です。<br><a class="tl" href="/school-reviews/chiiki-renkei-platform/">受講体験記を読む（よかった点も、困った点も）</a></p>\n'
             '</div></section>\n')
    body += voices("続けられるか、迷った人の声", "続けられるか迷った人の声", [
        ("hito_3_yoru", "仕事と育児で、毎日もう手いっぱい。", "仕事と子育てで毎日に余裕がない中、講座を考えた人の体験記です（note・2025年）。",
         '土日・平日・午前・午後・夜間のコースがあるよ。<a class="tl" href="#official">公式の情報へ</a>'),
        ("hito_1_cost", "通学に長い時間をかけるのは、むずかしい。", "働きながらの子育てで通う時間がとれず、全部オンラインで受けられる所にしぼった、という体験記です（note・2025年）。",
         "すべてオンラインで修了できるよ。"),
        ("hito_4_support", "振り替えができるかを、学校選びの条件にした。", "休んだ回を別の日に受け直せるかを、学校を選ぶ条件にした、という声です（note・2024年）。",
         'Zoom講習80時間のうち16時間まで、無料で振り替えられるよ。<a class="tl" href="#official">公式の情報へ</a>'),
    ])
    n = 1
    body += sec("okane", n, "費用：入学金なし・テキスト代こみ",
                '  <p class="lead1">受講料297,000円（税込）に、<b class="mark">入学金もテキスト代も入っています</b>。</p>\n'
                '  <div class="fig-t" aria-label="地域連携プラットフォームの費用"><div class="ft-row"><span class="ft-b">受講料<small>297,000円（税込）</small></span><span class="ft-a">入学金<small>なし</small></span><span class="ft-a">テキスト代<small>受講料にこみ</small></span></div><i class="ft-line"></i></div>\n'
                '  <p>専門実践教育訓練給付金の対象講座です（給付割合・条件は公式サイトとハローワークで確かめてね）。<br>国家試験の対策講座は、養成講習とは別の講座・別料金です。</p>\n'
                + pair("29万7,000円で、試験までぜんぶおまかせパックかな？", "国家試験の対策講座は別料金なんだ。全部でいくらかかるかは、試験対策も含めて計算しておこうね。")
                + '  <p class="src">公式サイト（2026年10月4日に確かめました）。キャンペーン・特典で変わることがあります</p>\n')
    n += 1
    body += (f'<section class="sec2 hb" id="kai"><div class="w nar">\n  <p class="eye">くわしく {n}</p>\n  <h2>説明会って、どんな感じ？</h2>\n'
             '  <div class="guide-mo solo"><p><span class="who">モヤン</span>説明会って、どんな雰囲気なんだろう。ドキドキするなあ…。</p><img src="' + MOYAN + '" alt="モヤン"></div>\n'
             '  <p class="lead1">説明会は<b class="mark">オンライン（Zoom）で、すべて無料</b>です。</p>\n'
             '  <div id="kai-kihon">\n' + table([
                 ("種類と時間", "講座説明会（約60分）、質問受付会（約40分）、無料の講座体験会（約90分）の3つがあります。全体を知りたいときは、講座説明会です"),
                 ("参加費", "すべて無料"), ("場所", "オンライン（Zoom）。自宅から参加できます"),
                 ("カメラ", "原則ONです。むずかしい場合は、事前にメールで相談できます"),
                 ("日程", "2026年11月は、講座説明会が8回あります。平日の昼12時、夕方17〜18時台、土曜の回があります"),
                 ("申込み", "フォームに名前・メールアドレス・電話番号を入れて、希望の日時を選びます。確認のあと、参加用のZoomのURLがメールで届きます")])
             + f'  <p class="src">出典：<a href="{SETSU}" rel="sponsored noopener nofollow" target="_blank">地域連携プラットフォーム「講座説明会・質問受付会の申込み」</a>（2026年10月6日に確かめました）。日程は変わるので、最新の予定は公式のページで確かめてね。</p>\n  </div>\n'
             '  <h3 style="margin-top:28px">運営者が参加したとき</h3>\n'
             '  <ol class="plain"><li><b>3人の少人数でした。</b>運営者が参加した回は、わたしを入れて3人でした。</li>'
             '<li><b>動画とスライドで説明を聞きます。</b>代表の方の動画と、スライドを使った説明です。講習の流れ、修了の条件、試験、費用と特典の話がありました。</li>'
             '<li><b>大変なところも正直に話してくれます。</b>「16時間休むと、そのぶん課題が16問増えて大変ですよ」「給付金で80%戻るまでの道のりは、なかなか厳しいです」という説明もありました。</li>'
             '<li><b>声を出して質問できます。</b>「対策講座にみんないくら使っているか」のような聞きにくいことにも、金額を出して答えてもらえました。</li>'
             '<li><b>聞き忘れは、あとからでも聞けます。</b>電話やフォームで聞けると案内がありました。</li></ol>\n'
             '  <p>申し込んだあとは、すぐに確認のメールが届き、ZoomのURLは翌日に届きました。<br>説明会のあとの勧誘は、ありませんでした。電話もメールも来ていません。</p>\n'
             '  <details class="more"><summary>くわしく：運営者のひとこと</summary><div class="in">'
             '<p>めちゃくちゃ不安でしたが、少人数で、基本的にはお話を説明してくださり、「不安な点はないですか？」と温かく聞いてくださいました。</p>'
             '<p>Zoomの操作に慣れていなくて、本当にあわあわしました。でも、挙手でも声出しでも、こちらの「質問したい！」という気持ちをくみ取ってくださいました。</p>'
             '<p>わたし以外の人は、あまり質問がなかったように思います。せっかくなら、質問を考えてから臨んでもいいのかなと思います。</p>'
             '<p>聞いておくべきは、子どものことですね。子どもが画面に映ってはいけないことを、わたしは受講前に知りませんでした。</p></div></details>\n'
             '</div></section>\n')
    n += 1
    mail = [("合格率の分母は「受験した人」か「受講生全体」か", "その試験回に当たる受講生が分母です。"),
            ("受講を始めてから修了までに、やめる人の割合は", "おおよそ1%未満です。"),
            ("給付金の申請を、学校はどこまで手伝ってくれるか", "制度の説明はハローワークでていねいにしてもらえます。学校は、手続きに必要な書類を用意してくれます。"),
            ("オンラインだけで実習まで終わるか。対面の日はあるか", "すべてオンラインで完結します。"),
            ("卒業した人の進路の割合（独立・企業内・副業・活動していない）", "学校が公開している「明示書」に書いてあります（このページの下の「出典」からも見られます）。"),
            ("この学校ならではの、卒業生どうしのつながりや継続サポートは", "学校としては特別には行っていません。親会社が運営する「キャリア・オアシス」で、つながりづくりと継続学習ができます。"),
            ("卒業後に、活動の場に登録して動けるか", "「キャリア・オアシス」で活動できます。"),
            ("主婦・ママ・転勤族の妻の受講生の割合や、活動している卒業生の事例", "集計していないので、答えは控えるとのことでした。")]
    kai_qa = [("本番そっくりの試験対策講座はあるか。費用は", "「キャリア・オアシス」などで試験の直前に開かれます。試験官役2人を置いたロールプレイの練習があり、教室（埼玉・志木）なら5,000ポイント（5,000円）、外部の会場なら13,800ポイント前後という説明でした。"),
              ("受講生は、試験対策にどのくらいお金をかけているか", "平均で3万円〜5万円ぶんの対策講座やレッスンを使う人が多いそうです。まったく使わない人もいます。"),
              ("資格を取ったあとの仕事の相談はできるか", "講義の中や、対策講座・面談練習会で講師に質問できます。合格後に講習のアシスタント（報酬あり）をして、横のつながりを作ることもできるそうです。"),
              ("休んだときの振替は", "合計16時間までできます。2時間単位で、同じ期のほかの曜日のコースに振り替えられます。")]
    body += sec("mailqa", n, "メールと説明会で聞いた質問と答え",
                '  <p class="lead1">説明会に申し込むとき、気になることを<b class="mark">メールで送ると、ひとつずつ返事</b>が届きました（2026年5月の回答です）。</p>\n'
                + table([(f"Q {q}", a) for q, a in mail])
                + '  <details class="more"><summary>くわしく：説明会の中で出た質問と答え（4つ）</summary><div class="in">' + table([(f"Q {q}", a) for q, a in kai_qa]) + '</div></details>\n'
                + pair("聞きにくいお金の話も、ちゃんと答えてもらえるんだね。ちょっと安心した！", "気になることは、そのままにしないのがいちばん。説明会は無料だから、自分の耳でたしかめてみよう。", "サニー先生")
                + '  <p class="src">どれも運営者が参加したときの回答です。金額やルールは変わることがあるので、いまの内容は説明会で聞いてみてね。</p>\n')
    n += 1
    body += sec("after", n, "受けてみて、どうだった？",
                '  <p class="lead1">「組織と人を元気にする」という点は、<b class="mark">もっと聞きたかった</b>です。</p>\n'
                '  <p>ふり返ってみると、「組織と人を元気にする」という点については、授業の内容は薄いように感じました。ファシリテーションなど、組織の中でどう活躍するかという具体的なお話を、もっと聞きたかったです。受講中に先生と連絡先を交換することもできますし、卒業後に「キャリア・オアシス」で相談する、という想定なのかもしれません。</p>\n'
                '  <p>やっぱりこの点は、授業中に先生に聞く。それこそ無料説明会のときに、「具体的に、どうやって組織と人を元気にしていけばいいか、学べるのでしょうか？」と、突っ込んだ質問をするなどがあったほうがいいと思います。</p>\n'
                '  <p>受講料も時間もタダではなく、あなたの人生の投資です。自分の目的を明確にして、学校にお任せではなく、自分がほしい情報や知識をつかみに行ってほしいと思います。</p>\n'
                '  <details class="more"><summary>くわしく：最後に、これから挑戦する人へ</summary><div class="in">'
                '<p>養成学校を卒業したあと、わたしは無料のキャリア相談にチャレンジしています。キャリアコンサルタントになるために、実績を積みたいからです。</p>'
                '<p>これまでに10人ほどと面談しました。ひとつ言えるのは、キャリアコンサルタントは、キャリアで悩んでいる人を元気にできる仕事だということ。その手応えを感じています。</p>'
                '<p>自分の不安な点をきちんと整理して、「自分にプラスになる」と思えるのなら、ぜひ挑戦してほしいです。</p>'
                '<p>わたしは、心からあなたの挑戦を応援しています。一緒にがんばりましょう！</p></div></details>\n'
                '  <p><a class="tl" href="/school-reviews/chiiki-renkei-platform/">授業でよかった点は、受講体験記に</a></p>\n')
    n += 1
    body += sec("official", n, "公式サイトで確かめた情報",
                '  <p class="lead1">受けられる日は<b class="mark">土日祝・平日・午前・午後・夜間</b>から選べます。</p>\n'
                + table([("講習名", "キャリアコンサルタント養成講習（厚生労働大臣認定）"),
                         ("受講形式", "オンライン（Zoom）。通学5日間＋オンライン5日間のハイブリッドコースも選択可"),
                         ("受講期間", "通常コース約3ヶ月／最短最速コース約1.5ヶ月／集中コース約0.5ヶ月"),
                         ("講習時間", "Zoom講習80時間＋通信課題70時間（明示書に記載・2026年7月11日に確かめました）"),
                         ("受講料", "297,000円（税込）。キャンペーン・特典により変わる場合があります"),
                         ("入学金・教材費", "入学金なし・テキスト代込み"), ("定員", "1コース20名"),
                         ("日程", "土曜・日曜・祝日コース／平日コース／午前・午後・夜間コース"),
                         ("振替制度", "Zoom講習80時間のうち16時間まで無料で振替可（2026年7月11日に確かめました）"),
                         ("修了要件", "習得度確認試験合格／出席時間が規定を満たすこと／通信添削課題すべて提出・合格"),
                         ("教育訓練給付", "専門実践教育訓練給付金の対象講座（給付割合・条件は公式サイトとハローワークで要確認）"),
                         ("試験対策講座", "養成講習とは別講座。受講生・卒業生価格で受講可能"),
                         ("卒業後のサポート", "懇親会・情報交換会・就業支援・独立開業支援・上位資格講座・アシスタント参加の機会（公式サイトの記載）。ただし、学校へのメールでの質問には「学校としては特別には行っていない。親会社の「キャリア・オアシス」で活動できる」という答えでした（キャリア・オアシスは別料金）"),
                         ("割引・特典", "給付金対象外特典、ペア特典、シニア特典、紹介特典、子育て特典、学生特典などの記載あり（適用条件は要確認）")])
                + pair("振替が16時間まで無料なら、お休みし放題のフリーパスかも！", "無料の振替は、Zoom講習80時間のうち16時間までだよ。説明会では、休んだぶん課題が増えて大変、という話もあったんだ。")
                + '  <p class="src">公式サイト（項目の日付がないものは2026年10月4日に確かめました）</p>\n')
    n += 1
    body += sec("apply-h", n, "地域連携プラットフォームの説明会の予約先",
                '  <p class="lead1">説明会で聞いておきたいのは、<b class="mark">カメラのきまり・振替・試験対策の費用</b>です。</p>\n'
                '  <ul class="plain"><li>子どもが家にいる時間に受ける場合、カメラのルールはどうなっているか</li><li>休んだときの振替は、何時間まで・どの日にできるか</li><li>試験対策の講座は別料金か。受けるなら全部でいくらか</li></ul>\n'
                '  <p class="prnote"><span class="pr" style="margin:0 4px 0 0">PR</span>広告リンクです（紹介料をいただいています）。運営者はこの講習を受けて修了しました。</p>\n'
                + cta(A8, "無料の説明会・質問会を見てみる", "school_chiiki_kai_setsumeikai", IMG)
                + '  <p class="src">説明会・質問会はオンラインで参加無料。申込みを決めていなくても参加できます。給付金の対象かは、<a class="tl" href="/school-guides/kyufukin-tetsuzuki/">給付金の手続き</a>で見られます。</p>\n')
    body += faq("地域連携プラットフォームのよくある質問", qas)
    body += shutten("本番のページの文（2026年7月11日〜11月15日に確かめた文）と、実質の金額は 2026-11-15〜16", [
        ("学校の案内", [f'<a href="{OFFICIAL}" rel="sponsored noopener nofollow" target="_blank">地域連携プラットフォーム キャリアコンサルタント養成講習（公式サイト）</a>',
                       f'<a href="{MEIJI}" rel="sponsored noopener nofollow" target="_blank">明示書（修了者の進路などの公開資料・PDF）</a>',
                       '<a href="https://www.kyufu.mhlw.go.jp/kensaku/" target="_blank" rel="noopener">教育訓練給付金 検索システム（厚生労働省）</a>']),
        ("受講を考えた人の声（要旨で紹介・ほかの学校の声もふくむ）", ["noteの体験談（2025年）", "noteの体験談（2025年）", "noteの体験談（2024年）"])])
    body += tsugi("ほかの学校とも、くらべてみよう", [("/schools/compare/", "ほかの5校とくらべる", "6校の比較表"),
                                                   ("/school-reviews/chiiki-renkei-platform/", "受けた人の話を読む", "受講体験記"),
                                                   ("/school-guides/kyufukin-tetsuzuki/", "給付金を使うなら", "給付金の手続き")])
    head = [article("地域連携プラットフォームは、総額29.7万円・実質14.85万円", desc), faq_ld(qas),
            moto_ld("schools_chiiki-renkei-platform.html", "Course"),
            '<script type="application/ld+json">{"@type": "BreadcrumbList"}</script>']
    return path, "schools_chiiki-renkei-platform.html", head, body, [("ホーム", "/"), ("講座をえらぶ", "/schools/"), ("地域連携プラットフォーム", None)]


# ------------------------------------------------------------------ 日本マンパワー
def nm():
    path = "schools/nippon-manpower/index.html"
    A8 = "https://px.a8.net/svt/ejp?a8mat=45BQMV+6WV8EY+5MF8+5YJRM"
    IMG = '<img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=45BQMV+6WV8EY+5MF8+5YJRM" alt="" style="position:absolute" loading="lazy" decoding="async">'
    qas = [("日本マンパワーの養成講座は、いくらですか？", "一般受講料は396,000円(税込)です。入学金はなく、教材費もこみです。"),
           ("給付金は使えますか？", "専門実践教育訓練給付制度の対象で、最大80%(約31万円)が給付対象との記載があります。"),
           ("どこで受けられますか？", "通信教育(eラーニング)とスクーリングの両方を受けます。スクーリングは、全国の主要都市の教室か、オンラインで受けられます。"),
           ("休んだときは、振替できますか？", "振替制度があり、通学とオンラインのあいだでも振り替えられます。"),
           ("修了したあとのサポートはありますか？", "CDA資格の取得が可能で、更新講習やコミュニティもあります。")]
    desc = "日本マンパワーのキャリアコンサルタント養成講座は、入学金なし・教材費こみの39.6万円。給付金で半分戻ると実質198,000円。通信＋スクーリング（全国20以上の都市かオンライン）、全国どのクラスにも無料の振替を、公式の情報でまとめました。"
    body = hero("日本マンパワーのキャリアコンサルタント養成講座",
                '<span class="nw">日本マンパワー<span class="pr">PR</span>は</span><br>実質19.8万円（総額39.6万円）',
                "この学校、わたしに合う？<br>全部でいくら？", "引っ越しや転勤があっても、続けられる？", "hito_4_support")
    body += kotae("日本マンパワーの養成講座は、全部でいくら？",
                  '入学金なし・教材費こみで<b class="mark">39.6万円</b>。給付金で半分戻ると、実質<b class="mark">198,000円</b>だよ。',
                  "実質＝給付金で半分戻ったときの額。各校の明示書・厚生労働省の講座検索システム（2026年11月15〜16日に確かめました）")
    body += toc([("kotae", "総額39.6万円。半分戻ると実質19.8万円"), ("shuuryou", "修了は、添削3回とスクーリング76時間以上など"),
                 ("okane", "入学金なし・教材費こみ"), ("hi", "通信＋スクーリング。教室は全国20以上の都市かオンライン"),
                 ("furikae", "休んだら、全国どのクラスにも無料で振替"), ("taisaku", "試験対策はオプション。取ったあとCDA資格も"),
                 ("apply-h", "説明会では、日程とカメラのきまりを聞く")], 5,
                '    <p class="who-for"><b>このページは、日本マンパワーの養成講座が気になる人が、「わたしに合う？ 全部でいくら？」を確かめるためのページです。</b></p>\n'
                '    <p>運営者はこの講座を受講していません。公式サイトで確かめた情報だけでまとめています。<br>ほかの学校とくらべたいときは、<a class="tl" href="/schools/compare/#tool">30秒で合う学校をしぼる</a></p>')
    body += ('<section class="sec2 sky" id="shuuryou"><div class="w nar">\n  <p class="eye c">修了の条件</p>\n  <h2 class="c">修了は、通信とスクーリングの両方で決まる</h2>\n  <div class="two">\n'
             '    <div class="tcard"><p class="tk">通信の添削問題<small>3回を提出</small></p><p class="tv">平均<b class="num">60</b>点以上</p><p class="tn">同社のWebシステム「Web Course-s」で提出します</p></div>\n'
             '    <div class="tcard"><p class="tk">スクーリングの出席<small>12日間・96時間のうち</small></p><p class="tv"><b class="num">76</b>時間以上</p><p class="tn">修了認定試験は60点以上（届かないときは指定会場で受け直し）</p></div>\n'
             '  </div>\n  <p class="src c">出典：日本マンパワーの公式サイト（2026年9月24日に確かめました）</p>\n</div></section>\n')
    body += voices("続けられるか、迷った人の声", "続けられるか迷った人の声", [
        ("hito_1_cost", "通学に長い時間をかけるのは、むずかしい。", "働きながらの子育てで通う時間がとれず、全部オンラインで受けられる所にしぼった、という体験記です（note・2025年）。",
         'スクーリングは、オンラインでも受けられるよ。<a class="tl" href="#hi">受け方と日程へ</a>'),
        ("hito_2_donichi", "できれば、土曜日に開講している所がいい。", "通う日は土日、できれば土曜に開いている講座を探した、という声です（note・2024年）。",
         "オンラインのクラスがあるよ。曜日は、開講の回ごとに公式で確かめてね。"),
        ("hito_4_support", "振り替えができるかを、学校選びの条件にした。", "休んだ回を別の日に受け直せるかを、学校を選ぶ条件にした、という声です（note・2024年）。",
         '全国どのクラスにも、無料で振り替えられるよ。<a class="tl" href="#furikae">振替へ</a>'),
    ])
    body += sec("okane", 1, "日本マンパワーの費用：入学金なし・教材費こみ",
                '  <p class="lead1">一般受講料396,000円（税込）に、<b class="mark">教材費も入っています</b>。入学金はありません。</p>\n'
                '  <div class="fig-t" aria-label="日本マンパワーの費用"><div class="ft-row"><span class="ft-b">受講料<small>396,000円（税込・一般受講料）</small></span><span class="ft-a">入学金<small>なし</small></span><span class="ft-a">教材費<small>受講料にこみ</small></span></div><i class="ft-line"></i></div>\n'
                '  <p>専門実践教育訓練給付制度の対象です。<br>最大80%（約31万円）が給付対象との記載があります。使えるかどうかは、ハローワークで確かめてね。</p>\n'
                + pair("入学金がないのは、うれしいね。", "そう、39.6万円に教材費もこみ。給付金で半分戻ると実質198,000円。全部でくらべると、ほかの学校との差も見えてくるよ。")
                + '  <p class="src">公式サイト（2026年9月24日に確かめました）</p>\n')
    body += sec("hi", 2, "受け方と日程",
                '  <p class="lead1"><b class="mark">通信教育（eラーニング）＋スクーリング</b>で学びます。</p>\n'
                '  <p>スクーリングは、全国の主要都市（20か所以上）の教室か、オンラインで受けます。<br>期間は約3か月（スクーリング12日間）で、クラスは最大20名（クラスにより異なる）です。</p>\n'
                '  <div class="fig-t" aria-label="学ぶ時間の図"><div class="ft-row"><span class="ft-a">通信（eラーニング）<small>Web Course-s で学ぶ</small></span><span class="ft-b">スクーリング<small>12日間・96時間（教室かオンライン）</small></span><span class="ft-c">期間<small>約3か月</small></span></div><i class="ft-line"></i></div>\n'
                '  <p>オンラインのクラスがあります。曜日は、開講の回ごとに公式ページで確かめてね。平日の夜のクラスは、公式ページに記載がありません。</p>\n'
                '  <p>いまの募集（開講日・締切）は、トップの「いまの募集」の表で、確かめた日といっしょに見られます。<a class="tl" href="/#boshu">いまの募集へ</a></p>\n'
                '  <p class="src">公式サイト（2026年11月15日に確かめました）。通信教育をふくむ合計の時間は、公式ページに記載がありません</p>\n')
    body += sec("furikae", 3, "休んだときの振替",
                '  <div class="guide-mo solo"><p><span class="who">モヤン</span>休んだら、取り戻せるの？</p><img src="' + MOYAN + '" alt="モヤン"></div>\n'
                '  <p class="lead1"><b class="mark">全国どのクラスにも、無料で振り替えられます</b>。</p>\n'
                '  <p>何度でも無料で、当日の朝8:30まで変更できます。<br>通学とオンラインのあいだでも振り替えられます（同じ開講月のコースの中で）。</p>\n'
                + pair("引っ越しがあっても、続けられそう？", "教室は全国20以上の都市にあって、通学とオンラインの行き来もできる。「今週は教室、来週は家から」もできるのは心強いね。")
                + '  <p class="src">公式サイト（2026年9月24日に確かめました）</p>\n')
    body += sec("taisaku", 4, "試験対策と、取ったあと",
                '  <p class="lead1">学科・実技試験の対策は、<b class="mark">オプション講座</b>です。</p>\n'
                '  <p>グループワーク・ロールプレイを通じて学びます。<br>資格を取ったあとは、CDA資格の取得が可能で、更新講習やコミュニティもあります。</p>\n'
                '  <p class="src">公式サイト（2026年9月24日に確かめました）</p>\n')
    body += sec("apply-h", 5, "日本マンパワーの説明会の予約先",
                '  <p class="lead1">説明会で聞いておきたいのは、<b class="mark">いまの日程と、カメラのきまり</b>です。</p>\n'
                '  <p class="prnote"><span class="pr" style="margin:0 4px 0 0">PR</span>広告リンクです（紹介料をいただいています）。運営者はこの講座を受講していません。</p>\n'
                + cta(A8, "日本マンパワーの説明会の日程を見る", "end_cta_nippon-manpower", IMG))
    body += faq("日本マンパワーの養成講座のよくある質問", qas)
    body += shutten("本番のページの文（2026年9月24日〜11月15日に確かめた文）と、実質の金額は 2026-11-15〜16", [
        ("学校の案内", [f'<a href="{A8}" rel="sponsored noopener nofollow" target="_blank">日本マンパワー キャリアコンサルタント養成講座（公式サイト）</a>',
                       '<a href="https://www.kyufu.mhlw.go.jp/kensaku/" target="_blank" rel="noopener">教育訓練給付金 検索システム（厚生労働省）</a>']),
        ("受講を考えた人の声（要旨で紹介・日本マンパワー以外の学校の声もふくむ）", ["noteの体験談（2025年）", "noteの体験談（2024年）", "noteの体験談（2024年）"])])
    body += tsugi("ほかの学校とも、くらべてみよう", [("/schools/compare/", "ほかの5校とくらべる", "6校の比較表"),
                                                   ("/school-guides/how-to-choose/", "選ぶ前に決めておく", "3つのこと"),
                                                   ("/school-guides/kyufukin-tetsuzuki/", "給付金を使うなら", "給付金の手続き")])
    head = [article("日本マンパワーは、総額39.6万円・実質19.8万円", desc), faq_ld(qas), moto_ld("schools_nippon-manpower.html", "Course"),
            '<script type="application/ld+json">{"@type": "BreadcrumbList"}</script>']
    return path, "schools_nippon-manpower.html", head, body, [("ホーム", "/"), ("講座をえらぶ", "/schools/"), ("日本マンパワー", None)]


# ------------------------------------------------------------------ リカレント
def rec():
    path = "schools/recurrent/index.html"
    SEMI = "https://px.a8.net/svt/ejp?a8mat=4BE7SX+HV1P6+5BEA+BWVTE&amp;a8ejpredirect=https%3A%2F%2Fwww.recurrent.co.jp%2Fcc%2Fkcc%2Fseminar%2Flist.php"
    OFFICIAL = "https://px.a8.net/svt/ejp?a8mat=4BE7SX+HV1P6+5BEA+BWVTE&amp;a8ejpredirect=https%3A%2F%2Fwww.recurrent.co.jp%2F"
    qas = [("リカレントの養成講座は、全部でいくらですか？", "受講料437,800円、入学金33,000円、教材費28,600円で、合計499,400円(税込)です。"),
           ("給付金は使えますか？", "専門実践教育訓練給付金の対象で、支給率は最大80%との記載があります。"),
           ("夜のクラスはありますか？", "オンラインで、夜8時に始まるクラスがあります。平日の午前・午後のクラスもあります。"),
           ("休んだときは、振替できますか？", "欠席したとき、同じ内容の授業をほかのクラスに振り替えられます。回数や費用の記載はありません。"),
           ("修了したあとのサポートはありますか？", "修了後も個別のキャリアカウンセリングを何度でも受けられます。実務ブラッシュアップ講座や、インターン制度もあります。")]
    desc = "リカレントのキャリアコンサルタント養成講座は、受講料・入学金・教材費で49.94万円。給付金で半分戻ると実質249,700円。通学かオンラインで6か月、夜8時のクラス、修了後の個別相談とインターン制度を、公式の情報でまとめました。"
    body = hero("リカレントのキャリアコンサルタント養成講座",
                '<span class="nw">リカレント<span class="pr">PR</span>は</span><br>実質24.97万円（総額49.94万円）',
                "この学校、わたしに合う？<br>全部でいくら？", "仕事のあと、夜に受けられる？", "hito_3_yoru")
    body += kotae("リカレントの養成講座は、全部でいくら？",
                  '受講料・入学金・教材費で<b class="mark">49.94万円</b>。給付金で半分戻ると、実質<b class="mark">249,700円</b>だよ。',
                  "実質＝給付金で半分戻ったときの額。各校の明示書・厚生労働省の講座検索システム（2026年11月15〜16日に確かめました）")
    body += toc([("kotae", "総額49.94万円。半分戻ると実質24.97万円"), ("shuuryou", "修了の目安は、出席率80%以上"),
                 ("okane", "受講料に、入学金3.3万円と教材費2.86万円"), ("hi", "通学かオンラインで6か月。夜8時のクラスも"),
                 ("furikae", "休んだら、同じ内容の授業をほかのクラスで"), ("taisaku", "学科・論述の対策はコースの中。取ったあとも個別相談"),
                 ("apply-h", "無料セミナーでは、日程とカメラのきまりを聞く")], 5,
                '    <p class="who-for"><b>このページは、リカレントの養成講座が気になる人が、「わたしに合う？ 全部でいくら？」を確かめるためのページです。</b></p>\n'
                '    <p>運営者はこの講座を受講していません。公式サイトで確かめた情報だけでまとめています。<br>ほかの学校とくらべたいときは、<a class="tl" href="/schools/compare/#tool">30秒で合う学校をしぼる</a></p>')
    body += ('<section class="sec2 sky" id="shuuryou"><div class="w nar">\n  <p class="eye c">修了の条件</p>\n  <h2 class="c">修了の目安は、出席率80%以上</h2>\n  <div class="two">\n'
             '    <div class="tcard"><p class="tk">出席率<small>全60回のうち</small></p><p class="tv"><b class="num">80</b>%以上</p><p class="tn">合格保証制度の条件として書かれています</p></div>\n'
             '    <div class="tcard"><p class="tk">授業の時間<small>通学かオンラインのリアルタイムの授業</small></p><p class="tv"><b class="num">150</b>時間</p><p class="tn">休んだ回は、同じ内容の授業をほかのクラスで</p></div>\n'
             '  </div>\n  <p class="src c">出典：リカレントの公式サイト（2026年11月15日に確かめました）。課題の形式は確かめられていません</p>\n</div></section>\n')
    body += voices("続けられるか、迷った人の声", "続けられるか迷った人の声", [
        ("hito_3_yoru", "仕事と育児で、毎日もう手いっぱい。", "仕事と子育てで毎日に余裕がない中、講座を考えた人の体験記です（note・2025年）。",
         '夜8時に始まるクラスがあるよ。<a class="tl" href="#hi">受け方と日程へ</a>'),
        ("hito_4_support", "振り替えができるかを、学校選びの条件にした。", "休んだ回を別の日に受け直せるかを、学校を選ぶ条件にした、という声です（note・2024年）。",
         '欠席したら、同じ内容の授業をほかのクラスで受けられるよ。<a class="tl" href="#furikae">振替へ</a>'),
    ])
    body += sec("okane", 1, "リカレントの費用：入学金と教材費が別",
                '  <p class="lead1">受講料437,800円に、<b class="mark">入学金33,000円と教材費28,600円</b>が足されます（税込）。</p>\n'
                '  <div class="fig-t" aria-label="リカレントの費用"><div class="ft-row"><span class="ft-b">受講料<small>437,800円（税込）</small></span><span class="ft-a">入学金<small>33,000円（税込）</small></span><span class="ft-a">教材費<small>28,600円（税込）</small></span></div><i class="ft-line"></i></div>\n'
                '  <p>専門実践教育訓練給付金の対象です。<br>学費の最大80%・最大39万円との記載があります。使えるかどうかで、実際の負担は大きく変わります。</p>\n'
                + pair("全部で49.94万円……。けっこうするね。", "受講料に入学金3.3万円と教材費2.86万円が足されるからね。学科・論述の対策授業はコースの中にある。全部でくらべると、見え方が変わるよ。")
                + '  <p class="src">公式サイト（2026年11月15日に確かめました）</p>\n')
    body += sec("hi", 2, "受け方と日程",
                '  <p class="lead1"><b class="mark">通学かオンライン</b>をえらべます。</p>\n'
                '  <p>オンラインは、平日の午前・午後に加えて、夜8時に始まるクラスもあります。<br>期間は6か月（全60回）で、少人数制です（具体的な人数の記載なし）。</p>\n'
                '  <div class="fig-t" aria-label="学ぶ時間の図"><div class="ft-row"><span class="ft-a">授業<small>全60回</small></span><span class="ft-b">リアルタイムの授業<small>150時間（通学かオンライン）</small></span><span class="ft-c">期間<small>6か月</small></span></div><i class="ft-line"></i></div>\n'
                '  <p>映像授業は、コースが終わったあとも試験日まで何度でも見られます。</p>\n'
                + pair("夜8時のクラスがあるんだ！", "子どもが寝たあとや、仕事のあとに受けたい人にはうれしいね。期間は6か月（全60回）と長めなので、続けられるペースかも考えておこう。")
                + '  <p>いまの募集（開講日・締切）は、トップの「いまの募集」の表で、確かめた日といっしょに見られます。<a class="tl" href="/#boshu">いまの募集へ</a></p>\n'
                '  <p class="src">公式サイト（2026年9月24日・11月15日に確かめました）</p>\n')
    body += sec("furikae", 3, "休んだときの振替",
                '  <div class="guide-mo solo"><p><span class="who">モヤン</span>休んだら、取り戻せるの？</p><img src="' + MOYAN + '" alt="モヤン"></div>\n'
                '  <p class="lead1">欠席したとき、<b class="mark">同じ内容の授業をほかのクラスに振り替え</b>られます。</p>\n'
                '  <p>回数や費用は、公式ページに記載がありません。説明会で確かめてね。</p>\n')
    body += sec("taisaku", 4, "試験対策と、取ったあと",
                '  <p class="lead1">学科・論述の<b class="mark">対策授業がコースの中に</b>あります。</p>\n'
                '  <p>面接の対策コースは別料金（74,800円）です。<br>ロールプレイング・ケーススタディなどの実践授業があります。</p>\n'
                '  <p>修了したあとも、個別のキャリアカウンセリングを何度でも受けられます。<br>実務ブラッシュアップ講座や、リカレントキャリアセンターなどで実務を経験するインターン制度もあります。</p>\n'
                + pair("取ったあとが不安な人には、心強いね。", "この学校の特ちょうは、修了したあと。個別のキャリア相談を何度でも受けられて、インターン制度で実務も経験できる。", "サニー先生")
                + '  <p class="src">公式サイト（2026年11月15日に確かめました）</p>\n')
    body += sec("apply-h", 5, "リカレントの無料セミナーの予約先",
                '  <p class="lead1">セミナーで聞いておきたいのは、<b class="mark">クラスごとの開講日と、カメラのきまり</b>です。</p>\n'
                '  <p class="prnote"><span class="pr" style="margin:0 4px 0 0">PR</span>広告リンクです（紹介料をいただいています）。運営者はこの講座を受講していません。</p>\n'
                + cta(SEMI, "リカレントの無料セミナーを見る", "end_cta_recurrent"))
    body += faq("リカレントの養成講座のよくある質問", qas)
    body += shutten("本番のページの文（2026年9月24日〜11月15日に確かめた文）と、実質の金額は 2026-11-15〜16", [
        ("学校の案内", [f'<a href="{OFFICIAL}" rel="sponsored noopener nofollow" target="_blank">リカレント（公式サイト）</a>',
                       '<a href="https://www.kyufu.mhlw.go.jp/kensaku/" target="_blank" rel="noopener">教育訓練給付金 検索システム（厚生労働省）</a>']),
        ("受講を考えた人の声（要旨で紹介・リカレント以外の学校の声もふくむ）", ["noteの体験談（2025年）", "noteの体験談（2024年）"])])
    body += tsugi("ほかの学校とも、くらべてみよう", [("/schools/compare/", "ほかの5校とくらべる", "6校の比較表"),
                                                   ("/school-guides/how-to-choose/", "選ぶ前に決めておく", "3つのこと"),
                                                   ("/school-guides/kyufukin-tetsuzuki/", "給付金を使うなら", "給付金の手続き")])
    head = [article("リカレントは、総額49.94万円・実質24.97万円", desc), faq_ld(qas), moto_ld("schools_recurrent.html", "Course"),
            '<script type="application/ld+json">{"@type": "BreadcrumbList"}</script>']
    return path, "schools_recurrent.html", head, body, [("ホーム", "/"), ("講座をえらぶ", "/schools/"), ("リカレント", None)]


# ------------------------------------------------------------------ 一覧
def index():
    path = "schools/index.html"
    six = [  # 比較表の並び（実質の負担が少ない順）。数字は比較表のまま
        ("chiiki-renkei-platform", "school_chiiki", "地域連携プラットフォーム", True, "148,500", "297,000", "土日祝・平日・午前・午後・夜間", "すべてオンラインで修了できる。運営者が受けて修了した学校"),
        ("jaico", "school_jaico", "日本産業カウンセラー協会", False, "165,000", "330,000", "平日昼（月・水・木・金）と土日", "Zoomのライブ授業12日間。修了生の交流の場「CC倶楽部」"),
        ("lec", "school_lec", "LEC東京リーガルマインド", True, "165,000", "330,000", "土日祝・平日夜・半日", "学科・論述・面接の対策Web講座3点セットつき"),
        ("nippon-manpower", "school_manpower", "日本マンパワー", True, "198,000", "396,000", "曜日は開講の回ごとに公式で", "教室は全国20か所以上。全国どのクラスにも無料で振替"),
        ("gcdf", "school_gcdf", "GCDF-Japan", False, "198,000", "396,000", "土日（時期によって平日も）", "1コース18名までの少人数。3回まで無料で振替"),
        ("recurrent", "school_recurrent", "リカレント", True, "249,700", "499,400", "土日・平日夜・平日昼", "夜8時のクラス。修了後も個別のキャリア相談"),
    ]
    ext = {"jaico": "https://www.jaico.cc/", "gcdf": "https://www.career-npo.org/GCDF/"}
    cards = []
    for sid, img, name, pr, jitsu, total, days, memo in six:
        if sid in ext:
            link = f'<a class="tl" href="{ext[sid]}" rel="noopener nofollow" target="_blank">公式サイトを見る</a>'
        else:
            link = f'<a class="tl" href="/schools/{sid}/">くわしく見る</a>'
        prs = '<span class="pr">PR</span>' if pr else ""
        cards.append(f'<div class="card"><img class="ico" src="{{R}}img/kata/{img}.webp" alt="" loading="lazy" decoding="async"><h3>{name}{prs}</h3>'
                     f'<p>給付金で半分戻ると、実質<b class="num">{jitsu}</b>円（総額{total}円）</p><p>受けられる日：{days}</p><p>{memo}</p><p>{link}</p></div>')
    desc = "キャリアコンサルタント養成講座の一覧。通学ゼロで修了できる・土日か夜のクラスがある・休んでも振替できる、を公式ページで確かめた6校を、実質の負担が少ない順に。比較表に入れていない2校の理由も載せています。"
    body = hero("キャリアコンサルタント養成講座の一覧",
                '<span class="nw">養成講座は、</span><br>まず6校から見る',
                "どんな学校があるの？<br>どこから見ればいい？", "多すぎて、ちがいがわからない…", "hito_5_mada")
    body += kotae("養成講座は、どこから見ればいい？",
                  '<b class="mark">通学ゼロ・土日か夜・休んでも振替</b>の3つを公式ページで確かめた6校から見ると、迷いにくいよ。',
                  "6校は、比較表と同じ（2026年10月17日に公式ページで確かめました）。実質＝給付金で半分戻ったときの額（2026年11月15〜16日に確かめました）")
    body += toc([("kotae", "通学ゼロ・土日か夜・振替の3つで、6校"), ("rokkou", "6校を、実質の負担が少ない順に"),
                 ("hoka", "6校に入れていない2校と、その理由"), ("tsugi", "しぼったら、比較表と説明会へ")], 0,
                '    <p class="who-for"><b>このページは、キャリアコンサルタント養成講座を選びたい人が、「どんな学校があるの？」を見わたすためのページです。</b></p>\n'
                '    <p>公式情報・受講者本人の体験・運営者の考察を分けて載せています。<br>料金や日程は変わることがあるので、申し込む前に公式サイトで確かめてね。</p>', has_voice=False)
    body += (f'<section class="sec2 sky" id="rokkou"><div class="w">\n  <p class="eye c">6校の一覧</p>\n  <h2 class="c">6校を、実質の負担が少ない順に</h2>\n'
             f'  <div class="cards">{"".join(cards)}</div>\n'
             '  <p class="src c"><span class="pr" style="margin:0 4px 0 0">PR</span>は広告（紹介料をいただいている学校）です。6校とも同じ項目・同じ確かめ方で載せています。</p>\n'
             '  <p class="c" style="margin-top:18px"><a class="tl" href="/schools/compare/">6校の比較表で、くわしくくらべる</a></p>\n</div></section>\n')
    body += ('<section class="sec2 hb" id="hoka"><div class="w nar">\n  <p class="eye">くわしく 1</p>\n  <h2>6校に入れていない学校</h2>\n  <ul class="plain">\n'
             '    <li><a class="tl" href="/schools/human-academy/">ヒューマンアカデミー</a>：完全オンラインのクラスで、修了の評価までオンラインで受けられるかを、公式ページで確かめられなかったため（確かめ中・2026年9月28日に確かめました）</li>\n'
             '    <li><a class="tl" href="/schools/pasona/">パソナ</a><span class="pr">PR</span>：休んだときの振替の決まりを、公式ページで確かめられなかったため（2026年9月28日に確かめました）</li>\n'
             '  </ul>\n'
             + pair("6校のほかにも、学校はあるの？", "あるよ。この2校は、条件の1つを公式ページで確かめられなかったから、比較表には入れていないんだ。気になるなら、説明会で聞いてみてね。", "サニー先生")
             + '</div></section>\n')
    body += ('<section class="sec2" id="shutten"><div class="w nar">\n  ' + KAKITE_KATA + '\n  <p class="eye">出典</p>\n'
             '  <p class="src">6校の条件は 2026-10-17、実質の金額は 2026-11-15〜16 に確かめた日</p>\n'
             '  <p class="sh">国・学校の案内</p><ul class="srcl"><li><a href="https://www.kyufu.mhlw.go.jp/kensaku/" target="_blank" rel="noopener">教育訓練給付金 検索システム（厚生労働省）</a></li><li>各校の明示書・公式ページ（比較表の各列の出典）</li></ul>\n</div></section>\n')
    body += tsugi("しぼったら、くわしく見よう", [("/schools/compare/", "6校をならべてくらべる", "6校の比較表"),
                                               ("/schools/compare/#apply-h", "説明会で確かめる", "6校の説明会の予約先"),
                                               ("/school-guides/how-to-choose/", "選ぶ前に決めておく", "3つのこと")])
    head = [moto_ld("schools_index.html", "WebPage"),
            ld({"@context": "https://schema.org", "@type": "ItemList", "name": "キャリアコンサルタント養成講習 6校", "numberOfItems": 6,
                "itemListElement": [{"@type": "ListItem", "position": i, "name": n,
                                     "url": ext.get(s) or f"https://carepicnic.com/schools/{s}/"} for i, (s, _, n, *_r) in enumerate(six, 1)]}),
            '<script type="application/ld+json">{"@type": "BreadcrumbList"}</script>']
    return path, "schools_index.html", head, body, [("ホーム", "/"), ("講座をえらぶ", None)]


def run(fn):
    path, moto, head_ld, body, crumbs = fn()
    html = page_html([x for x in head_ld if x], body, path)
    cfg = dict(out=path, head_from=os.path.join(MOTO, moto), crumb=crumbs, rough_html=html, links={}, fix=[])
    R.build(cfg)


if __name__ == "__main__":
    fns = {"chiiki": chiiki, "nm": nm, "rec": rec, "index": index}
    for k in sys.argv[1:] or fns:
        run(fns[k])

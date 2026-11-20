"""1115 のトップのイメージから、本番の形のトップ（sunny-ippen/index.html）を組む。
元のイメージと本番の index.html（origin/main）は読むだけ。"""
import json, re, shutil, subprocess
from pathlib import Path
from bs4 import BeautifulSoup

SCR = Path(__file__).resolve().parent / "_ippen_top_src"  # 11/20 一時置き場から移した（_ つき＝GitHub Pages が公開しない）
SRC = Path("/Users/iwawakiasako/Documents/Obsidian Vault/GitHub/picnic-docs/1108_サイトの設計/イメージ/1115_トップ_草原_Canvaの絵入り_イメージ.html")
REPO = Path("/Users/iwawakiasako/Projects/sunny-ippen")
snap = SCR / "1115_トップ_控え_1119夜.html"
shutil.copyfile(SRC, snap)
src = snap.read_text(encoding="utf-8")
prod = subprocess.run(["git", "-C", str(REPO), "show", "origin/main:index.html"], capture_output=True, text=True, check=True).stdout
imap = json.load(open(SCR / "map.json"))


def rep(s, old, new, count=1):
    n = s.count(old)
    assert n == count, (old[:80], n, count)
    return s.replace(old, new)


head_src, body_src = src.split("</head>", 1)
body_src = body_src.split("<body>", 1)[1].rsplit("</body>", 1)[0]

# ---------- CSS ----------
styles = re.findall(r"<style>(.*?)</style>", head_src, re.S)
assert len(styles) == 2
css = "\n".join(styles)
css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
drop = ("pic-lib", "copy-2", ".h1-b", ".kari", ".meta", ".p-lib")
css = "\n".join(l for l in css.split("\n") if l.strip() and not any(d in l for d in drop))
css = rep(css, ".bn{aspect-ratio", ".cimg{aspect-ratio")
css = rep(css, ".bn img{", ".cimg img{")
css = rep(css, 'url("1115_Canvaの絵入り_素材/gara_kimete.png")', 'url("img/top/gara_kimete.webp")')
css = css.replace("--grass:#ECF0D8", "--grass:#EEF4D6")
assert "1115_" not in css and "file:" not in css
css += """
#kimete{overflow-x:clip}
.hero h1 .h1-big{display:block}
.hero h1 .h1-sub{display:block;margin-top:14px;font-size:15px;line-height:1.8;letter-spacing:.12em;color:var(--sub)}
.ft .map{position:relative;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:24px 32px;margin-top:40px;padding-top:28px;border-top:1px solid rgba(46,74,120,.18)}
.ft .map h4 i{display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;margin-right:6px;border-radius:50%;background:var(--hat);font-family:var(--f-num);font-style:normal;font-size:12px;letter-spacing:0;vertical-align:1px}
.ft .map ul{margin:0;padding:0;list-style:none;font-size:13px;line-height:1.8}
.ft .map li{padding:3px 0}
.ft .map a{color:var(--ink);text-underline-offset:4px}
.ft .notes{position:relative;margin-top:32px;font-size:12.5px;color:var(--sub)}
.ft .notes p{font-size:12.5px}
.ft .copy{position:relative;margin-top:10px;font-size:12px;color:var(--sub)}
.bn{position:sticky;bottom:0;z-index:30;display:none;grid-template-columns:repeat(5,1fr);background:#fff;border-top:1px solid var(--line);font-size:11px;line-height:1.5;letter-spacing:.04em;text-align:center}
.bn a{display:block;color:var(--ink);text-decoration:none}
.bn span{display:block;padding:7px 0 9px}
.bn span i{display:block;font-style:normal;font-size:17px;line-height:1.2}
.bn span.on{color:var(--link);font-weight:700}
@media (max-width:1100px) and (min-width:701px){ .ft .map{grid-template-columns:repeat(2,minmax(0,1fr))} }
@media (max-width:700px){
  .hero h1 .h1-sub{margin-top:10px;font-size:13px;letter-spacing:.06em}
  .ft .map{grid-template-columns:1fr 1fr;gap:20px 16px}
  .bn{display:grid}
}
"""

# ---------- head ----------
P = prod.split("\n")
prod_head = "\n".join(P[3:31])   # meta charset 〜 apple-touch-icon（計測・title・説明文・canonical・OGP・アイコン）
assert prod_head.startswith('<meta charset="utf-8">') and "apple-touch-icon" in P[30] and "G-09GCDPKMKD" in prod_head
old_desc = "30秒で合う学校がわかります。"
new_desc = "いまの自分に近い人を押すと、合う学校がしぼれます。"
prod_head = rep(prod_head, old_desc, new_desc, 2)
ld_web = P[38]
ld_org = P[39]
assert '"@type":"WebSite"' in ld_web and '"@type":"Organization"' in ld_org
ld_web = rep(ld_web, "国家資格キャリアコンサルタント試験に向けて勉強中。", "2026年11月の国家資格キャリアコンサルタント試験を受け終えて、結果待ち（12月16日発表）。")

# ---------- body ----------
b = body_src
b = re.sub(r"<!--.*?-->\n?", "", b, flags=re.S)
b = re.sub(r'<div class="meta">.*?</div></div>\n', "", b, count=1, flags=re.S)
scripts = re.findall(r"<script>.*?</script>", b, re.S)
assert len(scripts) == 2
for s in scripts:
    b = b.replace(s, "")
assert 'class="meta"' not in b
# 絵：webp・相対の住所に
for k, v in imap.items():
    if k == "02_sky_cloud_center.png":
        continue
    b = b.replace(f"1115_Canvaの絵入り_素材/{k}", f"img/top/{v}")
b = b.replace("file:///Users/iwawakiasako/Projects/sunny/img/parts/02_sky_cloud_center.png", "img/top/sky_cloud_center.webp")
b = b.replace("file:///Users/iwawakiasako/Projects/sunny/img/", "img/")
b = re.sub(r'\s*<img class="art p-lib"[^>]*>', "", b)
assert "1115_" not in b and "file:" not in b, re.findall(r'(?:1115_|file:)[^"]*', b)[:5]

# ヘッダー：ほかのページ（新しい型）と同じ5本
b = rep(b, '<nav class="nav"><a href="/schools/">講座をえらぶ</a><a href="/schools/compare/">比較表</a><a href="/school-guides/kyufukin/">費用と給付金</a><a href="/school-experience/">体験記</a><a href="/careers/">はじめての方へ</a><a href="/start/">試験対策</a></nav>',
        '<nav class="nav" aria-label="メニュー"><a href="/careers/">キャリコンとは</a><a href="/schools/">講座をえらぶ</a><a href="/school-guides/kyufukin/">費用と給付金</a><a href="/exam/">試験対策</a><a href="/shikaku-guide/#touroku">受かったあと</a></nav>')
b = rep(b, '<a href="/start/">試験勉強中の方はこちら ›</a>', '<a href="/start/" data-ev="top_study_exam">試験勉強中の方はこちら ›</a>')

# 1画面目：大きい字はいまのまま＋下に小さく1行（11/19 質問3 A）
b = rep(b, '<h1><span class="h1-a">人の話を聴く仕事、<br>わたしも学んでいい</span><span class="h1-b">養成講座、<br>どれにしよう<span class="kari">言葉の案</span></span></h1>',
        '<h1><span class="h1-big">人の話を聴く仕事、<br>わたしも学んでいい</span><span class="h1-sub">キャリアコンサルタント養成講座の選び方・比較</span></h1>')
b = rep(b, '<a class="tl down" href="#cards">いまのあなたに合う学校は？</a>', '<a class="tl down" href="#school-match" data-ev="top_hero_match">いまのあなたに合う学校は？</a>')
b = rep(b, '<img class="art p-sup" src="img/top/hero_picnic.webp" alt="">', '<img class="art p-sup" src="img/top/hero_picnic.webp" alt="" fetchpriority="high">')

# いまのあなたは？：#school-match（ほかのページと llms.txt からの着地点）
b = rep(b, '<div class="who" id="sel">', '<div class="who" id="school-match">')
b = rep(b, '<p class="q">いまのあなたは？<span class="kari">仮</span><small>', '<p class="q">いまのあなたは？<small>')
for k in ["cost", "donichi", "yoru", "support", "mada"]:
    b = rep(b, f'data-k="{k}" aria-pressed="false">', f'data-k="{k}" data-ev="top_match_{k}" aria-pressed="false">')
b = b.replace('<span class="kari">仮</span>', "")
b = b.replace('<div class="bn">', '<div class="cimg">')
for k, n in [("nippon-manpower", "nm"), ("lec", "lec"), ("chiiki-renkei-platform", "chiiki"), ("recurrent", "rec")]:
    b = rep(b, f'<h3><a href="/schools/{k}/">', f'<h3><a href="/schools/{k}/" data-ev="top_card_{n}">')
b = rep(b, '<a class="tl" href="/schools/compare/">全部の比較表を見る</a>', '<a class="tl" href="/schools/compare/" data-ev="top_next_compare">全部の比較表を見る</a>')
b = rep(b, '<a class="tl" href="/school-guides/kyufukin/">給付金の条件を見る</a>', '<a class="tl" href="/school-guides/kyufukin/" data-ev="top_kyufukin_jouken">給付金の条件を見る</a>')

# 本音：体験記は転送のページでなく、体験記へ直接
b = rep(b, '<a class="tl" href="/school-experience/">体験記を読む</a>', '<a class="tl" href="/school-reviews/chiiki-renkei-platform/" data-ev="top_more_review">体験記を読む</a>')
b = rep(b, '<a class="cta" href="/schools/compare/#apply-h">', '<a class="cta" href="/schools/compare/#apply-h" data-ev="top_cta_apply">')
b = rep(b, '<p class="ref note">紹介料をいただいているのは、PRの表示がある学校です。<br>6校とも同じ項目・同じ確かめ方で載せています。</p>',
        '<p class="ref note">紹介料をいただいているのは、PRの表示がある学校です。あなたの受講料は変わりません。<br>6校とも同じ項目・同じ確かめ方で載せています。</p>')

# いまの募集（11/19 トリカブトの確かめ：1119_トップ_募集と特典の確かめ.md）
b = rep(b, '<span class="num" style="font-size:15px;letter-spacing:.1em">11/11</span> に確かめました', '<span class="num" style="font-size:15px;letter-spacing:.1em">11/19</span> に確かめました')
row_nm = '            <tr><th><a href="/schools/nippon-manpower/">日本マンパワー</a><span class="pr">PR</span></th><td data-k="次の開講">第36回養成講座は11/17に案内の予定</td><td data-k="申込みの締切">第35回養成講座（11/17開講）は受付終了</td><td data-k="いちばん早い試験（学校の案内では）" class="ex no">まだ案内が出ていません<small>「第36回」は講座の番号で、試験の回ではありません</small></td></tr>\n'
row_rec = '            <tr><th><a href="/schools/recurrent/">リカレント</a><span class="pr">PR</span></th><td data-k="次の開講">11月・12月生を募集中</td><td data-k="申込みの締切">公式に書いていません</td><td data-k="いちばん早い試験（学校の案内では）" class="ex no">公式に書いていません<small>説明会で確かめてね</small></td></tr>\n'
new_nm = '            <tr><th><a href="/schools/nippon-manpower/">日本マンパワー</a><span class="pr">PR</span></th><td data-k="次の開講">2月19日（金）・3月19日（金）<small>第36回養成講座</small></td><td data-k="申込みの締切">2月19日開講は2月12日（金）まで<small>3月19日開講は3月12日（金）まで</small></td><td data-k="いちばん早い試験（学校の案内では）" class="ex"><b>第36回</b>　2027年10月31日（日）<small>学校の案内「最短で第36回国家資格キャリアコンサルタント試験の受験ができます」</small></td></tr>\n'
b = rep(b, row_rec + row_nm, new_nm + row_rec)
b = rep(b, '<td data-k="申込みの締切">満席まで</td>', '<td data-k="申込みの締切">締切日は公式に書いていません</td>')
b = rep(b, '<small><i>給付金</i>使うなら、ハローワークの手続きは11/16まで（協会の案内）</small>',
        '<small><i>給付金</i>12月1日開講の回は、ハローワークの手続きの期限（11/16）が過ぎています（協会の案内）</small>')
b = rep(b, '<small><i>給付金</i>使うなら、申込みは12/1の2週間前まで。12/1はLECが決める受講開始日で、授業の1日目は12/13（LECの案内）</small>',
        '<small><i>給付金</i>12月生は、申込みの期限（受講開始日12/1の2週間前）が過ぎています。12月生の給付金のことは、実施本校への問い合わせの案内です（LECの案内）</small>')
b = rep(b, '<small><i>開講</i>第35回</small><small><i>締切</i>次の回は、まだ公式に出ていません</small>',
        '<small><i>開講</i>第36回養成講座。2月19日開講は東京・オンライン</small><small><i>締切</i>2月19日開講は2027年2月12日（金）・法人は10日（水）まで。3月19日開講は3月12日（金）まで</small>')
b = rep(b, '<p class="cond">説明会に最後まで参加すると</p><p class="amt"><i>割引</i><b>11,000円引き</b></p><small>対象の回だけ</small>',
        '<p class="cond">説明会・個別相談会に参加すると</p><p class="amt"><i>割引</i><b>11,000円引き</b></p><small>クーポンがもらえます（イベント・ランチタイムセミナーは対象外）</small>')
# 特典の並びも表と同じ順（マンパワーをリカレントの前へ）
li_rec = re.search(r'          <li class="wari"><p class="sc"><a href="/schools/recurrent/">.*?</li>\n', b).group(0)
li_nm = re.search(r'          <li class="wari"><p class="sc"><a href="/schools/nippon-manpower/">.*?</li>\n', b).group(0)
b = rep(b, li_rec + li_nm, li_nm + li_rec)
tr_rec = re.search(r'              <tr><th><a href="/schools/recurrent/">リカレント</a><span class="pr">PR</span></th><td data-k="日程のくわしいこと">.*?</tr>\n', b).group(0)
tr_nm = re.search(r'              <tr><th><a href="/schools/nippon-manpower/">日本マンパワー</a><span class="pr">PR</span></th><td data-k="日程のくわしいこと">.*?</tr>\n', b).group(0)
b = rep(b, tr_rec + tr_nm, tr_nm + tr_rec)

# Q&A のタブ・運営者
for g in range(4):
    b = rep(b, f'role="tab" data-g="{g}"', f'role="tab" data-g="{g}" data-ev="top_qa_tab{g}"')
b = rep(b, '<a class="tl" href="/about/">このサイトについて</a>', '<a class="tl" href="/about/" data-ev="top_author_about">このサイトについて</a>')

# フッター：地図・注意の文・運営者と ©（本番から引きつぐ）
ft_old = re.search(r'      <div class="links"><a href="/privacy/">プライバシーポリシー・免責事項</a><a href="/contact/">お問い合わせ</a></div>\n', b).group(0)
MAP = [
    ("1", "知る", [("/shikaku-guide/gimon/", "キャリコンって何？（よくある質問40問）"), ("/careers/", "キャリアコンサルタントの仕事"), ("/shikaku-guide/", "資格まるわかりガイド（とり方・期間）"), ("/exam-guide/goukakuritsu/", "試験の難易度と合格率"), ("/school-guides/merit-demerit/", "やめたほうがいい人・向いている人")]),
    ("2", "学校選び", [("/schools/compare/", "6校の比較表"), ("/schools/compare/#apply-h", "6校の無料説明会の申込み先"), ("/#school-match", "いまのあなたに合う学校をしぼる"), ("/schools/", "養成学校一覧"), ("/school-guides/kyufukin/", "費用と給付金"), ("/school-guides/how-to-choose/", "養成学校の選び方"), ("/school-guides/online/", "オンライン講座の選び方"), ("/school-guides/working-mothers/", "子育て中の学校選び"), ("/school-guides/training-and-exam-preparation/", "養成講習と試験対策講座の違い"), ("/school-reviews/chiiki-renkei-platform/", "運営者の受講体験記"), ("/schools/chiiki-renkei-platform/#kai", "運営者が出た説明会の話")]),
    ("3", "試験対策", [("/exam/", "試験対策トップ（学科・論述・面接）"), ("/start/", "初学者の学習ルート"), ("/terms/", "キャリコンことば図鑑"), ("/theorists/", "理論家図鑑"), ("/laws/", "労働法・統計・制度"), ("/games/quiz/", "1問1答ドリル"), ("/games/", "3分ミニゲーム"), ("/diagrams/", "図解ライブラリ"), ("/text/", "学科 直前対策テキスト（PDF）"), ("/books/", "さらに学べる本棚"), ("/omamori/", "お守りページ")]),
    ("4", "登録・その先", [("/shikaku-guide/#touroku", "受かったあとの登録"), ("/school-guides/zaitaku-fukugyo/", "在宅・副業で働く")]),
]
site = [("/", "ホーム"), ("/search/", "サイト内検索"), ("/column/", "コラム"), ("/about/", "このサイトについて"), ("/contact/", "お問い合わせ"), ("/privacy/", "プライバシーポリシー・免責事項")]
mp = ['      <nav class="map" aria-label="サイト全体のメニュー">']
for n, t, ls in MAP:
    mp.append(f'        <div><h4><i>{n}</i>{t}</h4><ul>' + "".join(f'<li><a href="{h}">{x}</a></li>' for h, x in ls) + "</ul></div>")
mp[-1] = mp[-1][:-len("</ul></div>")] + "</ul><h4 style=\"margin-top:20px\">このサイトのこと</h4><ul>" + "".join(f'<li><a href="{h}">{x}</a></li>' for h, x in site) + "</ul></div>"
mp.append("      </nav>")
ft_new = ("\n".join(mp) + "\n"
          '      <div class="notes"><p>掲載している学校の料金・日程・給付金などの情報は変更される可能性があります。申込み前に必ず各校の公式サイトで最新情報をご確認ください。</p>'
          '<p>法律・統計・試験制度に関する記述は、一次資料で確認できた範囲で掲載しています。</p></div>\n'
          '      <p class="copy">運営者：岩脇 朝子　&copy; 2026 キャリコン学びピクニック</p>\n')
b = rep(b, ft_old, ft_new)
b = rep(b, '<footer class="ft">', '<footer class="ft" id="sitemap">')
b = rep(b, '<div><h4>紹介料のこと</h4><p>紹介料をいただいているのは、PRの表示がある学校です。',
        '<div><h4>紹介料のこと</h4><p>紹介料をいただいているのは、PRの表示がある学校です。あなたの受講料は変わりません。')
b = rep(b, '（いまの募集は<span class="nb">2026年11月11日</span>、給付金は<span class="nb">11月11日</span>）',
        '（いまの募集は<span class="nb">2026年11月19日</span>、給付金は<span class="nb">11月11日</span>）')

# スマホの下のメニュー（11/19 ちゃん決定 A：学校えらびの側のまん中は「費用」。まん中は data-bn-mid の1か所）
BN = ('<nav class="bn" aria-label="下のメニュー"><a href="/" data-ev="nav_home"><span class="on"><i>⌂</i>ホーム</span></a>'
      '<a href="/schools/compare/" data-ev="nav_compare"><span><i>☰</i>6校くらべ</span></a>'
      '<a href="/school-guides/kyufukin/" data-ev="nav_cost" data-bn-mid><span><i>¥</i>費用</span></a>'
      '<a href="/search/" data-ev="nav_search"><span><i>⌕</i>さがす</span></a>'
      '<a href="#sitemap" data-ev="nav_menu"><span><i>≡</i>メニュー</span></a></nav>\n')
b = rep(b, "</footer>\n", "</footer>\n" + BN)

# 1画面目より下の絵は、あとで読む
hero_end = b.index("<!-- 2") if "<!-- 2" in b else b.index('<section class="sec s-meadow"')
top, rest = b[:hero_end], b[hero_end:]
rest = re.sub(r"<img (?![^>]*loading=)", '<img loading="lazy" decoding="async" ', rest)
b = top + rest

# ---------- script（確かめ用のしかけ・作業メモを外す） ----------
b = b.rstrip() + "\n"
SCRIPT = r"""<script>
(function(){
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!reduce && 'IntersectionObserver' in window) {
    document.documentElement.classList.add('js');
    var io = new IntersectionObserver(function(es){ es.forEach(function(e){ if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }); }, { threshold: 0.35 });
    document.querySelectorAll('.t-row').forEach(function(r){ io.observe(r); });
  }
})();
(function(){
  var tabs = document.querySelectorAll('.qtab'), gs = document.querySelectorAll('.qg');
  function pick(g){
    tabs.forEach(function(t){ t.setAttribute('aria-selected', t.dataset.g === g ? 'true' : 'false'); });
    gs.forEach(function(x){ x.classList.toggle('hide', x.dataset.g !== g); });
  }
  tabs.forEach(function(t){ t.addEventListener('click', function(){ pick(t.dataset.g); }); });
  pick('0');
})();
(function(){
  var hd = document.getElementById('hd'), bt = document.getElementById('menu-btn');
  bt.addEventListener('click', function(){ var o = hd.classList.toggle('open'); bt.setAttribute('aria-expanded', o ? 'true' : 'false'); });
})();
(function(){
  var S = {
    nm:{n:'日本マンパワー',h:'/schools/nippon-manpower/',pr:1,fee:'396,000円'},
    lec:{n:'LEC東京リーガルマインド',h:'/schools/lec/',pr:1,fee:'330,000円'},
    chiiki:{n:'地域連携プラットフォーム',h:'/schools/chiiki-renkei-platform/',pr:1,fee:'297,000円'},
    jaico:{n:'日本産業カウンセラー協会',h:'https://www.jaico.cc/',fee:'330,000円'},
    rec:{n:'リカレント',h:'/schools/recurrent/',pr:1,fee:'499,400円'}
  };
  var M = {
    cost:[['chiiki','総額297,000円'],['lec','総額330,000円'],['jaico','総額330,000円']],
    yoru:[['lec','平日夜のクラスあり'],['chiiki','夜間のコースあり'],['rec','平日夜（18:50〜／20:00〜）']],
    support:[['nm','振替が回数の制限なし・無料'],['lec','振替が回数の制限なし・無料']],
    donichi:'6校とも土日のクラスがあります。',
    mada:'まずは6校を、ひと目で見てみてね。'
  };
  var ps = document.querySelectorAll('.person'), res = document.getElementById('sel-res');
  function show(k){
    var m = M[k], h = '';
    if (typeof m === 'string') {
      h = '<p class="msg">' + m + '</p>';
    } else {
      h = '<p class="msg">当てはまる学校（' + m.length + '校・順位はつけていません）</p><ul>' + m.map(function(r){
        var s = S[r[0]], ext = /^https?:/.test(s.h);
        return '<li><b><a href="' + s.h + '"' + (ext ? ' target="_blank" rel="noopener"' : '') + '>' + s.n + (ext ? '<span class="ext">↗</span>' : '') + '</a>' + (s.pr ? '<span class="pr">PR</span>' : '') + '</b><span class="fee">' + s.fee + '</span><span class="why">当てはまる：' + r[1] + '</span></li>';
      }).join('') + '</ul><p class="after">説明会の予約先は、ページの下の「説明会で雰囲気を見てみよう」から</p>';
    }
    res.innerHTML = h;
  }
  ps.forEach(function(o){
    o.addEventListener('click', function(ev){
      ps.forEach(function(x){ x.setAttribute('aria-pressed', x === o ? 'true' : 'false'); });
      show(o.dataset.k);
      if (ev && ev.isTrusted) {
        var r = res.getBoundingClientRect();
        if (r.bottom > innerHeight || r.top > innerHeight * 0.7) res.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'nearest' });
      }
    });
  });
})();
(function(){
  var box = document.getElementById('cardbox'), bt = document.getElementById('auto-btn');
  var on = !window.matchMedia('(prefers-reduced-motion: reduce)').matches, hold = false, dir = 1, pos = 0, wait = 0, last = 0;
  function label(){ bt.textContent = on ? 'とめる' : 'うごかす'; bt.setAttribute('aria-pressed', on ? 'false' : 'true'); }
  function tick(t){
    var dt = Math.min(50, t - (last || t)); last = t;
    if (on && !hold) {
      if (wait > 0) { wait -= dt; }
      else {
        var max = box.scrollWidth - box.clientWidth;
        if (Math.abs(box.scrollLeft - pos) > 2) pos = box.scrollLeft;
        pos += dir * dt * 0.014;
        if (pos >= max) { pos = max; dir = -1; wait = 1800; }
        if (pos <= 0) { pos = 0; dir = 1; wait = 1800; }
        box.scrollLeft = pos;
      }
    }
    requestAnimationFrame(tick);
  }
  ['pointerenter', 'focusin', 'touchstart', 'pointerdown'].forEach(function(e){ box.addEventListener(e, function(){ hold = true; }, { passive: true }); });
  ['pointerleave', 'focusout', 'touchend'].forEach(function(e){ box.addEventListener(e, function(){ hold = false; pos = box.scrollLeft; }, { passive: true }); });
  bt.addEventListener('click', function(){ on = !on; pos = box.scrollLeft; label(); });
  label(); requestAnimationFrame(tick);
})();
</script>
"""
kg = scripts[1]
kg = re.sub(r"\n\s*//[^\n]*", "", kg)
kg = rep(kg, "  var fix = (location.search.match(/[?&]kg=(\\d)/) || [])[1];\n", "")
kg = rep(kg, "var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches || !('IntersectionObserver' in window) || (/noanim=1/.test(location.search) && !fix);",
         "var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches || !('IntersectionObserver' in window);")
kg = rep(kg, "  if (fix) { step(+fix, true); return; }\n", "")
assert "location.search" not in kg and "fix" not in kg.replace("prefix", "")
b += SCRIPT + kg + "\n" + '<script src="./js/reveal.js?v=2026.1018b" defer></script>\n'
assert "location.search" not in b and "?today" not in b and "noanim" not in b

# ---------- FAQPage（Q&A 12問と同じ言葉） ----------
soup = BeautifulSoup(b, "html.parser")
qs = []
for d in soup.select(".qa details"):
    q = d.summary.get_text("", strip=True)
    q = re.sub(r"^Q", "", q).strip()
    ans = " ".join(p.get_text("", strip=True) for p in d.select(".a > p") if "src" not in (p.get("class") or []))
    qs.append({"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ans}})
assert len(qs) == 12, len(qs)
faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": qs}
ld_faq = '<script type="application/ld+json">' + json.dumps(faq, ensure_ascii=False, separators=(",", ":")) + "</script>"

fonts = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&family=Zen+Kaku+Gothic+New:wght@400;500;700&family=Zen+Kurenaido&display=swap" rel="stylesheet">')
out = ("<!doctype html>\n<html lang=\"ja\">\n<head>\n" + prod_head + "\n" + fonts + "\n" + ld_web + "\n" + ld_org + "\n" + ld_faq + "\n"
       "<style>\n" + css.strip() + "\n</style>\n</head>\n<body>\n" + b.strip("\n") + "\n</body>\n</html>\n")

# 11/20 見出しを短く（ちゃん「長い見出しは短く・意味はわかるように・SEOにも配慮」）。title・説明文はそのまま
out = out.replace("<h2>在宅で修了できる<wbr>キャリアコンサルタント<wbr>養成講座 <wbr>6校を比較</h2>",
                  "<h2>在宅で修了できる<wbr>養成講座 <wbr>6校を比較</h2>")
out = out.replace("<h2>養成講座に申し込む前の、よくある不安</h2>", "<h2>申し込む前の、よくある不安</h2>")
# 字の大きさの決まりは html:root で（修正サイトの ink-tools.css の :root に上書きされないように。値は同じ）
out = out.replace("<style>\n:root{\n  --bg:#fff;", "<style>\nhtml:root{\n  --bg:#fff;", 1)
out = out.replace("  :root{--side:24px;--sec:88px;--fs-hero:25px;", "  html:root{--side:24px;--sec:88px;--fs-hero:25px;", 1)
import sys; sys.path.insert(0, str(Path(__file__).resolve().parent)); import ippen_kotei_1120 as K  # 11/20 出す前の直し
out = K.apply("index.html", out)
for bad in ["仮", "file://", "1115_", "見くらべ", "?today", "?t=", "noauto", "kari"]:
    assert bad not in out, bad
(REPO / "index.html").write_text(out, encoding="utf-8")
print("ok", len(out), "bytes", "faq", len(qs))

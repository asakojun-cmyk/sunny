#!/usr/bin/env python3
"""地域連携プラットフォーム「公式サイトで確かめた情報」を、14行の表から4つの箱にする（2026-11-22）。

ちゃん 11/22「公式サイトで確かめた情報もスクロールしなくてもわかるように。文字ばっかりで内容が入ってこない」
→ イメージ（お金／時間と受け方／休んだとき・修了／修了したあと＋大きな数字）にちゃん「OKです。読みやすい」。
- 言葉と数字は表と同じ（項目名だけ「受け方」「給付金」「修了の条件」などやさしく）。
- #official の <div class="tblw">…</div> を入れかえる。<style id="ofc1122"> を1つ（あれば入れかえ）。何度かけても同じ。
- このあと scripts/ippen_brk_1122.py をかけて、改行の印を入れる。
使い方: python3 scripts/ippen_official_1122.py
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = "schools/chiiki-renkei-platform/index.html"

HTML = """<div class="ofc">
  <p class="ofc-name">講習名：キャリアコンサルタント養成講習（厚生労働大臣認定）</p>
  <div class="ofc-g">
    <p class="ofc-h"><span class="ofc-i">¥</span>お金</p>
    <div class="ofc-big"><b>297,000<small>円（税込）</small></b><span>受講料</span></div>
    <ul class="ofc-l">
      <li><b>入学金・教材費</b>入学金なし・テキスト代込み</li>
      <li><b>給付金</b>専門実践教育訓練給付金の対象講座（給付割合・条件は公式サイトとハローワークで要確認）</li>
      <li><b>割引・特典</b>給付金対象外特典、ペア特典、シニア特典、紹介特典、子育て特典、学生特典などの記載あり（適用条件は要確認）。受講料は、キャンペーン・特典により変わる場合があります</li>
    </ul>
  </div>
  <div class="ofc-g">
    <p class="ofc-h"><span class="ofc-i">◷</span>時間と受け方</p>
    <div class="ofc-tiles">
      <div><b>約3<small>ヶ月</small></b><span>通常コース</span></div>
      <div><b>80<small>時間</small></b><span>Zoom講習</span></div>
      <div><b>70<small>時間</small></b><span>通信課題</span></div>
      <div><b>20<small>名</small></b><span>1コースの定員</span></div>
    </div>
    <ul class="ofc-l">
      <li><b>受け方</b>オンライン（Zoom）。通学5日間＋オンライン5日間のハイブリッドコースも選択可</li>
      <li><b>日程</b>土曜・日曜・祝日コース／平日コース／午前・午後・夜間コース</li>
      <li><b>短いコース</b>最短最速コース約1.5ヶ月／集中コース約0.5ヶ月</li>
    </ul>
    <p class="ofc-n">講習時間は明示書に記載（2026年7月11日に確かめました）</p>
  </div>
  <div class="ofc-g">
    <p class="ofc-h"><span class="ofc-i">↺</span>休んだとき・修了</p>
    <div class="ofc-big"><b>16<small>時間まで無料</small></b><span>Zoom講習80時間のうち、振替できる時間（2026年7月11日に確かめました）</span></div>
    <ul class="ofc-l">
      <li><b>修了の条件</b>習得度確認試験合格／出席時間が規定を満たすこと／通信添削課題すべて提出・合格</li>
    </ul>
  </div>
  <div class="ofc-g">
    <p class="ofc-h"><span class="ofc-i">→</span>修了したあと</p>
    <ul class="ofc-l">
      <li><b>試験対策講座</b>養成講習とは別講座。受講生・卒業生価格で受講可能</li>
      <li><b>卒業後のサポート</b>懇親会・情報交換会・就業支援・独立開業支援・上位資格講座・アシスタント参加の機会（公式サイトの記載）</li>
    </ul>
    <p class="ofc-n">学校へのメールでの質問には「学校としては特別には行っていない。親会社の「キャリア・オアシス」で活動できる」という答えでした（キャリア・オアシスは別料金）</p>
  </div>
</div>"""

CSS = (
    '<style id="ofc1122">'
    "/* 11/22 公式サイトで確かめた情報：4つの箱＋大きな数字（scripts/ippen_official_1122.py） */"
    "body.kata .ofc{display:grid;gap:16px;margin:22px 0 8px}"
    "body.kata .ofc-name{margin:0;font-size:13.5px;line-height:1.7;color:#5A6E8F}"
    "body.kata .ofc-g{background:#fff;border:1.5px solid #E3EAF3;border-radius:20px;padding:20px 20px 16px}"
    "body.kata .ofc-h{display:flex;align-items:center;gap:10px;margin:0 0 14px;font-size:17px;font-weight:700;color:#2E4A78;letter-spacing:.06em}"
    "body.kata .ofc-i{display:inline-grid;place-items:center;width:30px;height:30px;border-radius:50%;background:#FFE08A;color:#2E4A78;font-size:15px}"
    "body.kata .ofc-big{background:#FBF6EC;border-radius:14px;padding:12px 16px;margin:0 0 12px}"
    "body.kata .ofc-big b{display:block;font-size:30px;line-height:1.3;color:#2E4A78;letter-spacing:.02em}"
    "body.kata .ofc-big b small{font-size:14px;margin-left:4px}"
    "body.kata .ofc-big>span{display:block;font-size:13.5px;line-height:1.6;color:#5A6E8F}"
    "body.kata .ofc-tiles{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:0 0 12px}"
    "body.kata .ofc-tiles>div{background:#FBF6EC;border-radius:14px;padding:10px 12px;text-align:center}"
    "body.kata .ofc-tiles b{display:block;font-size:24px;line-height:1.3;color:#2E4A78}"
    "body.kata .ofc-tiles b small{font-size:13px;margin-left:2px}"
    "body.kata .ofc-tiles>div>span{display:block;font-size:12.5px;color:#5A6E8F}"
    "body.kata .ofc-l{list-style:none;margin:0;padding:0}"
    "body.kata .ofc-l li{padding:10px 0;border-top:1px dashed #E8DCC4;font-size:15px;line-height:1.8;color:#2E4A78;text-align:left!important}"
    "body.kata .ofc-l li:first-child{border-top:0;padding-top:2px}"
    "body.kata .ofc-l li>b{display:block;font-size:13px;color:#5A6E8F;letter-spacing:.06em;margin-bottom:2px}"
    "body.kata .ofc-n{margin:8px 0 0;font-size:13px;line-height:1.7;color:#6B7C99}"
    # 11/22 ちゃん「PCはPCで一番みやすく」→ PCは1グループ1段：左に見出しと大きな数字、右にくわしい中身
    "@media (min-width:761px){"
    "body.kata .ofc{gap:14px}"
    "body.kata .ofc-g{display:grid;grid-template-columns:216px 1fr;grid-template-rows:auto 1fr auto;column-gap:32px;padding:26px 30px}"
    "body.kata .ofc-g>.ofc-h{grid-column:1;grid-row:1;align-self:start;margin-bottom:14px}"
    "body.kata .ofc-g>.ofc-big,body.kata .ofc-g>.ofc-tiles{grid-column:1;grid-row:2;align-self:start;margin:0}"
    "body.kata .ofc-g>.ofc-l{grid-column:2;grid-row:1/span 2;align-self:start;padding-left:0!important;margin:0!important}"
    "body.kata .ofc-g>.ofc-n{grid-column:2;grid-row:3;margin-top:10px}"
    "body.kata .ofc-l li{font-size:15.5px}body.kata .ofc-l li:first-child{padding-top:4px}"
    "body.kata .ofc-big b{font-size:28px}"
    "body.kata .ofc-tiles>div>span{font-size:11.5px;letter-spacing:0;white-space:nowrap}"
    "}"
    "</style>"
)


def main():
    p = os.path.join(ROOT, PAGE)
    s = open(p, encoding="utf-8").read()
    new = s
    if 'class="ofc"' not in new:
        m = re.search(r'(<section class="sec2 hb" id="official">.*?)(<div class="tblw">.*?</table></div>)', new, re.S)
        if not m:
            raise SystemExit("#official の表が見つからない")
        new = new[:m.start(2)] + HTML + new[m.end(2):]
    if 'id="ofc1122"' in new:
        new = re.sub(r'<style id="ofc1122">.*?</style>', lambda _: CSS, new, count=1, flags=re.S)
    else:
        new = new.replace("</head>", CSS + "\n</head>", 1)
    if new != s:
        open(p, "w", encoding="utf-8").write(new)
    print(PAGE, "（変わりなし）" if new == s else "入れた")


if __name__ == "__main__":
    main()

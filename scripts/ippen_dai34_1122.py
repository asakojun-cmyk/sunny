#!/usr/bin/env python3
"""第33回（2026年11月1日）が終わったので、試験の側の古い案内を第34回に合わせる（2026-11-22）。

ちゃん 11/22「古い情報ってまだ残ってる？」→「次に進んでください」。
第34回の日程は 11/22 に確かめた：学科・論述 2027年3月7日(日)（厚生労働省の試験日程・JAICOの案内。サイトの /exam/ と同じ）。
- 試験対策などの下の帯（plan-banner）：「第33回(11月1日)を受ける方へ 試験まで30日の逆算プラン」→
  「第34回(3月7日)を受ける方へ 試験日までの流れと勉強の道」で /exam/#nagare へ（30日プランは11/1向けの中身のため）。
- お守りのカウントダウン：初めの試験日とボタンを第34回(2027年3月7日)に（omamori/index.html・js/omamori.js）。
- 30日の逆算プランのページ：中身（ちゃんの受験の言葉）は変えず、いちばん上に「第33回向けに書いたプラン」と第34回への案内を1行。
- 何度かけても同じ。
使い方: python3 scripts/ippen_dai34_1122.py
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANNER_PAGES = ["start/index.html", "theorists/oboekata/index.html", "exam-guide/shiryo/index.html",
                "exam-guide/shutsudai-hani/index.html", "exam-guide/gakka-benkyoho/index.html",
                "exam-guide/rodo-hikkake/index.html", "exam-guide/ronjutsu-kata/index.html",
                "exam-guide/saimoku-drill/index.html", "games/quiz/index.html"]


def rw(rel, fn):
    p = os.path.join(ROOT, rel)
    s = open(p, encoding="utf-8").read()
    new = fn(s, rel)
    if new != s:
        open(p, "w", encoding="utf-8").write(new)
    print(rel, "（変わりなし）" if new == s else "直した")


def banner(s, rel):
    pre = "../" * rel.count("/")
    new = (f'<p class="plan-banner"><a href="{pre}exam/#nagare"><b>第34回(3月7日)を<wbr>受ける方へ</b><wbr>'
           f'試験日までの<wbr>流れと<wbr>勉強の道 <span class="arw" aria-hidden="true">▶︎</span></a></p>')
    return re.sub(r'<p class="plan-banner"><a href="[^"]*last-30days/"><b>第33回.*?</p>', lambda _: new, s, flags=re.S)


def omamori_html(s, rel):
    s = s.replace('<input type="date" id="exam-date" value="2026-11-01">', '<input type="date" id="exam-date" value="2027-03-07">')
    s = s.replace('data-date-preset="2026-11-01">第33回(2026年11月1日)に<wbr>する</button>',
                  'data-date-preset="2027-03-07">第34回(2027年3月7日)に<wbr>する</button>')
    # 動きのファイルを直したので、スマホに残った古い版を使わないよう印を変える
    return s.replace('../js/omamori.js?v=2026.1018c', '../js/omamori.js?v=2026.1122')


def omamori_js(s, rel):
    s = s.replace('/* 第33回 学科・論述試験の日(サイト内の試験日案内と同じ) */',
                  '/* 第34回 学科・論述試験の日(サイト内の試験日案内と同じ。11/22 に第33回から変えた) */')
    return s.replace('var DEFAULT_DATE = "2026-11-01";', 'var DEFAULT_DATE = "2027-03-07";')


def plan_note(s, rel):
    if 'class="plan-old-note"' in s:
        return s
    note = ('<p class="plan-old-note" style="margin:14px 0 0;padding:12px 16px;border-radius:14px;background:#FBF6EC;'
            'font-size:14px;line-height:1.8">このプランは、<wbr>第33回<wbr>(2026年11月1日)に<wbr>向けて<wbr>書いたものです。<wbr>'
            '第34回の<wbr>学科・論述は<wbr>2027年3月7日<wbr>(日)。<wbr>'
            '<a href="../../exam/#nagare">第34回の<wbr>日程と<wbr>勉強の道を<wbr>見る <span class="arw" aria-hidden="true">▶︎</span></a></p>')
    return s.replace('<p class="updated-date"><span>更新日: 2026年10月18日</span></p>',
                     '<p class="updated-date"><span>更新日: 2026年10月18日</span></p>\n    ' + note, 1)


for r in BANNER_PAGES:
    rw(r, banner)
rw("omamori/index.html", omamori_html)
rw("js/omamori.js", omamori_js)
rw("exam-guide/last-30days/index.html", plan_note)

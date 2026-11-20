#!/usr/bin/env python3
"""11/20 出したあとの直し（美雨ちゃんの△・残っていた古い言葉）。何回かけても同じ。

- 試験の側の「書いた人」：「2026年11月の試験に挑戦中」→「第33回試験を受けた（合格発表は12/16）」（about と同じ）
- 学校ページの出典の行：作業メモの言葉「本番のページの文」→「学校の公式ページの文」
- トップ：「損しない？」「お得だね！」→「損」でなく「安心」で言う決まりに
使い方：python3 scripts/ippen_kotei_1120b.py
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ALL = [  # どのページにも当てる
    ("2026年11月の<wbr>試験に<wbr>挑戦中の<wbr>初学者と<wbr>して、",
     "2026年11月の<wbr>第33回試験を<wbr>受けた<wbr>初学者と<wbr>して、"),
    ("2026年11月の国家試験に挑戦中です。", "2026年11月の第33回国家試験を受けました（合格発表は2026年12月16日）。"),
    ("2026年11月の<wbr>国家試験に<wbr>挑戦中です。", "2026年11月の<wbr>第33回国家試験を<wbr>受けました<wbr>（合格発表は<wbr>2026年12月16日）。"),
    ('<p class="src">本番のページの文（','<p class="src">学校の公式ページの文（'),
]
TOP = [
    ('"name":"損しない？"', '"name":"締切で困らない？"'),
    ('<span class="qm">Q</span>損しない？</summary>', '<span class="qm">Q</span>締切で困らない？</summary>'),
    ("こんなに下がるんだね！<br>お得だね！", "こんなに下がるんだね！<br>助かるね！"),
]


def main():
    changed, left = 0, []
    for d, ds, fs in os.walk(ROOT):
        ds[:] = [x for x in ds if x not in (".git", "scripts", "node_modules") and not x.startswith("_")]
        for f in fs:
            if not f.endswith(".html"):
                continue
            p = os.path.join(d, f)
            s = open(p, encoding="utf-8").read()
            t = s
            for a, b in ALL + (TOP if os.path.relpath(p, ROOT) == "index.html" else []):
                t = t.replace(a, b)
            if t != s:
                open(p, "w", encoding="utf-8").write(t)
                changed += 1
            plain = t.replace("<wbr>", "")
            if "挑戦中" in plain or "本番のページの文" in plain:
                left.append(os.path.relpath(p, ROOT))
    print("書きかえたページ", changed)
    print("まだ残っている", len(left), left[:10])


if __name__ == "__main__":
    main()

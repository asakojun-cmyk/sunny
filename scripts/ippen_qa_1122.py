#!/usr/bin/env python3
"""地域連携プラットフォーム「メールと説明会で聞いた質問と答え」を縦並びにする（2026-11-22）。

ちゃん 11/22「地域連携プラットフォームのメールと説明会で聞いた答えはクエッションが窮屈すぎる。訂正して。
読みにくい。スクロールしなくてもいいようにして」
→ 2列の表（質問の列がせまく、答えは横スクロール）をやめ、どの幅でも「Q の下に A」を置く。言葉は変えない。
- <style id="qa1122"> を1つ足す（あれば入れかえる）。何度かけても同じ。
使い方: python3 scripts/ippen_qa_1122.py
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = "schools/chiiki-renkei-platform/index.html"
Q = "#mailqa table.tbl"
CSS = (
    '<style id="qa1122">'
    "/* 11/22 メールと説明会の質問と答え：Q の下に A（scripts/ippen_qa_1122.py） */"
    "#mailqa .tblw{overflow:visible!important;margin-left:0!important;margin-right:0!important}"
    f"{Q}{{display:block!important;width:auto!important;min-width:0!important;table-layout:auto!important}}"
    f"{Q} tbody{{display:block!important}}"
    f"{Q} tr{{display:block!important;padding:20px 26px!important;border-bottom:1px solid var(--line,#dfe6ef)}}"
    f"{Q} tr:last-child{{border-bottom:0}}"
    f"{Q} th,{Q} td{{display:block!important;width:auto!important;min-width:0!important;max-width:none!important;"
    "padding:0!important;border:0!important;background:none!important;white-space:normal!important;text-align:left!important}"
    f"{Q} th{{font-size:16.5px!important;line-height:1.7!important;margin-bottom:8px}}"
    f"{Q} td{{font-size:16px!important;line-height:1.85!important;font-weight:400}}"
    f"{Q} td::before{{content:\"A \";font-weight:700;color:#E07A5F}}"
    "@media (max-width:760px){"
    f"{Q} tr{{padding:18px 20px!important}}{Q} th{{font-size:16px!important}}{Q} td{{font-size:15.5px!important}}"
    "}"
    "</style>"
)


def main():
    p = os.path.join(ROOT, PAGE)
    s = open(p, encoding="utf-8").read()
    if 'id="mailqa"' not in s:
        print("mailqa の段なし")
        return
    if 'id="qa1122"' in s:
        new = re.sub(r'<style id="qa1122">.*?</style>', lambda _: CSS, s, count=1, flags=re.S)
    else:
        new = s.replace("</head>", CSS + "\n</head>", 1)
    if new != s:
        open(p, "w", encoding="utf-8").write(new)
    print(PAGE, "（変わりなし）" if new == s else "入れた")


if __name__ == "__main__":
    main()

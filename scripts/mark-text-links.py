#!/usr/bin/env python3
"""文の中にあるリンクに class="txt-link" をつける(色と太字で、リンクだとわかるようにするため)。

「文の中にある」= <main> の中で、リンクのすぐ外側の要素(p・li・dd・td など)に、リンク以外の文字が4文字以上あるもの。
ボタンやカードのように、それだけで1つの部品になっているリンクにはつけない。
ページを足したり本文にリンクを足したりしたら、サイトの一番上のフォルダでもう一度実行する:
  python3 scripts/mark-text-links.py
見た目は css/tone.css の .txt-link。
"""
import glob
import re
from html.parser import HTMLParser

PARENTS = {"p", "li", "dd", "td", "span", "small", "figcaption", "b", "strong", "em"}
VOID = {"wbr", "br", "img", "input", "meta", "link", "hr", "source", "area", "base", "col", "embed", "track"}
SKIP_CLASS = re.compile(r"button|btn|newsflash|camp-banner|card|chip|tab|nav|logo|share|skip")


class Finder(HTMLParser):
    def __init__(self, src):
        super().__init__(convert_charrefs=True)
        self.src = src
        self.lines = [0]
        for line in src.split("\n"):
            self.lines.append(self.lines[-1] + len(line) + 1)
        self.stack = []      # [tag, 自分の文字数, [(aタグの位置, 元のタグ文字列)]]
        self.in_main = 0
        self.edits = []

    def pos(self):
        line, col = self.getpos()
        return self.lines[line - 1] + col

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        if tag == "main":
            self.in_main += 1
        if tag == "a" and self.in_main and self.stack and self.stack[-1][0] in PARENTS:
            cls = dict(attrs).get("class") or ""
            if dict(attrs).get("href") and "txt-link" not in cls and not SKIP_CLASS.search(cls):
                self.stack[-1][2].append((self.pos(), self.get_starttag_text()))
        self.stack.append([tag, 0, []])

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        while self.stack:
            t, n, links = self.stack.pop()
            if n >= 4:
                self.edits += links
            if t == tag:
                break
        if tag == "main":
            self.in_main -= 1

    def handle_data(self, data):
        if self.stack:
            self.stack[-1][1] += len(re.sub(r"[\s▶︎►→・｜|/／:：()（）「」、。]", "", data))


total = 0
for path in sorted(glob.glob("**/*.html", recursive=True)):
    if path.startswith("_to_delete"):
        continue
    src = open(path, encoding="utf-8").read()
    f = Finder(src)
    f.feed(src)
    if not f.edits:
        continue
    for pos, tag in sorted(set(f.edits), reverse=True):
        assert src[pos:pos + len(tag)] == tag, (path, tag)
        if re.search(r'\bclass="', tag):
            new = re.sub(r'\bclass="([^"]*)"', lambda m: f'class="{m.group(1)} txt-link"', tag, count=1)
        else:
            new = tag.replace("<a ", '<a class="txt-link" ', 1)
        src = src[:pos] + new + src[pos + len(tag):]
    open(path, "w", encoding="utf-8").write(src)
    total += len(set(f.edits))
    print(f"{len(set(f.edits)):4d} {path}")
print("合計", total)

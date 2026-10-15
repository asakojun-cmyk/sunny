#!/usr/bin/env python3
"""CSSをページごとに1本にまとめて、軽くする(表示速度の改善 2026-10-16)。

しくみ
- 各HTMLの <link rel="stylesheet" href="…css/○○.css?v=…"> を、上から順に集める。
- あいだに <style> がない連続したまとまりごとに、1本の css/_b-<ハッシュ>.css にまとめる
  (順番はそのまま。だから見た目は変わらない)。
- まとめたリンクには data-src="元のファイル一覧" を残す。次に実行したときは、ここから作り直す。
- 元の css/○○.css は、これまでどおり手で直してよい。直したら、このスクリプトを実行する
  (GitHub Actions でも push のたびに自動で実行される)。

使い方: python3 scripts/build-css.py
"""
import glob
import hashlib
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

COMMON = ['style.css', 'picnic.css', 'refine.css', 'yomiyasu.css']
LINK = re.compile(r'<link rel="stylesheet" href="((?:\./|\.\./)*)css/([^"?]+\.css)(\?[^"]*)?"(?: data-src="([^"]*)")?>')


def minify(css: str) -> str:
    out, i, n = [], 0, len(css)
    buf = []
    while i < n:
        c = css[i]
        if c == '/' and css.startswith('/*', i):
            j = css.find('*/', i + 2)
            i = n if j < 0 else j + 2
            buf.append(' ')
            continue
        if c in '"\'':
            j = i + 1
            while j < n and css[j] != c:
                j += 2 if css[j] == '\\' else 1
            out.append(_squash(''.join(buf)))
            buf = []
            out.append(css[i:j + 1])
            i = j + 1
            continue
        buf.append(c)
        i += 1
    out.append(_squash(''.join(buf)))
    return ''.join(out).strip()


def _squash(s: str) -> str:
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'\s*([{};,])\s*', r'\1', s)
    s = s.replace(';}', '}')
    return s


def expand(link_match):
    """リンク1本 → 元ファイルの一覧 [(name, query)]"""
    prefix, name, query, data_src = link_match.groups()
    if data_src:
        return [tuple(x.split('?', 1)) if '?' in x else (x, '') for x in data_src.split(',')]
    return [(name, (query or '').lstrip('?'))]


def build_bundle(files):
    parts = []
    for name, _q in files:
        path = os.path.join('css', name)
        with open(path, encoding='utf-8') as fh:
            parts.append(minify(fh.read()))
    body = '\n'.join(p for p in parts if p)
    h = hashlib.sha1(body.encode()).hexdigest()[:10]
    out = f'css/_b-{h}.css'
    if not os.path.exists(out):
        with open(out, 'w', encoding='utf-8') as fh:
            fh.write(body + '\n')
    return out


def process(html_path, used):
    with open(html_path, encoding='utf-8') as fh:
        s = fh.read()
    links = list(LINK.finditer(s))
    if not links:
        return False
    # まとまり(あいだに <style> がない連続)に分ける
    groups, cur = [], []
    for m in links:
        if cur and re.search(r'<style\b', s[cur[-1].end():m.start()]):
            groups.append(cur)
            cur = []
        cur.append(m)
    if cur:
        groups.append(cur)
    edits = []  # (start, end, replacement)
    for g in groups:
        files = []
        for m in g:
            for f in expand(m):
                if f[0].startswith('_b-'):
                    continue
                files.append(f)
        if not files:
            continue
        prefix = g[0].group(1)
        names = [n for n, _ in files]
        # どのページにも共通の土台は、別の1本にする(ページを移っても使い回せる)
        chunks = [files[:len(COMMON)], files[len(COMMON):]] if names[:len(COMMON)] == COMMON else [files]
        tags = []
        for ch in chunks:
            if not ch:
                continue
            bundle = build_bundle(ch)
            used.add(bundle)
            src = ','.join(f'{n}?{q}' if q else n for n, q in ch)
            tags.append(f'<link rel="stylesheet" href="{prefix}{bundle}" data-src="{src}">')
        tag = '\n'.join(tags)
        edits.append((g[0].start(), g[0].end(), tag))
        for m in g[1:]:
            st, en = m.start(), m.end()
            if s[en:en + 1] == '\n':
                en += 1
            edits.append((st, en, ''))
    new = s
    for st, en, rep in sorted(edits, reverse=True):
        new = new[:st] + rep + new[en:]
    if new != s:
        with open(html_path, 'w', encoding='utf-8') as fh:
            fh.write(new)
        return True
    return False


def main():
    used, changed = set(), 0
    for f in sorted(glob.glob('**/*.html', recursive=True)):
        if f.startswith(('node_modules/', '_to_delete/')):
            continue
        if process(f, used):
            changed += 1
    removed = 0
    for old in glob.glob('css/_b-*.css'):
        if old not in used:
            os.remove(old)
            removed += 1
    print(f'pages changed: {changed}, bundles: {len(used)}, removed old: {removed}')


if __name__ == '__main__':
    sys.exit(main())

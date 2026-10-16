#!/usr/bin/env python3
"""過去問の出題回数バッジを、ことば図鑑・理論家図鑑のページと一覧に入れる(何度実行しても同じ結果)。
データ: data/kakomon.json (第27〜32回の学科試験の問題文・選択肢に出てきた回)
"""
import json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
D = json.load(open('data/kakomon.json', encoding='utf-8'))
N = len(D['rounds'])
BADGE_RE = re.compile(r' ?<a class="kako-badge"[^>]*>.*?</a>| ?<span class="kako-chip"[^>]*>.*?</span>', re.S)

def label(rs):
    return f'第{rs[0]}〜{rs[-1]}回' if rs else ''

def page(kind, slug, rounds):
    f = f'{kind}/{slug}/index.html'
    if not os.path.exists(f):
        return
    s = open(f, encoding='utf-8').read()
    s = BADGE_RE.sub('', s)
    if rounds:
        rs = '・'.join(f'第{r}回' for r in rounds)
        b = (f' <a class="kako-badge" href="../../kakomon-keiko/" title="学科試験の問題文・選択肢に出てきた回: {rs}">'
             f'過去{N}回で<b>{len(rounds)}</b>回出題</a>')
        s, n = re.subn(r'(<p class="term-header__number">.*?)(</p>)', lambda m: m.group(1) + b + m.group(2), s, count=1, flags=re.S)
    open(f, 'w', encoding='utf-8').write(s)

def lists():
    for f, kind in (('terms/index.html', 'terms'), ('hinshutsu/index.html', 'terms'), ('theorists/index.html', 'theorists')):
        s = open(f, encoding='utf-8').read()
        s = BADGE_RE.sub('', s)
        def rep(m):
            slug = m.group(2)
            rounds = D[kind].get(slug) or []
            chip = f' <span class="kako-chip" title="過去{N}回の学科試験で出てきた回数">過去{N}回で{len(rounds)}回</span>' if rounds else ''
            return m.group(1) + chip + m.group(3)
        s = re.sub(r'(<a href="\.\./' + kind + r'/([^/"]+)/">\s*(?:<span class="theorist-list__avatar".*?</span>\s*)?<span class="(?:term|theorist)-list__number">.*?)(</span>\s*<span class="(?:term|theorist)-list__name">)', rep, s, flags=re.S)
        open(f, 'w', encoding='utf-8').write(s)

for kind in ('terms', 'theorists'):
    for slug, rounds in D[kind].items():
        page(kind, slug, rounds)
lists()
print('ok')

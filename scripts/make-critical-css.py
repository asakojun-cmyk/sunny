#!/usr/bin/env python3
"""トップページの「最初の画面に必要なデザイン(クリティカルCSS)」を作り直す(表示速度の改善7 2026-10-16)。

しくみ
- いろいろな画面幅でトップを開き、最初の画面(+150px)に見えている部分に効くCSSだけを集める。
- index.html の <style id="crit-a">(1本目・2本目のCSSの分)と <style id="crit-b">(3本目の分)を書き換える。
- CSSファイル全体は media="print" onload で後から読むので、デザインを直したあとにこれを実行しておく
  (実行しなくても、ファイル全体が届いた時点で正しい見た目になる。最初の一瞬だけ古いデザインが出る)。

使い方: リポジトリ直下で python3 -m http.server 8765 を動かしてから
        python3 scripts/make-critical-css.py
必要なもの: Playwright(Chromium)
"""
from playwright.sync_api import sync_playwright
import json, sys
from playwright.sync_api import sync_playwright
URL=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8765/'
MARK=r"""(h)=>{const top=e=>{let x=e;while(x&&x!==document.documentElement){const r=x.getBoundingClientRect();if(r.width||r.height)return r.top;x=x.parentElement}return 0};for(const e of document.querySelectorAll('*')){if(top(e)<h+150)e.setAttribute('data-crit','1')}}"""
COLLECT=r"""()=>{
const DYN=/::?(before|after|placeholder|marker|selection|first-letter|first-line|backdrop|-webkit-[a-z-]+|-moz-[a-z-]+)|:(hover|focus|focus-visible|focus-within|active|visited|target|checked|disabled|invalid|valid|placeholder-shown)\b/g;
const els=[...document.querySelectorAll('[data-crit]')];
function split(sel){const out=[];let d=0,cur='';for(const c of sel){if(c==='('||c==='[')d++;else if(c===')'||c===']')d--;if(c===','&&d===0){out.push(cur);cur=''}else cur+=c}out.push(cur);return out}
function clean(p){p=p.replace(DYN,'').replace(/:is\(\s*\)|:where\(\s*\)|:not\(\s*\)/g,'').trim();if(!p||/[>+~]$/.test(p))p+='*';return p}
function used(sel){for(let p of split(sel)){p=clean(p);if(/^(html|body|:root|\*)$/.test(p))return true;try{for(const e of els)if(e.matches(p))return true}catch(x){}}return false}
const res={};
function walk(rules,path){for(let i=0;i<rules.length;i++){const r=rules[i],pp=path.concat(i);
 if(r instanceof CSSStyleRule){if(used(r.selectorText))res.cur.push(pp.join('.'))}
 else if(r instanceof CSSMediaRule||r instanceof CSSSupportsRule){walk(r.cssRules,pp)}
 else res.cur.push(pp.join('.'))}}
const out={};for(const sh of document.styleSheets){if(!sh.href||!sh.href.includes('/css/cb-'))continue;res.cur=[];walk(sh.cssRules,[]);out[sh.href.split('/').pop()]=res.cur}return out}"""
BUILD=r"""(keep)=>{const out={};
function walk(rules,path){let s='';for(let i=0;i<rules.length;i++){const r=rules[i],k=path.concat(i).join('.');
 if(r instanceof CSSMediaRule||r instanceof CSSSupportsRule){const inner=walk(r.cssRules,path.concat(i));if(inner)s+=(r instanceof CSSMediaRule?'@media ':'@supports ')+r.conditionText+'{'+inner+'}'}
 else if(keep.has(k))s+=r.cssText}return s}
for(const sh of document.styleSheets){if(!sh.href||!sh.href.includes('/css/cb-'))continue;const n=sh.href.split('/').pop();const kk=new Set(window.__keep[n]||[]);keep=kk;out[n]=walk(sh.cssRules,[])}return out}"""
keep={}
with sync_playwright() as p:
    b=p.chromium.launch()
    for w,h in [(320,640),(360,740),(390,844),(430,932),(768,1024),(1024,768),(1280,900),(1536,960),(1920,1080)]:
        pg=b.new_page(viewport={'width':w,'height':h})
        pg.route('**/*', lambda r: r.abort() if any(x in r.request.url for x in ['googletagmanager','clarity.ms','a8.net']) else r.continue_())
        pg.goto(URL,wait_until='load'); pg.wait_for_timeout(300)
        pg.evaluate(MARK,h)
        for k,v in pg.evaluate(COLLECT).items(): keep.setdefault(k,set()).update(v)
        pg.close()
    pg=b.new_page(viewport={'width':390,'height':844})
    pg.goto(URL,wait_until='load')
    pg.evaluate("k=>{window.__keep=k}",{k:sorted(v) for k,v in keep.items()})
    built=pg.evaluate(BUILD.replace("(keep)=>{","()=>{let keep;"))
    b.close()
import os, re, importlib.util


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location('bc', os.path.join(ROOT, 'scripts', 'build-css.py'))
bc = importlib.util.module_from_spec(spec); spec.loader.exec_module(bc)
html = os.path.join(ROOT, 'index.html')
src = open(html, encoding='utf-8').read()
links = re.findall(r'<link rel="stylesheet" href="\./css/(cb-[0-9a-f]+\.css)"', src)
a = bc.minify(''.join(built.get(n, '') for n in links[:2]))
b = bc.minify(''.join(built.get(n, '') for n in links[2:]))
src = re.sub(r'<style id="crit-a">.*?</style>', lambda m: '<style id="crit-a">' + a + '</style>', src, flags=re.S)
src = re.sub(r'<style id="crit-b">.*?</style>', lambda m: '<style id="crit-b">' + b + '</style>', src, flags=re.S)
open(html, 'w', encoding='utf-8').write(src)
print('crit-a', len(a), 'crit-b', len(b))

/* むずかしい言葉に、ルビ(読みがな)と「タップでヒント」をつける。
   言葉と読みと「ひとことでいうと」は search-index.json(ことば図鑑・理論家図鑑)から読む。
   - 同じ言葉は、ページの中で最初の1回だけ
   - 見出し・リンク・ボタン・1問1答の中にはつけない
   - 模試・ドリル・ゲームのページでは動かさない(ヒントが答えになるため)
   ページで止めたいときは <main data-no-hint> 、一部だけ止めたいときはその要素に data-no-hint */
(function () {
  "use strict";
  var path = location.pathname;
  if (/\/(exam-guide\/(moshi|bunya|ronjutsu-moshi|last-30days)|games|kakomon-keiko|text|search|notrack)\//.test(path)) return;
  var main = document.querySelector("main");
  if (!main || main.hasAttribute("data-no-hint")) return;
  var me = document.currentScript && document.currentScript.src;
  var base = me ? new URL("../", me) : new URL("/", location.href);

  var SKIP = "a,button,h1,h2,h3,h4,h5,h6,script,style,ruby,rt,label,input,textarea,select,svg,nav,code,pre," +
    ".quiz-box,.quiz-saimoku,.term-header,.theorist-header,.bottom-nav,.kh,.kh-card,[data-no-hint],[aria-hidden='true']";
  var KANJI = /[一-鿿々]/;
  var KANA = /^[゠-ヿー・]+$/;
  var MAX = 40;

  function css() {
    var s = document.createElement("style");
    s.textContent =
      ".kh{cursor:pointer;text-decoration:underline dotted;text-decoration-color:currentColor;text-underline-offset:.28em;text-decoration-thickness:1.5px;border-radius:4px}" +
      ".kh:focus-visible{outline:2px solid var(--color-terracotta,#a0583d);outline-offset:2px}" +
      ".kh ruby rt{font-size:.5em;letter-spacing:0;color:var(--color-text-subtle,#6f6b63);font-weight:400}" +
      ".kh-card{position:absolute;z-index:9000;max-width:min(320px,calc(100vw - 32px));background:var(--color-surface,#fffdf8);" +
      "border:1.5px solid var(--color-border,#d8d2c7);border-radius:16px;box-shadow:0 10px 30px rgba(39,39,34,.14);padding:14px 16px 12px;" +
      "font-size:14px;line-height:1.7;color:var(--color-text,#272722)}" +
      ".kh-card__w{font-weight:700;font-size:15px;margin:0}.kh-card__y{font-size:12px;color:var(--color-text-subtle,#6f6b63);margin:0 0 6px}" +
      ".kh-card__k{display:inline-block;font-size:11px;font-weight:700;color:var(--color-green,#758679);margin:0 0 2px}" +
      ".kh-card__d{margin:0 0 8px}.kh-card__a{font-weight:700;color:var(--color-terracotta,#a0583d);text-decoration:none;font-size:13px}" +
      ".kh-card__x{position:absolute;top:6px;right:8px;border:0;background:none;font-size:18px;line-height:1;color:var(--color-text-subtle,#6f6b63);cursor:pointer;padding:6px}";
    document.head.appendChild(s);
  }

  function prep(list) {
    var here = path.replace(/index\.html$/, "");
    var out = [];
    list.forEach(function (x) {
      if (x.type !== "用語" && x.type !== "理論家") return;
      if (!x.title || !x.description || !x.url) return;
      if (here.replace(/\/$/, "") === x.url.replace(/\/$/, "")) return;
      var rd = (x.type === "用語" && x.reading) ? String(x.reading).split(/[\s(（]/)[0] : "";
      var words = [x.title];
      var short = x.title.split(/[(（]/)[0];
      if (short && short !== x.title) words.push(short);
      words.forEach(function (w) {
        if (w.length < 2) return;
        if (KANA.test(w) && w.length < 3) return;
        out.push({ w: w, rd: KANJI.test(w) && !/[(（]/.test(w) && /^[\u3040-\u309fー]+$/.test(rd) ? rd : "",
          key: x.url, t: x.title, d: x.description, u: x.url, ty: x.type });
      });
    });
    out.sort(function (a, b) { return b.w.length - a.w.length; });
    return out;
  }

  function esc(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }

  function walk(terms) {
    var re = new RegExp(terms.map(function (t) { return esc(t.w); }).join("|"), "g");
    var byW = {}; terms.forEach(function (t) { if (!byW[t.w]) byW[t.w] = t; });
    var used = {}, n = 0;
    var tw = document.createTreeWalker(main, NodeFilter.SHOW_TEXT, {
      acceptNode: function (node) {
        if (!node.nodeValue || node.nodeValue.trim().length < 2) return NodeFilter.FILTER_REJECT;
        var p = node.parentElement;
        if (!p || p.closest(SKIP)) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    var nodes = []; while (tw.nextNode()) nodes.push(tw.currentNode);
    for (var i = 0; i < nodes.length && n < MAX; i++) {
      var node = nodes[i], text = node.nodeValue, m, hit = null;
      re.lastIndex = 0;
      while ((m = re.exec(text))) {
        var t = byW[m[0]];
        if (!t || used[t.key]) continue;
        var before = text.charAt(m.index - 1), after = text.charAt(m.index + m[0].length);
        if (KANA.test(m[0]) && (/[゠-ヿ]/.test(before) || /[゠-ヿ]/.test(after))) continue;
        hit = { t: t, i: m.index, len: m[0].length, w: m[0] }; break;
      }
      if (!hit) continue;
      used[hit.t.key] = 1; n++;
      var mid = node.splitText(hit.i); mid.splitText(hit.len);
      var span = document.createElement("span");
      span.className = "kh"; span.tabIndex = 0; span.setAttribute("role", "button");
      span.setAttribute("aria-label", hit.w + "のヒントを見る");
      span.dataset.k = hit.t.key;
      if (hit.t.rd && hit.w === hit.t.w) {
        var r = document.createElement("ruby"); r.textContent = hit.w;
        var rt = document.createElement("rt"); rt.textContent = hit.t.rd; r.appendChild(rt); span.appendChild(r);
      } else span.textContent = hit.w;
      mid.parentNode.replaceChild(span, mid);
      span._t = hit.t;
      if (span.nextSibling && span.nextSibling.nodeType === 3) nodes.splice(i + 1, 0, span.nextSibling);
    }
  }

  var card = null;
  function close() { if (card) { card.remove(); card = null; } }
  function open(el) {
    close();
    var t = el._t; if (!t) return;
    card = document.createElement("div"); card.className = "kh-card"; card.setAttribute("role", "dialog");
    var href = new URL(t.u.replace(/^\//, ""), base).href;
    card.innerHTML = '<button class="kh-card__x" type="button" aria-label="閉じる">×</button>' +
      '<p class="kh-card__k">' + (t.ty === "理論家" ? "理論家" : "ことば") + '</p>' +
      '<p class="kh-card__w"></p><p class="kh-card__y"></p><p class="kh-card__d"></p>' +
      '<a class="kh-card__a">' + (t.ty === "理論家" ? "理論家図鑑" : "ことば図鑑") + 'でくわしく見る ▶︎</a>';
    card.querySelector(".kh-card__w").textContent = t.t;
    var y = card.querySelector(".kh-card__y"); if (t.rd) y.textContent = t.rd; else y.remove();
    card.querySelector(".kh-card__d").textContent = "ひとことでいうと：" + t.d;
    var a = card.querySelector(".kh-card__a"); a.href = href;
    a.addEventListener("click", function () { try { if (window.gtag) gtag("event", "term_hint_go", { term: t.t }); } catch (e) {} });
    card.querySelector(".kh-card__x").addEventListener("click", close);
    document.body.appendChild(card);
    var r = el.getBoundingClientRect(), cw = card.offsetWidth, vw = document.documentElement.clientWidth;
    var left = Math.min(Math.max(16, r.left + window.scrollX + r.width / 2 - cw / 2), window.scrollX + vw - cw - 16);
    card.style.left = left + "px"; card.style.top = (r.bottom + window.scrollY + 8) + "px";
    try { if (window.gtag) gtag("event", "term_hint_open", { term: t.t }); } catch (e) {}
  }
  document.addEventListener("click", function (e) {
    var k = e.target.closest && e.target.closest(".kh");
    if (k) { e.preventDefault(); open(k); return; }
    if (card && !card.contains(e.target)) close();
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") close();
    if ((e.key === "Enter" || e.key === " ") && e.target.classList && e.target.classList.contains("kh")) { e.preventDefault(); open(e.target); }
  });
  window.addEventListener("resize", close);

  function start() {
    fetch(new URL("search-index.json", base).href, { credentials: "same-origin" })
      .then(function (r) { return r.ok ? r.json() : []; })
      .then(function (list) { var t = prep(list); if (!t.length) return; css(); walk(t); })
      .catch(function () {});
  }
  if ("requestIdleCallback" in window) requestIdleCallback(start, { timeout: 2500 }); else setTimeout(start, 600);
})();

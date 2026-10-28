/* トップの「卒業生の声」(2026-10-28)
   - 声は Googleフォーム → スプレッドシート。シートを「ウェブに公開」したCSVを読む(設定は js/koe-config.js)
     (公開CSVは Google 側が Access-Control-Allow-Origin を返すので、ブラウザから直接読める。2026-10-28 実測)
   - 出すのは「掲載」の列が ○ の行だけ。掲載への同意の列が空の行も出さない
   - 投稿の文字は、すべて textContent で入れる(HTMLとしては読まない)
   - 学校 → ボタンのリンクは data/koe-schools.json(投稿の文字からリンクは作らない)
   - 読めない・0件のときは、フォームの入口だけ(フォームのURLもなければ、何も出さない)
   - 声が1件以上あるときだけ、トップの「声を見る」リンク([data-koe-link])を出す
   - 「卒業生の方へ」の入口は共通部品。置き場所 <div data-koe-invite="ページ名" hidden></div> に、ここで中身を作る
     (トップ・試験対策トップ・今日の問題で同じもの。フォームのURLが空なら出さない。PR・紹介リンクは置かない)
   - 手元の確かめ用: localhost のときだけ ?koe-csv=… ?koe-form=… で読み先を差しかえられる */
(function () {
  var root = document.querySelector("[data-koe]");
  var slots = document.querySelectorAll("[data-koe-invite]");
  if (!root && !slots.length) return;

  var cfg = window.KOE_CONFIG || {};
  var csvUrl = cfg.sheetCsvUrl || "";
  var formUrl = cfg.formUrl || "";
  if (/^(localhost|127\.0\.0\.1)$/.test(location.hostname)) {
    var q = new URLSearchParams(location.search);
    if (q.get("koe-csv")) csvUrl = q.get("koe-csv");
    if (q.get("koe-form")) formUrl = q.get("koe-form");
  }

  var FIRST = 3; /* はじめに見せる件数 */
  /* フォームの質問の名前(先頭が合えばよい)。上から順に、1つの列は1つの役だけ */
  var COLS = [
    ["reason", "えらんだ理由"],
    ["good", "良かったこと"],
    ["hard", "大変だったこと"],
    ["now", "いまどうしているか"],
    ["nickname", "ニックネーム"],
    ["when", "受講した時期"],
    ["how", "受け方"],
    ["school", "学校"],
    ["ok", "掲載"],
    ["consent", "サイト掲載に同意"],
    ["time", "タイムスタンプ"]
  ];
  var BODY = [["reason", "えらんだ理由"], ["good", "良かったこと"], ["hard", "大変だったこと"], ["now", "いまどうしているか"]];

  var $ = function (s) { return root.querySelector(s); };
  var el = function (tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  };
  /* 文のかたまりを、変なところで折れないように並べる(<wbr> のルールと同じ考え) */
  var phrases = function (p, list) {
    list.forEach(function (t, i) {
      if (i) p.appendChild(document.createElement("wbr"));
      p.appendChild(el("span", "nb", t));
    });
    return p;
  };
  var norm = function (s) { return String(s || "").replace(/[\s　()（）・]/g, "").toLowerCase(); };
  var hasForm = /^https:\/\//.test(formUrl);

  /* 「卒業生の方へ」の入口(共通部品) */
  function fillInvites() {
    if (!hasForm) return false;
    [].forEach.call(slots, function (slot) {
      if (slot.firstChild) return;
      var box = el("aside", "koe-invite");
      box.setAttribute("aria-label", "卒業生の方へ");
      phrases(box.appendChild(el("p", "koe-invite__t")), ["卒業生の方へ：", "あなたの声を", "聞かせてください"]);
      phrases(box.appendChild(el("p", "koe-invite__d")), ["養成講座を受けて", "よかったこと、", "大変だったことを、", "これから選ぶ人に", "届けませんか。", "ニックネームで", "送れます。"]);
      var go = box.appendChild(el("p", "koe-invite__go"));
      var a = go.appendChild(el("a", "picnic-button picnic-button--line", "声を送る(Googleフォーム) "));
      a.href = formUrl;
      a.target = "_blank";
      a.rel = "noopener";
      a.setAttribute("data-ev", "koe_form_" + (slot.getAttribute("data-koe-invite") || "page"));
      a.appendChild(el("span", "arw", "▶︎")).setAttribute("aria-hidden", "true");
      slot.appendChild(box);
      slot.hidden = false;
    });
    return true;
  }

  if (!root) { fillInvites(); return; }
  if (!window.fetch) return;

  function showInviteOnly() {
    if (fillInvites()) root.hidden = false; /* フォームのURLもなければ、何も出さない */
  }

  /* CSV(RFC 4180: "…" の中のカンマ・改行・"" を正しく読む) */
  function parseCsv(t) {
    t = t.replace(/^﻿/, "");
    var rows = [], row = [], f = "", i = 0, n = t.length, inq = false, c;
    while (i < n) {
      c = t[i];
      if (inq) {
        if (c === '"') { if (t[i + 1] === '"') { f += '"'; i++; } else inq = false; }
        else f += c;
      } else if (c === '"') inq = true;
      else if (c === ",") { row.push(f); f = ""; }
      else if (c === "\n" || c === "\r") {
        if (c === "\r" && t[i + 1] === "\n") i++;
        row.push(f); rows.push(row); row = []; f = "";
      } else f += c;
      i++;
    }
    if (f !== "" || row.length) { row.push(f); rows.push(row); }
    return rows;
  }

  function toVoices(rows, schools) {
    if (!rows.length) return [];
    var head = rows[0].map(function (h) { return String(h).trim(); });
    var idx = {}, used = {};
    COLS.forEach(function (k) {
      for (var j = 0; j < head.length; j++) {
        if (!used[j] && head[j].indexOf(k[1]) === 0) { idx[k[0]] = j; used[j] = 1; return; }
      }
    });
    if (idx.ok == null) return []; /* 「掲載」の列がなければ、1件も出さない */
    var find = {};
    schools.forEach(function (s) {
      find[norm(s.name)] = s;
      (s.aliases || []).forEach(function (a) { find[norm(a)] = s; });
    });
    var get = function (r, k) { return idx[k] == null ? "" : String(r[idx[k]] || "").trim(); };
    var out = [];
    rows.slice(1).forEach(function (r, n) {
      if (!/^[○〇◯]$/.test(get(r, "ok"))) return;
      if (idx.consent != null && !get(r, "consent")) return;
      var v = { n: n };
      COLS.forEach(function (k) { v[k[0]] = get(r, k[0]); });
      if (!v.good && !v.hard && !v.now && !v.reason) return;
      v.s = find[norm(v.school)] || null;
      out.push(v);
    });
    return out.reverse(); /* 新しい投稿から */
  }

  function card(v) {
    var li = el("li", "koe-card");
    var who = el("p", "koe-card__who");
    who.appendChild(el("b", "", v.nickname || "卒業生"));
    li.appendChild(who);
    var meta = el("ul", "koe-card__meta");
    [v.s ? v.s.name : v.school, v.when, v.how].forEach(function (m) { if (m) meta.appendChild(el("li", "", m)); });
    if (meta.children.length) li.appendChild(meta);
    var dl = el("dl", "koe-card__body");
    BODY.forEach(function (b) {
      if (!v[b[0]]) return;
      var d = el("div");
      d.appendChild(el("dt", "", b[1]));
      d.appendChild(el("dd", "", v[b[0]]));
      dl.appendChild(d);
    });
    li.appendChild(dl);
    return li;
  }

  function render(voices, schools) {
    var sel = $("[data-koe-select]"), list = $("[data-koe-list]"), more = $("[data-koe-more]"),
        count = $("[data-koe-count]"), go = $("[data-koe-go]");
    var bySlug = {};
    schools.forEach(function (s) { bySlug[s.slug] = s; });

    var opt0 = el("option", "", "すべての学校(" + voices.length + "件)");
    opt0.value = "";
    sel.appendChild(opt0);
    schools.forEach(function (s) {
      var k = voices.filter(function (v) { return v.s === s; }).length;
      var o = el("option", "", s.name + "(" + k + "件)");
      o.value = s.slug;
      sel.appendChild(o);
    });

    function draw(open) {
      var s = bySlug[sel.value] || null;
      var show = voices.filter(function (v) { return !s || v.s === s; });
      list.textContent = "";
      show.forEach(function (v, i) {
        var c = card(v);
        if (!open && i >= FIRST) c.hidden = true;
        list.appendChild(c);
      });
      count.textContent = show.length ? "" : "この学校の声は、まだありません。";
      count.hidden = !!show.length;
      var rest = show.length - FIRST;
      more.hidden = open || rest <= 0;
      if (rest > 0) more.querySelector("button").textContent = "ほかの声も見る(あと" + rest + "件)";

      go.textContent = "";
      if (!s) {
        var a0 = el("a", "picnic-button picnic-button--line koe-go__btn", "7校を比較表でくらべてみよう ");
        a0.href = "./schools/compare/";
        a0.setAttribute("data-ev", "top_koe_compare");
        a0.appendChild(el("span", "arw", "▶︎")).setAttribute("aria-hidden", "true");
        go.appendChild(a0);
        return;
      }
      var a = el("a", "picnic-button koe-go__btn");
      a.href = s.href;
      a.setAttribute("data-ev", "top_koe_go_" + s.slug);
      if (s.pr) {
        a.target = "_blank";
        a.rel = "sponsored nofollow noopener noreferrer";
        a.appendChild(el("span", "pr-label", "PR"));
      }
      a.appendChild(document.createTextNode(s.label));
      go.appendChild(a);
      if (s.page) {
        var p = el("p", "koe-go__sub"), b = el("a", "txt-link", "このサイトの学校ページを見る");        b.href = s.page;
        b.setAttribute("data-ev", "top_koe_page_" + s.slug);
        p.appendChild(b);
        go.appendChild(p);
      }
      if (s.pr) {
        var n = el("p", "koe-go__pr");
        n.appendChild(el("span", "nb", "「PR」のボタンは広告(紹介リンク)です。"));
        n.appendChild(document.createElement("wbr"));
        n.appendChild(el("span", "nb", "あなたの受講料は変わりません。"));
        go.appendChild(n);
      }
    }

    sel.addEventListener("change", function () { draw(false); });
    more.querySelector("button").addEventListener("click", function () { draw(true); });
    draw(false);
    $("[data-koe-body]").hidden = false;
    root.hidden = false;
    fillInvites();
    [].forEach.call(document.querySelectorAll("[data-koe-link]"), function (l) { l.hidden = false; });
  }

  if (!csvUrl) { showInviteOnly(); return; }

  var ctrl = window.AbortController ? new AbortController() : null;
  var timer = setTimeout(function () { if (ctrl) ctrl.abort(); }, 10000);
  var opt = ctrl ? { signal: ctrl.signal } : {};
  Promise.all([
    fetch("./data/koe-schools.json", opt).then(function (r) { if (!r.ok) throw 0; return r.json(); }),
    fetch(csvUrl, opt).then(function (r) { if (!r.ok) throw 0; return r.text(); })
  ]).then(function (res) {
    clearTimeout(timer);
    var schools = res[0].schools || [];
    var voices = toVoices(parseCsv(res[1]), schools);
    if (!voices.length) { showInviteOnly(); return; }
    render(voices, schools);
  }).catch(function () {
    clearTimeout(timer);
    showInviteOnly();
  });
})();

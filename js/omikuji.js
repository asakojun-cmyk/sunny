/* ぴったりな理論家おみくじ v2（案C・2026-11-22 ナデシコ）
   データは js/omikuji-data.js（picnic-docs/作り直し用スクリプト/omikuji_v2.py で書き出す）。
   答え・結果はこの画面の中だけで使い、どこにも保存・送信しない（localStorage・cookie も使わない）。
   確認用：?pick=slug&luck=大吉&scene=draw|paper&anim=0&open=1 */
(function () {
  "use strict";
  var D = window.OMIKUJI;
  if (!D) return;
  var IMG = "../../img/nigaoe/";
  var KW_SHOW = 2; /* 紙に最初から見せる言葉の数（残りは開く） */
  /* 系統：本番 /theorists/keifu/ の6つのタブ。添えた言葉は読む人向けの言いかえ（11/22 リンドウ確認） */
  var KEI = [
    ["特性因子理論", "k-trait", "人と仕事の相性"],
    ["発達論", "k-dev", "人生の段階と転機"],
    ["認知行動論", "k-cog", "考え方・行動・学び方"],
    ["自己成長論", "k-self", "自分らしく生きる"],
    ["精神力動論", "k-psy", "こころの奥のはたらき"],
    ["組織心理論", "k-org", "職場・やる気・働き方"]
  ];
  /* 紙の左の列に入らない長い名前だけ、折る所を決める（11/22 66人の確かめで見つけた2人） */
  var NAME_BR = { "deshazer-berg": "ド・シャザーと<wbr>バーグ", "bronfenbrenner": "ブロンフェン<wbr>ブレナー" };
  var KC = {};
  KEI.forEach(function (k) { KC[k[0]] = k; });
  var Q = new URLSearchParams(location.search);
  var anim = Q.get("anim") !== "0" && !matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (id) { return document.getElementById(id); };
  var esc = function (s) { return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); };
  var noTag = function (s) { return String(s || "").replace(/<[^>]+>/g, ""); };
  var pick = function (a) { return a[Math.floor(Math.random() * a.length)]; };
  var bySlug = function (s) { return D.kami.filter(function (k) { return k.slug === s; })[0]; };
  var faces = function (k) {
    return k.imgs.map(function (s) { return '<img src="' + IMG + s + '.webp" alt="" loading="lazy" decoding="async">'; }).join("");
  };
  var scenes = { start: $("omk-start"), draw: $("omk-draw"), paper: $("omk-paper") };
  var cur = null, timer = null;

  function show(name, focusEl) {
    Object.keys(scenes).forEach(function (n) { scenes[n].hidden = n !== name; });
    var top = document.querySelector(".omk .kc");
    window.scrollTo({ top: name === "start" ? 0 : Math.max(0, top.getBoundingClientRect().top + window.pageYOffset), behavior: "instant" });
    if (focusEl) focusEl.focus({ preventScroll: true });
  }

  /* ---------- 一覧（帯と、たたんだ一覧） ---------- */
  function card(k, hit) {
    var kc = KC[k.kei];
    var a = document.createElement("a");
    a.className = "omk-card " + kc[1] + (hit ? " hit" : "");
    a.href = k.path; /* 本番の理論家ページ /theorists/<slug>/ */
    a.innerHTML = '<span class="ph' + (k.imgs.length > 1 ? " two" : "") + '">' + faces(k) +
      '<span class="omk-chip">' + kc[0] + "</span>" +
      (k.not_yet ? '<span class="stand">絵は<br>準備中</span>' : "") + "</span>" +
      '<span class="nm">' + esc(k.name) + '</span><span class="ln">' + esc(noTag(k.line)) + "</span>";
    a.setAttribute("aria-label", k.name + "（" + kc[0] + "）のページへ" + (hit ? "・いま出た先生" : ""));
    return a;
  }
  function legends() {
    document.querySelectorAll(".omk-legend").forEach(function (ul) {
      ul.innerHTML = "";
      KEI.forEach(function (k) {
        var n = D.kami.filter(function (r) { return r.kei === k[0]; }).length;
        var li = document.createElement("li");
        li.className = k[1];
        li.innerHTML = "<b>" + k[0] + "（" + n + "人）</b>" + k[2];
        ul.appendChild(li);
      });
    });
  }
  function strip() {
    var s = $("omk-strip");
    D.kami.forEach(function (k) { s.appendChild(card(k, false)); });
  }
  function grid(hitSlug) {
    var g = $("omk-grid");
    g.innerHTML = "";
    var hit = bySlug(hitSlug);
    [hit].concat(D.kami.filter(function (k) { return k.slug !== hitSlug; })).forEach(function (k) { g.appendChild(card(k, k.slug === hitSlug)); });
    var f = $("omk-fold");
    if (Q.get("open") !== "1") f.classList.add("closed");
    $("omk-open-all").hidden = !f.classList.contains("closed");
  }
  $("omk-open-all").addEventListener("click", function () {
    $("omk-fold").classList.remove("closed");
    this.hidden = true;
  });

  /* ---------- ② 引く ---------- */
  function draw(k, luck) {
    cur = { k: k || pick(D.kami), luck: luck || pick(D.unsei) };
    var f = $("omk-stick-face");
    f.className = "omk-stick__face" + (cur.k.imgs.length > 1 ? " two" : "");
    f.innerHTML = faces(cur.k);
    $("omk-num-b").innerHTML = "<i>第</i>" + cur.k.no + "<i>番</i><span class=\"nm\">" + esc(cur.k.name) + "</span>";
    var sc = scenes.draw;
    sc.classList.remove("omk-draw-anim", "omk-draw-done");
    show("draw");
    clearTimeout(timer);
    if (anim) {
      void sc.offsetWidth;
      sc.classList.add("omk-draw-anim");
      timer = setTimeout(function () { sc.classList.add("omk-draw-done"); $("omk-num").focus({ preventScroll: true }); }, 3100);
    } else {
      sc.classList.add("omk-draw-done");
      $("omk-num").focus({ preventScroll: true });
    }
  }

  /* ---------- ③ 紙 ---------- */
  function paper() {
    var k = cur.k, kc = KC[k.kei];
    var tanka = (k.tanka || []).map(function (p, i) { return '<span class="' + (i >= 3 ? "s" : "") + '">' + esc(p) + "</span>"; }).join("");
    var kwRow = function (w) {
      return '<div class="omk-it"><span class="lb">' + esc(w[0]) + "</span><p>" + w[1] + (w[2] ? '<span class="ap">→ ' + w[2] + "</span>" : "") + "</p></div>";
    };
    var shown = k.kws.slice(0, KW_SHOW), rest = k.kws.slice(KW_SHOW);
    var more = "";
    if (rest.length) more += "<dt>ほかのキーワード</dt><dd>" + rest.map(function (w) { return "<b>" + esc(w[0]) + "</b>　" + w[1] + (w[2] ? "（" + w[2] + "）" : ""); }).join("<br>") + "</dd>";
    if (k.what) more += "<dt>何を説明する理論か</dt><dd>" + k.what + "</dd>";
    if (k.core) more += "<dt>核の考え</dt><dd>" + k.core + "</dd>";
    if (k.machigai) more += "<dt>" + esc(D.machigai_title) + "</dt><dd>" + k.machigai + "</dd>";
    var label = rest.length ? "ほかのキーワード（あと" + rest.length + "つ）・くわしく" : "くわしく";
    /* いまのあなたへ（v5 の imano：こんなときに・この理論の見方・今日の一歩）。11/6 の版にはないので出さない */
    var im = k.imano, toyou = "";
    if (im && (im.konna_toki || im.mikata || im.ippo)) {
      toyou = '<section class="omk-toyou"><h3>' + esc(D.imano_title) + "</h3><dl>" +
        (im.konna_toki ? "<dt>こんなときに</dt><dd>" + im.konna_toki + "</dd>" : "") +
        (im.mikata ? "<dt>この理論の見方</dt><dd>" + im.mikata + "</dd>" : "") +
        (im.ippo ? "<dt>今日の一歩</dt><dd>" + im.ippo + "</dd>" : "") + "</dl></section>";
    }
    var el = $("omk-paper-el");
    el.setAttribute("data-result", k.slug);
    el.innerHTML =
      '<span class="omk-luck">' + esc(cur.luck) + "</span>" +
      '<p class="omk-pno"><b>' + esc(k.label) + "</b>理論家おみくじ</p>" +
      '<div class="omk-duo">' +
        '<p class="omk-uta" aria-label="' + esc(noTag(k.tanka_yomi)) + '">' + tanka + "</p>" +
        '<div class="omk-who">' +
          '<span class="omk-who__box ' + kc[1] + (k.imgs.length > 1 ? " two" : "") + '">' + faces(k).replace(/ alt=""/g, ' alt="' + esc(k.name) + 'の似顔絵"') + "</span>" +
          (k.not_yet ? '<span class="omk-chip">（似顔絵は準備中）</span>' : "") +
          '<span class="omk-chip ' + kc[1] + '">' + kc[0] + "</span>" +
          '<h2 class="nm' + (noTag(k.name).length > 7 ? " xlong" : noTag(k.name).length > 5 ? " long" : "") + '">' + (NAME_BR[k.slug] || esc(k.name)) + "</h2>" +
          (k.en ? '<p class="en">' + esc(k.en) + "</p>" : "") +
          '<p class="th">' + k.line + "</p>" +
        "</div>" +
      "</div>" +
      '<div class="omk-hito"><span class="k">ひとことで言うと</span><p><span>' + k.hitokoto + "</span></p></div>" +
      (shown.length ? '<div class="omk-items">' + shown.map(kwRow).join("") + "</div>" : "") +
      (more ? '<details class="omk-more"' + (Q.get("open") === "1" ? " open" : "") + "><summary>" + label + "</summary><dl>" + more + "</dl></details>" : "") +
      toyou +
      '<a class="omk-btn" href="' + k.path + '">' + esc(k.name) + "のページを読む</a>";
    grid(k.slug);
    var sc = scenes.paper;
    sc.classList.remove("omk-paper-anim");
    show("paper", el);
    if (anim) { void sc.offsetWidth; sc.classList.add("omk-paper-anim"); }
  }

  /* ---------- つなぐ ---------- */
  $("omk-go").addEventListener("click", function () { draw(); });
  $("omk-tube").addEventListener("click", function () { draw(); });
  $("omk-open").addEventListener("click", paper);
  $("omk-again").addEventListener("click", function () { show("start", $("omk-go")); });
  window.__omikuji = { draw: draw, paper: paper, data: D }; /* 手元の確認用 */

  /* 紙の外の一言（v5 の closing）。なければ画面の文のまま */
  if (D.closing) document.querySelector(".omk-after .sub").textContent = noTag(D.closing);
  legends();
  strip();
  var sc0 = Q.get("scene");
  if (sc0 === "draw" || sc0 === "paper") {
    draw(bySlug(Q.get("pick")), Q.get("luck"));
    if (sc0 === "paper") paper();
  }
})();

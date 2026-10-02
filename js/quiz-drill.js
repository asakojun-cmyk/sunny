/* ○×クイズドリル: 全用語の1問1答を連続出題(プルダウンで範囲・時間を選択+シャッフル)。h=1 は本番形式(4つの文から選ぶ) */
(function () {
  "use strict";
  var dataEl = document.getElementById("quiz-data");
  var root = document.querySelector("[data-quiz-drill]");
  if (!dataEl || !root) return;

  var ALL;
  try {
    ALL = JSON.parse(dataEl.textContent || "[]");
  } catch (_e) {
    return;
  }

  var filter = "all";
  var timeSel = "5";
  var COUNTS = { "1": 3, "5": 10, "10": 20, "30": 50, all: null };
  var pool = ALL.slice();
  var order = [];
  var idx = 0;
  var score = 0;

  var startBox = document.querySelector("[data-quiz-start]");
  var card = root.querySelector("[data-quiz-card]");
  var endBox = root.querySelector("[data-quiz-end]");
  var poolEl = document.querySelector("[data-quiz-pool]");
  var genreSel = document.querySelector("[data-quiz-genre]");
  var timeSelEl = document.querySelector("[data-quiz-timesel]");

  // これまでの記録(0=まだ / 1=まちがえた / 2=正解した)を読む
  function readLog() {
    try { return window.localStorage.getItem("carepicnic-quiz-log-v1") || ""; } catch (_e) { return ""; }
  }
  // 模擬試験: 本番の学科50問に近い配分で、分野ごとに問題を選ぶ
  var MOCK_PLAN = { 1: 3, 2: 8, 3: 6, 4: 3, 5: 6, 6: 3, 7: 3, 8: 5, 9: 9, 10: 4 };
  function buildMock() {
    var out = [];
    Object.keys(MOCK_PLAN).forEach(function (d) {
      var inDom = shuffle(ALL.filter(function (x) { return x.d === Number(d); }));
      out = out.concat(inDom.slice(0, MOCK_PLAN[d]));
    });
    return out;
  }

  function applyFilter() {
    if (filter === "all") pool = ALL.slice();
    else if (filter === "wrong" || filter === "unseen") {
      var log = readLog();
      pool = ALL.filter(function (x, k) {
        var c = log.charAt(k);
        return filter === "wrong" ? c === "1" : (c !== "1" && c !== "2");
      });
    } else if (filter === "mock") {
      pool = buildMock();
    } else if (filter === "shiryo") {
      pool = ALL.filter(function (x) { return x.s === 1; });
    }
    else if (filter === "freq3") {
      pool = ALL.filter(function (x) { return x.f === 3; });
    } else if (filter === "theorist") {
      pool = ALL.filter(function (x) { return x.t === 1; });
    } else if (filter === "theory") {
      pool = ALL.filter(function (x) { return x.c === "キャリア理論" || x.c === "カウンセリング理論"; });
    } else if (filter.indexOf("dom:") === 0) {
      var dom = Number(filter.slice(4));
      pool = ALL.filter(function (x) { return x.d === dom; });
    } else if (filter === "honban") {
      pool = ALL.filter(function (x) { return x.h === 1; });
    } else if (filter === "choice") {
      pool = ALL.filter(function (x) { return !!(x.o && x.o.length); });
    } else {
      var cat = filter.slice(4);
      pool = ALL.filter(function (x) { return x.c === cat; });
    }
    if (poolEl) poolEl.textContent = String(pool.length);
    var cEl = document.querySelector("[data-quiz-count]");
    if (cEl) {
      var c = filter === "mock" ? null : COUNTS[timeSel];
      cEl.textContent = String(c === null ? pool.length : Math.min(c, pool.length));
    }
  }

  function shuffle(arr) {
    var a = arr.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }

  function show(el) { el.hidden = false; }
  function hide(el) { el.hidden = true; }

  function backToStart() {
    hide(card); hide(endBox); hide(root); show(startBox);
  }

  var oxBox = root.querySelector("[data-quiz-ox]");
  var choiceBox = root.querySelector("[data-quiz-choices]");

  function isChoice(item) { return !!(item && item.o && item.o.length); }

  // 理解度の記録: 1問ごとに「まだ=0 / まちがえた=1 / 正解した=2」を、この端末のブラウザにだけ保存する
  var LOG_KEY = "carepicnic-quiz-log-v1";
  var DOM_KEY = "carepicnic-quiz-domains-v1";
  function recordResult(item, correct) {
    try {
      var i = ALL.indexOf(item);
      if (i < 0) return;
      var log = window.localStorage.getItem(LOG_KEY) || "";
      while (log.length < ALL.length) log += "0";
      log = log.slice(0, i) + (correct ? "2" : "1") + log.slice(i + 1);
      window.localStorage.setItem(LOG_KEY, log);
      var doms = {};
      ALL.forEach(function (x, k) {
        var d = x.d || 0;
        if (!doms[d]) doms[d] = { total: 0, ok: 0, ng: 0 };
        doms[d].total++;
        if (log.charAt(k) === "2") doms[d].ok++;
        else if (log.charAt(k) === "1") doms[d].ng++;
      });
      window.localStorage.setItem(DOM_KEY, JSON.stringify(doms));
    } catch (_e) { /* 保存できない環境でも、ドリルはそのまま動かす */ }
  }

  function judge(item, correct, btn) {
    recordResult(item, correct);
    if (correct) score++;
    var label = isChoice(item) ? "「" + item.o[item.ai] + "」" : "「" + (item.a ? "○" : "×") + "」";
    btn.classList.add(correct ? "is-correct" : "is-wrong");
    if (!correct && isChoice(item)) {
      var right = choiceBox.querySelectorAll("button")[item.ai];
      if (right) right.classList.add("is-correct");
    }
    var v = root.querySelector("[data-quiz-verdict]");
    v.textContent = correct ? "🌞 正解！" : "🌥️ おしい！正解は" + label;
    v.className = "quiz-drill__verdict " + (correct ? "is-ok" : "is-ng");
    root.querySelector("[data-quiz-exp]").textContent = item.e;
    var link = root.querySelector("[data-quiz-link]");
    link.setAttribute("href", item.u);
    link.textContent = "「" + item.n + "」のページで復習する ▶︎";
    root.querySelector("[data-quiz-score]").textContent = String(score);
    show(root.querySelector("[data-quiz-result]"));
  }

  function renderQuestion() {
    var item = order[idx];
    root.querySelector("[data-quiz-no]").textContent = String(idx + 1);
    root.querySelector("[data-quiz-total]").textContent = String(order.length);
    root.querySelector("[data-quiz-score]").textContent = String(score);
    root.querySelector("[data-quiz-cat]").textContent = item.c + " / " + item.n;
    root.querySelector("[data-quiz-q]").textContent = item.q;
    hide(root.querySelector("[data-quiz-result]"));
    root.querySelectorAll("[data-quiz-ans]").forEach(function (b) { b.disabled = false; b.classList.remove("is-correct", "is-wrong"); });
    if (isChoice(item)) {
      hide(oxBox); show(choiceBox);
      choiceBox.textContent = "";
      item.o.forEach(function (text, i) {
        var b = document.createElement("button");
        b.type = "button";
        b.className = "button button--ghost quiz-drill__choice";
        b.textContent = String(i + 1) + ". " + text;
        b.addEventListener("click", function () {
          choiceBox.querySelectorAll("button").forEach(function (x) { x.disabled = true; });
          judge(item, i === item.ai, b);
        });
        choiceBox.appendChild(b);
      });
    } else {
      show(oxBox); hide(choiceBox);
      choiceBox.textContent = "";
    }
  }

  function begin() {
    if (filter === "mock" || filter === "wrong" || filter === "unseen") applyFilter();
    if (pool.length === 0) {
      var zero = document.querySelector("[data-quiz-zero]");
      if (zero) { zero.hidden = false; zero.textContent = filter === "wrong" ? "まちがえたままの問題は、いまはありません。" : "この範囲に、出せる問題がありません。"; }
      return;
    }
    var zeroEl = document.querySelector("[data-quiz-zero]");
    if (zeroEl) zeroEl.hidden = true;
    var c = filter === "mock" ? null : COUNTS[timeSel];
    order = shuffle(pool);
    if (c !== null) order = order.slice(0, Math.min(c, order.length));
    idx = 0;
    score = 0;
    hide(startBox); hide(endBox); show(root); show(card);
    renderQuestion();
  }

  function finish() {
    hide(card); show(endBox);
    var rate = Math.round((score / order.length) * 100);
    root.querySelector("[data-quiz-final]").textContent = order.length + "問中 " + score + "問正解(" + rate + "%)";
    var note = rate === 100 ? "完璧！サニー先生もびっくりの仕上がりだよ☀️"
      : rate >= 80 ? "合格ライン越え！この調子で他の範囲もいってみよう😊"
      : rate >= 50 ? "いい感じ！まちがえた問題の用語ページを読み直すと、ぐんと伸びるよ"
      : "だいじょうぶ、まちがいは伸びしろ。用語ページでゆっくり復習してからまた来てね🌥️";
    if (filter === "mock") {
      note = rate >= 70
        ? "模擬試験の合格ライン(70%)を越えたよ☀️ 本番は公式の過去問でも確かめてね。"
        : "模擬試験の合格ライン(70%)まで、あと少し。まちがえた問題は「まちがえた問題だけ」でもう一度解けるよ。";
    }
    root.querySelector("[data-quiz-endnote]").textContent = note;
    var shareText = "キャリコン1問1答ドリル、" + order.length + "問中" + score + "問正解(" + rate + "%)\u2600\ufe0f #キャリコン学びピクニック";
    var pageUrl = "https://carepicnic.com/games/quiz/";
    var xBtn = document.querySelector("[data-quiz-share-x]");
    var lineBtn = document.querySelector("[data-quiz-share-line]");
    if (xBtn) xBtn.setAttribute("href", "https://twitter.com/intent/tweet?text=" + encodeURIComponent(shareText) + "&url=" + encodeURIComponent(pageUrl));
    if (lineBtn) lineBtn.setAttribute("href", "https://line.me/R/share?text=" + encodeURIComponent(shareText + " " + pageUrl));
  }

  root.querySelectorAll("[data-quiz-ans]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var item = order[idx];
      root.querySelectorAll("[data-quiz-ans]").forEach(function (b) { b.disabled = true; });
      judge(item, (btn.getAttribute("data-quiz-ans") === "true") === item.a, btn);
    });
  });

  root.querySelector("[data-quiz-next]").addEventListener("click", function () {
    idx++;
    if (idx >= order.length) finish();
    else renderQuestion();
  });
  document.querySelector("[data-quiz-begin]").addEventListener("click", begin);
  var randBtn = document.querySelector("[data-quiz-random]");
  if (randBtn) {
    randBtn.addEventListener("click", function () {
      order = shuffle(ALL.slice()).slice(0, Math.min(10, ALL.length));
      idx = 0; score = 0;
      hide(startBox); hide(endBox); show(root); show(card);
      renderQuestion();
    });
  }
  if (timeSelEl) {
    timeSelEl.addEventListener("change", function () {
      timeSel = timeSelEl.value;
      applyFilter();
      backToStart();
    });
  }
  if (genreSel) {
    genreSel.addEventListener("change", function () {
      filter = genreSel.value;
      applyFilter();
      backToStart();
    });
  }
  root.querySelector("[data-quiz-retry]").addEventListener("click", begin);

  // ほかのページから「この分野を解く」で来たとき(?g=dom:9 など)は、その範囲を最初から選んでおく
  var m = /[?&]g=([^&]+)/.exec(window.location.search);
  if (m && genreSel) {
    var want = decodeURIComponent(m[1]);
    var has = [].some.call(genreSel.options, function (o) { return o.value === want; });
    if (has) { genreSel.value = want; filter = want; }
  }

  applyFilter();
})();

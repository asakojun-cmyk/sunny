/* ○×クイズドリル: 全用語の1問1答を連続出題(範囲絞り込み+シャッフル) */
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

  var startBox = root.querySelector("[data-quiz-start]");
  var card = root.querySelector("[data-quiz-card]");
  var endBox = root.querySelector("[data-quiz-end]");
  var poolEl = root.querySelector("[data-quiz-pool]");

  function applyFilter() {
    if (filter === "all") pool = ALL.slice();
    else if (filter === "freq3") {
      pool = ALL.filter(function (x) { return x.f === 3; });
    } else if (filter === "theorist") {
      pool = ALL.filter(function (x) { return x.t === 1; });
    } else {
      var cat = filter.slice(4);
      pool = ALL.filter(function (x) { return x.c === cat; });
    }
    poolEl.textContent = String(pool.length);
    var cEl = root.querySelector("[data-quiz-count]");
    if (cEl) {
      var c = COUNTS[timeSel];
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

  function renderQuestion() {
    var item = order[idx];
    root.querySelector("[data-quiz-no]").textContent = String(idx + 1);
    root.querySelector("[data-quiz-total]").textContent = String(order.length);
    root.querySelector("[data-quiz-score]").textContent = String(score);
    root.querySelector("[data-quiz-cat]").textContent = item.c + " / " + item.n;
    root.querySelector("[data-quiz-q]").textContent = item.q;
    hide(root.querySelector("[data-quiz-result]"));
    root.querySelectorAll("[data-quiz-ans]").forEach(function (b) { b.disabled = false; b.classList.remove("is-correct", "is-wrong"); });
  }

  function begin() {
    if (pool.length === 0) return;
    var c = COUNTS[timeSel];
    order = shuffle(pool);
    if (c !== null) order = order.slice(0, Math.min(c, order.length));
    idx = 0;
    score = 0;
    hide(startBox); hide(endBox); show(card);
    renderQuestion();
  }

  function finish() {
    hide(card); show(endBox);
    var rate = Math.round((score / order.length) * 100);
    root.querySelector("[data-quiz-final]").textContent = order.length + "問中 " + score + "問正解(" + rate + "%)";
    var note = rate === 100 ? "完璧!サニー先生もびっくりの仕上がりだよ☀️"
      : rate >= 80 ? "合格ライン越え!この調子で他の範囲もいってみよう😊"
      : rate >= 50 ? "いい感じ!まちがえた問題の用語ページを読み直すと、ぐんと伸びるよ"
      : "だいじょうぶ、まちがいは伸びしろ。用語ページでゆっくり復習してからまた来てね🌥️";
    root.querySelector("[data-quiz-endnote]").textContent = note;
  }

  root.querySelectorAll("[data-quiz-ans]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var item = order[idx];
      var chosen = btn.getAttribute("data-quiz-ans") === "true";
      var correct = chosen === item.a;
      if (correct) score++;
      root.querySelectorAll("[data-quiz-ans]").forEach(function (b) { b.disabled = true; });
      btn.classList.add(correct ? "is-correct" : "is-wrong");
      var v = root.querySelector("[data-quiz-verdict]");
      v.textContent = correct ? "🌞 正解!" : "🌥️ おしい!正解は「" + (item.a ? "○" : "×") + "」";
      v.className = "quiz-drill__verdict " + (correct ? "is-ok" : "is-ng");
      root.querySelector("[data-quiz-exp]").textContent = item.e;
      var link = root.querySelector("[data-quiz-link]");
      link.setAttribute("href", item.u);
      link.textContent = "「" + item.n + "」のページで復習する →";
      root.querySelector("[data-quiz-score]").textContent = String(score);
      show(root.querySelector("[data-quiz-result]"));
    });
  });

  root.querySelector("[data-quiz-next]").addEventListener("click", function () {
    idx++;
    if (idx >= order.length) finish();
    else renderQuestion();
  });
  root.querySelector("[data-quiz-begin]").addEventListener("click", begin);
  var randBtn = root.querySelector("[data-quiz-random]");
  if (randBtn) {
    randBtn.addEventListener("click", function () {
      pool = ALL.slice();
      order = shuffle(pool).slice(0, Math.min(10, pool.length));
      idx = 0; score = 0;
      hide(startBox); hide(endBox); show(card);
      renderQuestion();
    });
  }
  document.querySelectorAll("[data-quiz-time]").forEach(function (chip) {
    chip.addEventListener("click", function () {
      timeSel = chip.getAttribute("data-quiz-time");
      document.querySelectorAll("[data-quiz-time]").forEach(function (c) {
        c.setAttribute("aria-pressed", c === chip ? "true" : "false");
      });
      applyFilter();
      hide(card); hide(endBox); show(startBox);
    });
  });
  root.querySelector("[data-quiz-retry]").addEventListener("click", begin);

  document.querySelectorAll("[data-quiz-filter]").forEach(function (chip) {
    chip.addEventListener("click", function () {
      filter = chip.getAttribute("data-quiz-filter");
      document.querySelectorAll("[data-quiz-filter]").forEach(function (c) {
        c.setAttribute("aria-pressed", c === chip ? "true" : "false");
      });
      applyFilter();
      hide(card); hide(endBox); show(startBox);
    });
  });

  applyFilter();
})();

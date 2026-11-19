/* 1問1答ドリル（/games/quiz/）の新しい型（2026-11-20）：ラフのボタンで、本番の js/quiz-drill.js を動かすだけ。
 * - 範囲・時間のボタン → 本番の <select>（data-quiz-genre・data-quiz-timesel）を選んで change を送る
 * - 「1分でスタート」→ 時間を1分にして、本番の「始める」を押す
 * - 流れ（範囲と時間を選ぶ → 答える → 正誤と解説 → 次へ・結果）と「きょうの進み具合」に色をつける
 * 問題・採点・記録（この端末だけ）は quiz-drill.js のまま */
(function () {
  "use strict";
  var genre = document.querySelector("[data-quiz-genre]");
  var time = document.querySelector("[data-quiz-timesel]");
  var start = document.querySelector("[data-quiz-start]");
  var stage = document.querySelector("[data-quiz-drill]");
  if (!genre || !time || !start || !stage) return;
  var card = stage.querySelector("[data-quiz-card]");
  var result = stage.querySelector("[data-quiz-result]");
  var end = stage.querySelector("[data-quiz-end]");
  var begin = document.querySelector("[data-quiz-begin]");
  var flow = document.querySelectorAll("#dflow li");
  var smooth = !(window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches);

  function pick(sel, v) {
    if (sel.value === v) return;
    sel.value = v;
    sel.dispatchEvent(new Event("change"));
  }
  function pressed() {
    Array.prototype.forEach.call(document.querySelectorAll('.opts[data-g="genre"] .opt'), function (b) {
      b.setAttribute("aria-pressed", String(b.getAttribute("data-v") === genre.value));
    });
    Array.prototype.forEach.call(document.querySelectorAll('.opts[data-g="time"] .opt'), function (b) {
      b.setAttribute("aria-pressed", String(b.getAttribute("data-v") === time.value));
    });
  }
  Array.prototype.forEach.call(document.querySelectorAll(".opts"), function (g) {
    g.addEventListener("click", function (ev) {
      var b = ev.target.closest(".opt");
      if (!b) return;
      pick(g.getAttribute("data-g") === "time" ? time : genre, b.getAttribute("data-v"));
      pressed();
    });
  });
  var quick = document.querySelector("[data-qk-quick]");
  if (quick) {
    quick.addEventListener("click", function () {
      pick(time, "1");
      pressed();
      begin.click();
      var d = document.getElementById("drill");
      if (d) d.scrollIntoView({ behavior: smooth ? "smooth" : "auto", block: "start" });
    });
  }
  pressed(); /* ?g= ?n= で来たときも、本番が選んだものに色をつける */

  /* ---- 流れと、きょうの進み具合 ---- */
  var log = [];
  var total = 0;
  var okEl = document.querySelector("[data-qk-ok]");
  var doneEl = document.querySelector("[data-qk-done]");
  var dotsEls = document.querySelectorAll("[data-qk-dots]");
  function no() { return parseInt((stage.querySelector("[data-quiz-no]") || {}).textContent, 10) || 1; }
  function draw() {
    var step = !start.hidden ? 0 : !end.hidden ? 3 : !result.hidden ? 2 : 1;
    Array.prototype.forEach.call(flow, function (li, i) { li.className = i < step ? "done" : i === step ? "on" : ""; });
    var ok = log.filter(function (x) { return x; }).length;
    var done = log.filter(function (x) { return x != null; }).length;
    if (okEl) okEl.textContent = ok;
    if (doneEl) doneEl.textContent = total ? "／ " + total + "問のうち " + done + "問 解いた" : "／ まだ解いていません";
    var h = "";
    for (var i = 0; i < total; i++) {
      var c = log[i] == null ? (i === no() - 1 && step < 3 ? "now" : "") : log[i] ? "ok" : "ng";
      h += '<i class="' + c + '"></i>';
    }
    Array.prototype.forEach.call(dotsEls, function (d) { d.innerHTML = h; });
  }
  function watch(el, fn) {
    if (el && "MutationObserver" in window) new MutationObserver(fn).observe(el, { attributes: true, attributeFilter: ["hidden"] });
  }
  watch(card, function () {
    if (!card.hidden && no() === 1 && result.hidden) {
      total = parseInt(stage.querySelector("[data-quiz-total]").textContent, 10) || 0;
      log = [];
    }
    draw();
  });
  watch(result, function () {
    if (!result.hidden) {
      var v = stage.querySelector("[data-quiz-verdict]");
      log[no() - 1] = !!(v && v.classList.contains("is-ok"));
      result.classList.toggle("ng", !log[no() - 1]);
    }
    draw();
  });
  watch(start, draw);
  watch(end, draw);
  draw();
})();

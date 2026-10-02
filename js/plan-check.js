/* 30日の逆算プラン: 試験日までの日数と、「できたらチェック」。チェックはこの端末のブラウザにだけ保存する */
(function () {
  "use strict";
  var dayEl = document.querySelector("[data-exam-days]");
  if (dayEl) {
    var exam = new Date(2026, 10, 1); // 2026年11月1日(第33回)
    var now = new Date();
    var today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    var days = Math.round((exam - today) / 86400000);
    var wrap = document.querySelector("[data-exam-countdown]");
    if (days > 0) dayEl.textContent = String(days);
    else if (wrap) wrap.textContent = days === 0 ? "きょうが試験日。いってらっしゃい！" : "第33回の試験は終わりました。おつかれさまでした。";
  }
  var KEY = "carepicnic-plan30-v1";
  var boxes = [].slice.call(document.querySelectorAll("[data-plan-check]"));
  if (!boxes.length) return;
  var saved = {};
  try { saved = JSON.parse(window.localStorage.getItem(KEY) || "{}") || {}; } catch (_e) { saved = {}; }
  var doneEl = document.querySelector("[data-plan-done]");
  var totalEl = document.querySelector("[data-plan-total]");
  var barEl = document.querySelector("[data-plan-bar]");
  function render() {
    var n = 0;
    boxes.forEach(function (b) {
      var on = !!saved[b.getAttribute("data-plan-check")];
      b.checked = on;
      var li = b.closest("li");
      if (li) li.classList.toggle("is-done", on);
      if (on) n++;
    });
    if (doneEl) doneEl.textContent = String(n);
    if (totalEl) totalEl.textContent = String(boxes.length);
    if (barEl) barEl.style.width = Math.round((n / boxes.length) * 100) + "%";
  }
  boxes.forEach(function (b) {
    b.addEventListener("change", function () {
      var id = b.getAttribute("data-plan-check");
      if (b.checked) saved[id] = 1; else delete saved[id];
      try { window.localStorage.setItem(KEY, JSON.stringify(saved)); } catch (_e) { /* 保存できなくても表示は動かす */ }
      render();
    });
  });
  render();
})();

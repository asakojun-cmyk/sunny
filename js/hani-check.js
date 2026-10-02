/* 出題範囲と対応表: 1問1答の結果(この端末のブラウザに保存)から、分野ごとの理解度を表示する */
(function () {
  "use strict";
  var doms = null;
  try { doms = JSON.parse(window.localStorage.getItem("carepicnic-quiz-domains-v1") || "null"); } catch (_e) { doms = null; }
  var meters = [].slice.call(document.querySelectorAll("[data-rikaido]"));
  if (!meters.length) return;
  var any = false;
  meters.forEach(function (el) {
    var d = doms && doms[el.getAttribute("data-rikaido")];
    var bar = el.querySelector("[data-rikaido-bar]");
    var text = el.querySelector("[data-rikaido-text]");
    if (!d || !d.total || (d.ok + d.ng) === 0) {
      if (text) text.textContent = "まだ記録がありません";
      return;
    }
    any = true;
    var pct = Math.round((d.ok / d.total) * 100);
    if (bar) bar.style.width = pct + "%";
    if (text) text.textContent = pct + "%(" + d.total + "問中 " + d.ok + "問正解" + (d.ng ? "・まちがえたまま " + d.ng + "問" : "") + ")";
    el.classList.add("has-data");
  });
  var empty = document.querySelector("[data-rikaido-empty]");
  if (empty) empty.hidden = any;
  var reset = document.querySelector("[data-rikaido-reset]");
  if (reset) {
    reset.addEventListener("click", function () {
      try {
        window.localStorage.removeItem("carepicnic-quiz-domains-v1");
        window.localStorage.removeItem("carepicnic-quiz-log-v1");
      } catch (_e) { /* 何もしない */ }
      window.location.reload();
    });
  }
})();

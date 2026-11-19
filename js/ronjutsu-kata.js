/* 論述ボードゲーム（/games/ronjutsu/）の新しい型（2026-11-20）：受ける型（CC協議会型・JCDA型）をえらぶ札。
 * えらんだ型のバッジがついたマスに色がつく。マスの並び・進み方・正誤は本番の js/ronjutsu.js のまま */
(function () {
  "use strict";
  var pks = document.querySelectorAll(".pick .pk[data-mode]");
  if (!pks.length) return;
  var name = document.querySelector("[data-mode-name]");
  var KEY = "ronjutsu-mode";
  function set(mode) {
    Array.prototype.forEach.call(pks, function (b) {
      var on = b.getAttribute("data-mode") === mode;
      b.setAttribute("aria-pressed", String(on));
      if (on && name) name.textContent = b.querySelector(".nm").textContent;
    });
    document.documentElement.setAttribute("data-ron-mode", mode);
    try { localStorage.setItem(KEY, mode); } catch (e) {}
  }
  Array.prototype.forEach.call(pks, function (b) {
    b.addEventListener("click", function () {
      set(b.getAttribute("data-mode"));
      var j = document.getElementById("jirei");
      if (j) j.scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "start" });
    });
  });
  var saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) {}
  set(saved === "jcda" ? "jcda" : "cc");
})();

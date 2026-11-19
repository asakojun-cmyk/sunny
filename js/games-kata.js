/* ミニゲームの一覧（/games/）の新しい型（2026-11-20）：「試験のどこに効く？」で、カードを絞りこむ */
(function () {
  "use strict";
  var bs = document.querySelectorAll(".filt .opt");
  Array.prototype.forEach.call(bs, function (b) {
    b.addEventListener("click", function () {
      Array.prototype.forEach.call(bs, function (x) { x.setAttribute("aria-pressed", "false"); });
      b.setAttribute("aria-pressed", "true");
      var f = b.getAttribute("data-f");
      Array.prototype.forEach.call(document.querySelectorAll(".gcard"), function (c) {
        c.hidden = !(f === "all" || c.getAttribute("data-t").split(" ").indexOf(f) >= 0);
      });
      Array.prototype.forEach.call(document.querySelectorAll("[data-grp]"), function (g) {
        g.hidden = !g.querySelector(".gcard:not([hidden])");
      });
    });
  });
})();

/* お弁当（新しい型・2026-11-20）：上に貼りつく「いま読んでいる所」の帯。
 * 読んでいる段に色をつけ、ことばのタネの段が終わったら帯を消す（出口の段に重ならないように）。 */
(function () {
  "use strict";
  var bar = document.querySelector(".prog");
  if (!bar) return;
  var as = Array.prototype.slice.call(bar.querySelectorAll("a[data-t]"));
  var ids = as.map(function (a) { return a.getAttribute("data-t"); });
  var last = document.getElementById(ids[ids.length - 1]);
  function up() {
    var y = window.innerHeight * 0.35, cur = -1;
    ids.forEach(function (id, i) {
      var el = document.getElementById(id);
      if (el && el.getBoundingClientRect().top < y) cur = i;
    });
    as.forEach(function (a, i) { a.classList.toggle("now", i === cur); a.classList.toggle("done", i < cur); });
    if (last) bar.classList.toggle("x-gone", last.getBoundingClientRect().bottom < bar.offsetHeight + 8);
  }
  window.addEventListener("scroll", up, { passive: true });
  window.addEventListener("resize", up);
  up();
})();

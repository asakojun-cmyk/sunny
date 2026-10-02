/* 試験対策ページ: 絵のカードを押すと、その中のページの一覧が下にひらく */
(function () {
  "use strict";
  var root = document.querySelector("[data-study-cards]");
  if (!root) return;
  var cards = [].slice.call(root.querySelectorAll("[data-acc]"));
  var panels = [].slice.call(root.querySelectorAll("[data-acc-panel]"));
  function show(key) {
    cards.forEach(function (c) {
      var on = c.getAttribute("data-acc") === key;
      c.classList.toggle("is-open", on);
      c.setAttribute("aria-expanded", on ? "true" : "false");
    });
    panels.forEach(function (p) { p.hidden = p.getAttribute("data-acc-panel") !== key; });
  }
  cards.forEach(function (c) {
    c.addEventListener("click", function () {
      var key = c.getAttribute("data-acc");
      show(c.classList.contains("is-open") ? "" : key);
    });
  });
})();

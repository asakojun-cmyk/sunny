/* 学校一覧の絞り込み(フロントエンドのみの簡易フィルター) */
(function () {
  "use strict";
  var chips = document.querySelectorAll(".filter-chip[data-filter]");
  var reset = document.querySelector("[data-filter-reset]");
  var cards = document.querySelectorAll("[data-school-list] .school-card");
  if (!chips.length || !cards.length) return;

  function apply() {
    var active = [];
    chips.forEach(function (chip) {
      if (chip.getAttribute("aria-pressed") === "true") {
        active.push(chip.getAttribute("data-filter"));
      }
    });
    cards.forEach(function (card) {
      var tags = (card.getAttribute("data-filter-tags") || "").split(/\s+/);
      var visible = active.every(function (f) {
        return tags.indexOf(f) !== -1;
      });
      card.classList.toggle("is-hidden", !visible);
    });
  }

  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      var pressed = chip.getAttribute("aria-pressed") === "true";
      chip.setAttribute("aria-pressed", pressed ? "false" : "true");
      apply();
    });
  });

  if (reset) {
    reset.addEventListener("click", function () {
      chips.forEach(function (chip) {
        chip.setAttribute("aria-pressed", "false");
      });
      apply();
    });
  }
})();

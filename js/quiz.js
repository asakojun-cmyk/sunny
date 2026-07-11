/* 用語ページの1問1答(○×) */
(function () {
  "use strict";
  document.querySelectorAll("[data-quiz]").forEach(function (box) {
    var answer = box.getAttribute("data-answer") === "true";
    var result = box.querySelector("[data-quiz-result]");
    if (!result) return;
    var original = result.textContent;
    box.querySelectorAll("[data-quiz-answer]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var chosen = btn.getAttribute("data-quiz-answer") === "true";
        var prefix = chosen === answer ? "正解です。" : "おしい!";
        result.textContent = prefix + " " + original;
        result.hidden = false;
      });
    });
  });
})();

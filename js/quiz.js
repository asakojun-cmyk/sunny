/* 用語・理論家ページの1問1答(○×と4択) */
(function () {
  "use strict";
  document.querySelectorAll("[data-quiz]").forEach(function (box) {
    var result = box.querySelector("[data-quiz-result]");
    if (!result) return;
    var original = result.textContent;

    var choices = box.querySelectorAll("[data-quiz-choice]");
    if (choices.length) {
      var correctIdx = parseInt(box.getAttribute("data-correct"), 10);
      choices.forEach(function (btn, i) {
        btn.addEventListener("click", function () {
          var ok = i === correctIdx;
          choices.forEach(function (b) { b.disabled = true; });
          btn.classList.add(ok ? "is-correct" : "is-wrong");
          if (!ok && choices[correctIdx]) choices[correctIdx].classList.add("is-correct");
          result.textContent = (ok ? "正解です。" : "おしい!") + " " + original;
          result.hidden = false;
        });
      });
      return;
    }

    var answer = box.getAttribute("data-answer") === "true";
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

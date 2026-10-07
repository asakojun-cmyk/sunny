/* 用語・理論家ページの1問1答(○×と4択)。
 * 1ページに何問あってもよい。答えると正解数を数え、全部とき終わると結果と「もう一度」を出す。 */
(function () {
  "use strict";
  var boxes = Array.prototype.slice.call(document.querySelectorAll("[data-quiz]"));
  if (!boxes.length) return;

  var groups = [];
  boxes.forEach(function (box) {
    var parent = box.parentNode;
    var g = null;
    for (var i = 0; i < groups.length; i++) if (groups[i].parent === parent) g = groups[i];
    if (!g) { g = { parent: parent, boxes: [], done: 0, ok: 0, score: parent.querySelector("[data-quiz-score]") }; groups.push(g); }
    g.boxes.push(box);
  });

  function showScore(g) {
    if (!g.score || g.boxes.length < 2) return;
    g.score.hidden = false;
    if (g.done < g.boxes.length) {
      g.score.textContent = g.boxes.length + "問中 " + g.done + "問とき終わりました";
      return;
    }
    var all = g.ok === g.boxes.length;
    g.score.innerHTML = "";
    var b = document.createElement("b");
    b.textContent = g.boxes.length + "問中 " + g.ok + "問 正解";
    g.score.appendChild(b);
    g.score.appendChild(document.createTextNode(all ? " 全問正解です。" : " まちがえた問題の解説を、もう一度読んでみましょう。"));
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "quiz-score__retry";
    btn.textContent = "もう一度とく";
    btn.addEventListener("click", function () { g.boxes.forEach(function (bx) { bx.__reset(); }); g.done = 0; g.ok = 0; g.score.hidden = true; g.boxes[0].scrollIntoView({ behavior: "smooth", block: "center" }); });
    g.score.appendChild(btn);
  }

  groups.forEach(function (g) {
    g.boxes.forEach(function (box) {
      var result = box.querySelector("[data-quiz-result]");
      if (!result) return;
      var original = result.textContent;
      var answered = false;
      var btns = Array.prototype.slice.call(box.querySelectorAll("[data-quiz-choice],[data-quiz-answer]"));

      function finish(ok, picked, right) {
        if (answered) return;
        answered = true;
        btns.forEach(function (b) { b.disabled = true; });
        if (picked) picked.classList.add(ok ? "is-correct" : "is-wrong");
        if (!ok && right) right.classList.add("is-correct");
        box.classList.add(ok ? "is-ok" : "is-ng");
        result.textContent = (ok ? "正解です。" : "おしい！") + " " + original;
        result.hidden = false;
        g.done++; if (ok) g.ok++;
        showScore(g);
      }
      box.__reset = function () {
        answered = false;
        btns.forEach(function (b) { b.disabled = false; b.classList.remove("is-correct", "is-wrong"); });
        box.classList.remove("is-ok", "is-ng");
        result.textContent = original;
        result.hidden = true;
      };

      var choices = Array.prototype.slice.call(box.querySelectorAll("[data-quiz-choice]"));
      if (choices.length) {
        var correctIdx = parseInt(box.getAttribute("data-correct"), 10);
        choices.forEach(function (btn, i) {
          btn.addEventListener("click", function () { finish(i === correctIdx, btn, choices[correctIdx]); });
        });
        return;
      }
      var answer = box.getAttribute("data-answer") === "true";
      var ans = Array.prototype.slice.call(box.querySelectorAll("[data-quiz-answer]"));
      ans.forEach(function (btn) {
        btn.addEventListener("click", function () {
          var chosen = btn.getAttribute("data-quiz-answer") === "true";
          var right = ans.filter(function (b) { return (b.getAttribute("data-quiz-answer") === "true") === answer; })[0];
          finish(chosen === answer, btn, right);
        });
      });
    });
  });
})();

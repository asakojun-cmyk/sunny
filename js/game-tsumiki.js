/* 傾聴のつみきブロック: 人間観→基本的態度→技法の順に積む */
(function () {
  var game = document.getElementById("tsumiki-game");
  if (!game) return;
  var ORDER = ["ningen", "taido", "giho"];
  var LABEL = { ningen: "人間観", taido: "基本的態度", giho: "技法" };
  var stack = game.querySelector("[data-stack]");
  var bank = game.querySelector("[data-bank]");
  var feedback = game.querySelector("[data-feedback]");
  var clearBox = game.querySelector("[data-clear]");
  var placed = 0;
  var locked = false;

  function reset() {
    placed = 0;
    locked = false;
    stack.innerHTML = "";
    clearBox.hidden = true;
    bank.hidden = false;
    Array.prototype.forEach.call(bank.querySelectorAll("[data-block]"), function (b) {
      b.disabled = false;
      b.style.visibility = "visible";
    });
    feedback.textContent = "👇 土台にするブロックからタップしてね";
  }

  bank.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-block]");
    if (!btn || locked) return;
    var kind = btn.getAttribute("data-block");
    if (kind === ORDER[placed]) {
      var block = document.createElement("div");
      block.className = "tsumiki-block tsumiki-block--" + kind + " tsumiki-block--placed";
      block.textContent = LABEL[kind];
      stack.appendChild(block);
      btn.disabled = true;
      btn.style.visibility = "hidden";
      placed++;
      if (placed === 1) feedback.textContent = "☀️ そのとおり! 土台は「人は成長する」という信頼から。次は?";
      if (placed === 2) feedback.textContent = "☀️ いいね! 態度がのった。最後の仕上げは?";
      if (placed === ORDER.length) {
        feedback.textContent = "";
        bank.hidden = true;
        clearBox.hidden = false;
      }
    } else {
      locked = true;
      var wrong = document.createElement("div");
      wrong.className = "tsumiki-block tsumiki-block--" + kind + " tsumiki-block--placed";
      wrong.textContent = LABEL[kind];
      stack.appendChild(wrong);
      stack.classList.add("is-collapse");
      feedback.textContent = "🌥️ わ〜! " + LABEL[kind] + "を先に積んだら、グラグラ…くずれちゃった! カウンセリング失敗〜。";
      setTimeout(function () {
        stack.classList.remove("is-collapse");
        stack.innerHTML = "";
        placed = 0;
        locked = false;
        Array.prototype.forEach.call(bank.querySelectorAll("[data-block]"), function (b) {
          b.disabled = false;
          b.style.visibility = "visible";
        });
        setTimeout(function () {
          feedback.textContent = "もう一回! いちばん下に置くべきものはどれかな?";
        }, 200);
      }, 1400);
    }
  });

  game.querySelector("[data-retry]").addEventListener("click", reset);
})();

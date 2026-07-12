/* 理論家の流派仕分けゲーム */
(function () {
  var game = document.getElementById("ryuha-game");
  if (!game) return;
  var cards = Array.prototype.slice.call(game.querySelectorAll("[data-card]"));
  var buckets = Array.prototype.slice.call(game.querySelectorAll("[data-bucket]"));
  var progress = game.querySelector("[data-progress]");
  var missEl = game.querySelector("[data-miss]");
  var feedback = game.querySelector("[data-feedback]");
  var clearBox = game.querySelector("[data-clear]");
  var resultEl = game.querySelector("[data-result]");
  var order = [];
  var pos = 0;
  var miss = 0;
  var locked = false;

  function shuffle(a) {
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }

  function finish() {
    clearBox.hidden = false;
    var text = miss === 0
      ? "ノーミス! 流派マスターだよ、すごい!"
      : "ミス" + miss + "回。まちがえた流派の説明を下で読み直そうね。";
    resultEl.textContent = "☀️ " + text;
    feedback.textContent = "";
    buckets.forEach(function (b) { b.disabled = true; });
    clearBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function show() {
    cards.forEach(function (c) { c.hidden = true; c.classList.remove("is-wrong"); });
    if (pos >= order.length) return finish();
    order[pos].hidden = false;
    progress.textContent = (pos + 1) + " / " + cards.length;
    missEl.textContent = "ミス: " + miss;
  }

  function start() {
    order = shuffle(cards.slice());
    pos = 0;
    miss = 0;
    locked = false;
    clearBox.hidden = true;
    buckets.forEach(function (b) { b.disabled = false; });
    feedback.textContent = "この理論家は、どの流派の棚に入る?";
    show();
  }

  buckets.forEach(function (b) {
    b.addEventListener("click", function () {
      if (locked || pos >= order.length) return;
      var card = order[pos];
      if (b.getAttribute("data-bucket") === card.getAttribute("data-school")) {
        locked = true;
        feedback.textContent = "☀️ 正解! " + card.querySelector("[data-fact]").textContent;
        b.classList.add("is-correct");
        setTimeout(function () {
          b.classList.remove("is-correct");
          pos++;
          locked = false;
          if (pos < order.length) feedback.textContent = "つぎ! この理論家はどの棚?";
          show();
        }, 1400);
      } else {
        miss++;
        missEl.textContent = "ミス: " + miss;
        card.classList.add("is-wrong");
        feedback.textContent = "🌥️ おしい! べつの棚みたい。ヒント: " + card.querySelector("[data-fact]").textContent;
        setTimeout(function () { card.classList.remove("is-wrong"); }, 500);
      }
    });
  });

  game.querySelector("[data-retry]").addEventListener("click", start);
  start();
})();

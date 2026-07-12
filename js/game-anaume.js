/* 理論の図あなうめゲーム: 枠をタップ→言葉をタップではめる */
(function () {
  var game = document.getElementById("anaume-game");
  if (!game) return;

  var tabs = Array.prototype.slice.call(game.querySelectorAll("[data-anaume-tab]"));
  var boards = Array.prototype.slice.call(game.querySelectorAll("[data-anaume-board]"));
  tabs.forEach(function (t) {
    t.addEventListener("click", function () {
      tabs.forEach(function (x) { x.classList.toggle("is-active", x === t); });
      boards.forEach(function (b) {
        b.hidden = b.getAttribute("data-anaume-board") !== t.getAttribute("data-anaume-tab");
      });
    });
  });

  boards.forEach(function (board) {
    var slots = Array.prototype.slice.call(board.querySelectorAll("[data-slot]"));
    var chips = Array.prototype.slice.call(board.querySelectorAll("[data-chip]"));
    var feedback = board.querySelector("[data-feedback]");
    var usage = board.querySelector("[data-usage]");
    var active = null;

    function selectSlot(s) {
      if (s.classList.contains("is-filled")) return;
      active = s;
      slots.forEach(function (x) { x.classList.toggle("is-active", x === s); });
      feedback.textContent = "この枠に入る言葉をタップしてね";
    }

    slots.forEach(function (s) {
      s.addEventListener("click", function () { selectSlot(s); });
    });

    chips.forEach(function (chip) {
      chip.addEventListener("click", function () {
        if (chip.disabled) return;
        if (!active) {
          var firstEmpty = slots.filter(function (s) { return !s.classList.contains("is-filled"); })[0];
          if (!firstEmpty) return;
          selectSlot(firstEmpty);
        }
        var word = chip.getAttribute("data-chip");
        if (active.getAttribute("data-answer") === word) {
          active.classList.remove("is-active");
          active.classList.add("is-filled");
          active.querySelector(".anaume-slot__q").textContent = word;
          chip.disabled = true;
          chip.classList.add("is-used");
          active = null;
          var remaining = slots.filter(function (s) { return !s.classList.contains("is-filled"); });
          if (remaining.length === 0) {
            feedback.textContent = "";
            usage.hidden = false;
            usage.scrollIntoView({ behavior: "smooth", block: "nearest" });
          } else {
            feedback.textContent = "☀️ 正解! つぎの「?」をタップしてね";
          }
        } else {
          chip.classList.add("is-wrong");
          feedback.textContent = "🌥️ そこじゃないみたい。ヒントの小さな文字を見てみて!";
          setTimeout(function () { chip.classList.remove("is-wrong"); }, 500);
        }
      });
    });
  });
})();

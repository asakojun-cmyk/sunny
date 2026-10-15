/* 理論の図あなうめゲーム
   言葉を図の「?」までドラッグ。タップで言葉→「?」(または「?」→言葉)の順に選んでもはめられる */
(function () {
  "use strict";
  var game = document.getElementById("anaume-game");
  if (!game) return;
  var tabs = [].slice.call(game.querySelectorAll("[data-anaume-tab]"));
  var boards = [].slice.call(game.querySelectorAll("[data-anaume-board]"));
  var allDone = game.querySelector("[data-all]");

  tabs.forEach(function (t) {
    t.addEventListener("click", function () {
      tabs.forEach(function (x) { x.classList.toggle("is-active", x === t); });
      boards.forEach(function (b) { b.hidden = b.getAttribute("data-anaume-board") !== t.getAttribute("data-anaume-tab"); });
    });
  });

  function shuffle(a) {
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }

  boards.forEach(function (board) {
    var key = board.getAttribute("data-anaume-board");
    var slots = [].slice.call(board.querySelectorAll("[data-slot]"));
    var chipBox = board.querySelector("[data-chips]");
    var chips = [].slice.call(board.querySelectorAll("[data-chip]"));
    var msg = board.querySelector("[data-feedback]");
    var usage = board.querySelector("[data-usage]");
    var pickedChip = null, pickedSlot = null, miss = 0;
    shuffle(chips).forEach(function (c) { chipBox.appendChild(c); });

    function say(t) { msg.textContent = t; }
    function clearPick() {
      if (pickedChip) pickedChip.classList.remove("is-picked");
      if (pickedSlot) pickedSlot.classList.remove("is-picked");
      pickedChip = pickedSlot = null;
      board.classList.remove("is-picking");
    }

    function tryPut(chip, s) {
      clearPick();
      if (!chip || !s || s.classList.contains("is-filled") || chip.disabled) return;
      var word = chip.getAttribute("data-chip");
      if (s.getAttribute("data-answer") === word) {
        s.classList.add("is-filled");
        s.querySelector(".az-slot__q").textContent = word;
        s.setAttribute("aria-label", word);
        chip.disabled = true;
        chip.classList.add("is-used");
        var left = slots.filter(function (x) { return !x.classList.contains("is-filled"); }).length;
        if (left) { say("☀️ 正解！ のこり" + left + "つ。"); return; }
        say(miss === 0 ? "⭐ ノーミスで完成！" : "🎉 完成！(ミス" + miss + "回)");
        usage.hidden = false;
        var tab = game.querySelector('[data-anaume-tab="' + key + '"]');
        if (tab && tab.textContent.indexOf("✓") < 0) tab.insertAdjacentText("beforeend", " ✓");
        if (allDone && boards.every(function (b) { return !b.querySelector("[data-slot]:not(.is-filled)"); })) allDone.hidden = false;
        setTimeout(function () { usage.scrollIntoView({ behavior: "smooth", block: "nearest" }); }, 200);
      } else {
        miss++;
        chip.classList.remove("is-wrong"); void chip.offsetWidth; chip.classList.add("is-wrong");
        s.classList.remove("is-wrong"); void s.offsetWidth; s.classList.add("is-wrong");
        var note = s.querySelector(".az-slot__note");
        say("🌥️ 「" + word + "」は、そこじゃないみたい。" + (note ? "枠の小さな文字がヒントだよ。" : "図の上下・内外の位置をヒントにしてみて。"));
      }
    }

    /* タップ */
    chips.forEach(function (c) {
      c.addEventListener("click", function () {
        if (justDragged || c.disabled) return;
        if (pickedSlot) return tryPut(c, pickedSlot);
        var same = pickedChip === c;
        clearPick();
        if (same) return;
        pickedChip = c; c.classList.add("is-picked"); board.classList.add("is-picking");
        say("「" + c.getAttribute("data-chip") + "」を選んだよ。はめたい「?」をタップしてね。");
      });
    });
    slots.forEach(function (s) {
      s.addEventListener("click", function () {
        if (justDragged || s.classList.contains("is-filled")) return;
        if (pickedChip) return tryPut(pickedChip, s);
        var same = pickedSlot === s;
        clearPick();
        if (same) return;
        pickedSlot = s; s.classList.add("is-picked");
        say("この枠に入る言葉をタップしてね。");
      });
    });

    /* ドラッグ(マウス・タッチ共通)。言葉の置き場は縦にドラッグ、横はスクロール */
    var drag = null, justDragged = false;
    chipBox.addEventListener("pointerdown", function (e) {
      var c = e.target.closest("[data-chip]");
      if (!c || c.disabled || e.button > 0) return;
      drag = { chip: c, sx: e.clientX, sy: e.clientY, id: e.pointerId, ghost: null, over: null };
    });
    window.addEventListener("pointermove", function (e) {
      if (!drag || drag.id !== e.pointerId) return;
      if (!drag.ghost) {
        if (Math.abs(e.clientX - drag.sx) + Math.abs(e.clientY - drag.sy) < 8) return;
        var r = drag.chip.getBoundingClientRect();
        drag.dx = e.clientX - r.left; drag.dy = e.clientY - r.top;
        drag.ghost = drag.chip.cloneNode(true);
        drag.ghost.className = "az-chip az-ghost";
        drag.ghost.style.width = r.width + "px";
        document.body.appendChild(drag.ghost);
        drag.chip.classList.add("is-dragging");
        clearPick();
      }
      e.preventDefault();
      drag.ghost.style.transform = "translate(" + (e.clientX - drag.dx) + "px," + (e.clientY - drag.dy) + "px)";
      var el = document.elementFromPoint(e.clientX, e.clientY);
      var s = el && el.closest("[data-slot]");
      if (s && (s.classList.contains("is-filled") || !board.contains(s))) s = null;
      if (s !== drag.over) {
        if (drag.over) drag.over.classList.remove("is-over");
        if (s) s.classList.add("is-over");
        drag.over = s;
      }
    }, { passive: false });
    function end(e, cancel) {
      if (!drag || drag.id !== e.pointerId) return;
      var d = drag; drag = null;
      if (!d.ghost) return;
      d.ghost.remove();
      d.chip.classList.remove("is-dragging");
      if (d.over) d.over.classList.remove("is-over");
      justDragged = true; setTimeout(function () { justDragged = false; }, 50);
      if (!cancel && d.over) tryPut(d.chip, d.over);
    }
    window.addEventListener("pointerup", function (e) { end(e, false); });
    window.addEventListener("pointercancel", function (e) { end(e, true); });
  });
})();

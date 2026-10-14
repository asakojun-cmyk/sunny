/* 理論家の流派仕分けゲーム
   ① カードを流派の箱の「仮置き場」へ(流派だけを当てる)
   ② 箱に集まった人を、左の上流から右の下流へ「?」に並べる(順番だけを当てる)
   ドラッグでも、タップで選んでからタップでもよい。
   カードにカーソルを当てる(スマホはタップ)と、理論家のひとことが吹き出しで出る */
(function () {
  var game = document.getElementById("ryuha-game");
  if (!game) return;
  var tray = game.querySelector("[data-tray]");
  var dock = game.querySelector("[data-dock]");
  var chips = Array.prototype.slice.call(game.querySelectorAll("[data-chip]"));
  var slots = Array.prototype.slice.call(game.querySelectorAll("[data-slot]"));
  var boxes = Array.prototype.slice.call(game.querySelectorAll("[data-box]"));
  var leftEl = game.querySelector("[data-left]");
  var missEl = game.querySelector("[data-miss]");
  var msg = game.querySelector("[data-msg]");
  var clearBox = game.querySelector("[data-clear]");
  var resultEl = game.querySelector("[data-result]");
  var header = document.querySelector(".site-header");
  var selected = null;
  var miss = 0;
  var placed = 0;
  var missBy = {};

  function nameOf(chip) { return chip.querySelector(".rg-chip__name").textContent; }
  function boxOf(el) { return el.closest("[data-box]"); }
  function schoolName(el) { return boxOf(el).querySelector(".rg-box__name").textContent; }
  function poolOf(box) { return box.querySelector("[data-pool]"); }
  function say(text) { msg.textContent = text; }

  function shuffle(a) {
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }

  /* ---- 吹き出し ---- */
  var tip = document.createElement("div");
  tip.className = "rg-tip";
  tip.setAttribute("role", "tooltip");
  tip.hidden = true;
  document.body.appendChild(tip);
  var tipFor = null;

  function showTip(chip) {
    if (!chip || (drag && drag.ghost)) return;
    tipFor = chip;
    tip.innerHTML = "";
    var who = document.createElement("b");
    who.textContent = nameOf(chip);
    tip.appendChild(who);
    tip.appendChild(document.createTextNode(chip.getAttribute("data-hint")));
    tip.hidden = false;
    var r = chip.getBoundingClientRect();
    var tw = tip.offsetWidth, th = tip.offsetHeight;
    var x = Math.max(8, Math.min(window.innerWidth - tw - 8, r.left + r.width / 2 - tw / 2));
    var below = r.top - th - 12 < 70;
    var y = below ? r.bottom + 12 : r.top - th - 12;
    tip.classList.toggle("is-below", below);
    tip.style.left = x + "px";
    tip.style.top = y + "px";
    tip.style.setProperty("--arrow", (r.left + r.width / 2 - x) + "px");
  }
  function hideTip(chip) {
    if (chip && chip !== tipFor) return;
    tip.hidden = true;
    tipFor = null;
  }
  game.addEventListener("mouseover", function (e) {
    var chip = e.target.closest("[data-chip]");
    if (chip && chip !== tipFor) showTip(chip);
  });
  game.addEventListener("mouseout", function (e) {
    var chip = e.target.closest("[data-chip]");
    if (chip && !chip.contains(e.relatedTarget) && chip !== selected) hideTip(chip);
  });
  game.addEventListener("focusin", function (e) {
    var chip = e.target.closest("[data-chip]");
    if (chip) showTip(chip);
  });
  game.addEventListener("focusout", function (e) {
    var chip = e.target.closest("[data-chip]");
    if (chip && chip !== selected) hideTip(chip);
  });
  window.addEventListener("scroll", function () { if (tipFor) showTip(tipFor); }, { passive: true });
  tray.addEventListener("scroll", function () { if (tipFor) showTip(tipFor); }, { passive: true });

  /* ---- えらぶ・置く ---- */
  function select(chip) {
    if (selected) selected.classList.remove("is-selected");
    selected = chip;
    game.classList.toggle("is-picking", !!chip);
    game.classList.toggle("is-ordering", !!(chip && chip.parentNode.hasAttribute("data-pool")));
    if (chip) {
      chip.classList.add("is-selected");
      showTip(chip);
      say(chip.parentNode.hasAttribute("data-pool")
        ? nameOf(chip) + "を選んだよ。並べたい「?」をタップしてね。"
        : nameOf(chip) + "を選んだよ。流派の箱の仮置き場をタップしてね。");
    } else {
      hideTip();
    }
  }

  function shake(chip) {
    chip.classList.remove("is-wrong");
    void chip.offsetWidth;
    chip.classList.add("is-wrong");
  }

  function wrongSchool(chip, box) {
    var name = nameOf(chip);
    miss++;
    missBy[name] = (missBy[name] || 0) + 1;
    shake(chip);
    if (missBy[name] >= 2) {
      var right = game.querySelector('[data-box="' + chip.getAttribute("data-school") + '"]');
      say("🌥️ おしい！ ヒント: " + name + "が見ているのは「" + right.querySelector(".rg-box__see").textContent + "」だよ。");
    } else {
      say("🌥️ おしい！ " + name + "は、" + schoolName(box) + "とはべつの流派の人みたい。吹き出しのひとことも見てみてね。");
    }
    update();
  }

  function settle() {
    selected = null;
    game.classList.remove("is-picking", "is-ordering");
    hideTip();
  }

  /* 仮置き場へ(流派だけを見る) */
  function toPool(chip, box) {
    if (!chip || chip.classList.contains("is-placed")) return;
    if (chip.parentNode === poolOf(box)) { select(null); return; }
    if (chip.getAttribute("data-school") !== box.getAttribute("data-box")) return wrongSchool(chip, box);
    poolOf(box).appendChild(chip);
    chip.classList.remove("is-selected", "is-wrong");
    settle();
    update();
    var p = poolCount(box);
    say(p.inPool + p.placed === p.total
      ? "☀️ " + schoolName(box) + "の" + p.total + "人がそろったよ！ 次は、上流から下流へ「?」に並べてみよう。"
      : "☀️ 正解！ " + nameOf(chip) + "は" + schoolName(box) + "。");
  }

  function poolCount(box) {
    var all = chips.filter(function (c) { return c.getAttribute("data-school") === box.getAttribute("data-box"); });
    return {
      total: all.length,
      inPool: poolOf(box).querySelectorAll("[data-chip]").length,
      placed: all.filter(function (c) { return c.classList.contains("is-placed"); }).length
    };
  }

  function revealNotes(box) {
    var opened = null;
    Array.prototype.forEach.call(box.querySelectorAll("[data-note]"), function (note) {
      if (!note.hidden) return;
      var t = note.getAttribute("data-note");
      var need = box.querySelectorAll('[data-tier="' + (t - 1) + '"][data-slot], [data-tier="' + t + '"][data-slot]');
      var ok = Array.prototype.every.call(need, function (s) { return s.classList.contains("is-filled"); });
      if (ok) { note.hidden = false; opened = note; }
    });
    return opened;
  }

  /* 「?」へ(流派と順番を見る) */
  function toSlot(chip, slot) {
    if (!chip || !slot || chip.classList.contains("is-placed")) return;
    var name = nameOf(chip);
    if (slot.classList.contains("is-filled")) {
      say("そこはもう埋まっているよ。ほかの「?」へどうぞ。");
      return;
    }
    if (chip.getAttribute("data-school") !== slot.getAttribute("data-school")) return wrongSchool(chip, boxOf(slot));
    var want = +chip.getAttribute("data-tier");
    var got = +slot.getAttribute("data-tier");
    if (want !== got) {
      miss++;
      shake(chip);
      if (!chip.parentNode.hasAttribute("data-pool")) poolOf(boxOf(slot)).appendChild(chip);
      say("🌤️ 流派は合ってる！ でも順番がちがうよ。" + name + "は、もっと" + (want < got ? "上流(左)" : "下流(右)") + "の人。");
      settle();
      update();
      return;
    }
    slot.innerHTML = "";
    slot.appendChild(chip);
    slot.classList.add("is-filled");
    slot.setAttribute("aria-label", schoolName(slot) + ": " + name);
    chip.classList.add("is-placed");
    chip.classList.remove("is-selected", "is-wrong");
    settle();
    placed++;
    var note = revealNotes(boxOf(slot));
    say(note ? "☀️ つながった！ " + note.textContent : "☀️ 正解！ " + name + "は、ここ。");
    update();
    if (placed === chips.length) finish();
  }

  function update() {
    leftEl.textContent = "のこり " + tray.querySelectorAll("[data-chip]").length + "人";
    missEl.textContent = "ミス " + miss;
    boxes.forEach(function (box) {
      var p = poolCount(box);
      box.querySelector("[data-pool-count]").textContent = (p.inPool + p.placed) + " / " + p.total + "人";
      box.classList.toggle("is-gathered", p.inPool + p.placed === p.total);
      box.classList.toggle("is-done", p.placed === p.total);
      poolOf(box).classList.toggle("has-chips", p.inPool > 0);
    });
    var empty = !tray.querySelector("[data-chip]");
    tray.classList.toggle("is-empty", empty);
    dock.classList.toggle("is-slim", empty);
  }

  function finish() {
    resultEl.textContent = "☀️ " + (miss === 0
      ? "ノーミス！ 理論の流れがしっかり頭に入っているね。"
      : "ミス" + miss + "回。下のまとめで、流れをもう一度たどってみよう。");
    dock.hidden = true;
    clearBox.hidden = false;
    setTimeout(function () { clearBox.scrollIntoView({ behavior: "smooth", block: "start" }); }, 600);
  }

  function start() {
    shuffle(chips.slice()).forEach(function (c) {
      c.classList.remove("is-placed", "is-selected", "is-wrong");
      tray.appendChild(c);
    });
    slots.forEach(function (s) {
      s.classList.remove("is-filled", "is-over");
      s.innerHTML = '<span class="rg-slot__empty">?</span>';
      s.setAttribute("aria-label", schoolName(s) + "の" + s.getAttribute("data-tier") + "番目に置く");
    });
    Array.prototype.forEach.call(game.querySelectorAll("[data-note]"), function (n) { n.hidden = true; });
    miss = 0; placed = 0; missBy = {};
    settle();
    dock.hidden = false;
    clearBox.hidden = true;
    update();
    say("まずは、知っている理論家から仮置き場へ入れてみよう。");
  }

  /* 置く先: 「?」が最優先、それ以外は箱のどこでも仮置き場あつかい */
  function dropTarget(el) {
    if (!el) return null;
    var slot = el.closest("[data-slot]");
    if (slot) return { slot: slot };
    var box = el.closest("[data-box]");
    return box ? { box: box } : null;
  }
  function dropTo(chip, t) {
    if (!t) return;
    if (t.slot) toSlot(chip, t.slot); else toPool(chip, t.box);
  }

  /* ---- タップ(クリック) ---- */
  var justDragged = false;
  game.addEventListener("click", function (e) {
    if (justDragged) return;
    var chip = e.target.closest("[data-chip]");
    if (chip && !chip.classList.contains("is-placed")) {
      // 別の人を選んでいる時に仮置き場の人をタップ → その箱へ入れる
      if (selected && selected !== chip && chip.parentNode.hasAttribute("data-pool") && !selected.parentNode.hasAttribute("data-pool")) {
        return toPool(selected, boxOf(chip));
      }
      select(selected === chip ? null : chip);
      return;
    }
    var t = dropTarget(e.target);
    if (!t) return;
    if (!selected) {
      if (t.slot && !t.slot.classList.contains("is-filled")) say("先に、仮置き場か上のカードから理論家を1人えらんでね。");
      return;
    }
    dropTo(selected, t);
  });

  /* ---- ドラッグ(マウス・タッチ共通) ----
     カードは touch-action: pan-x。横は置き場のスクロール、縦に動かすとドラッグ */
  var drag = null;
  var raf = 0;

  function autoScroll() {
    if (!drag || !drag.ghost) return;
    var y = drag.y;
    var top = dock.getBoundingClientRect().bottom;
    var dy = 0;
    if (y > window.innerHeight - 70) dy = 12;
    else if (drag.left && y < top + 50) dy = -12;
    if (dy) window.scrollBy(0, dy);
    raf = requestAnimationFrame(autoScroll);
  }

  game.addEventListener("pointerdown", function (e) {
    var chip = e.target.closest("[data-chip]");
    if (!chip || chip.classList.contains("is-placed") || e.button > 0) return;
    drag = { chip: chip, sx: e.clientX, sy: e.clientY, x: e.clientX, y: e.clientY, ghost: null, over: null, left: false, id: e.pointerId };
  });

  function mark(t) {
    var el = t ? (t.slot || poolOf(t.box)) : null;
    if (el && t.slot && t.slot.classList.contains("is-filled")) el = null;
    if (el !== drag.over) {
      if (drag.over) drag.over.classList.remove("is-over");
      if (el) el.classList.add("is-over");
      drag.over = el;
    }
    drag.target = t;
  }

  window.addEventListener("pointermove", function (e) {
    if (!drag || e.pointerId !== drag.id) return;
    drag.x = e.clientX; drag.y = e.clientY;
    if (!drag.ghost) {
      if (Math.abs(e.clientX - drag.sx) + Math.abs(e.clientY - drag.sy) < 8) return;
      var r = drag.chip.getBoundingClientRect();
      drag.dx = e.clientX - r.left; drag.dy = e.clientY - r.top;
      drag.ghost = drag.chip.cloneNode(true);
      drag.ghost.classList.add("rg-ghost");
      drag.ghost.classList.remove("is-selected");
      drag.ghost.removeAttribute("data-chip");
      drag.ghost.style.width = r.width + "px";
      document.body.appendChild(drag.ghost);
      drag.chip.classList.add("is-dragging");
      if (selected) selected.classList.remove("is-selected");
      selected = null;
      hideTip();
      game.classList.add("is-picking");
      game.classList.toggle("is-ordering", drag.chip.parentNode.hasAttribute("data-pool"));
      say(nameOf(drag.chip) + "を運んでいるよ。");
      raf = requestAnimationFrame(autoScroll);
    }
    e.preventDefault();
    drag.ghost.style.transform = "translate(" + (e.clientX - drag.dx) + "px," + (e.clientY - drag.dy) + "px)";
    if (e.clientY > dock.getBoundingClientRect().bottom + 50) drag.left = true;
    mark(dropTarget(document.elementFromPoint(e.clientX, e.clientY)));
  }, { passive: false });

  function endDrag(e, cancel) {
    if (!drag || (e && e.pointerId !== drag.id)) return;
    var d = drag;
    drag = null;
    cancelAnimationFrame(raf);
    if (!d.ghost) return;
    d.ghost.remove();
    d.chip.classList.remove("is-dragging");
    game.classList.remove("is-picking", "is-ordering");
    if (d.over) d.over.classList.remove("is-over");
    justDragged = true;
    setTimeout(function () { justDragged = false; }, 50);
    if (!cancel && d.target) dropTo(d.chip, d.target);
    else if (!cancel) say("流派の箱か「?」の上で手をはなすと置けるよ。");
  }
  window.addEventListener("pointerup", function (e) { endDrag(e, false); });
  window.addEventListener("pointercancel", function (e) { endDrag(e, true); });

  /* ヘッダーの下に置き場を貼りつける */
  function fitDock() {
    dock.style.top = (header && getComputedStyle(header).position === "sticky" ? header.offsetHeight : 0) + "px";
  }
  window.addEventListener("resize", fitDock);
  fitDock();

  game.querySelector("[data-retry]").addEventListener("click", function () {
    start();
    game.scrollIntoView({ behavior: "smooth", block: "start" });
  });
  start();
})();

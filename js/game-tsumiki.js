/* 傾聴のつみきブロック: 4つのタワーを、土台から順に積む
   - ブロックをタップすると、いちばん上に積まれる
   - 順番をまちがえると、タワーがくずれて、そのタワーをやり直し
   - 2つめからは、ほかの理論のブロック(ひっかけ)が1つまざっている */
(function () {
  "use strict";
  var game = document.getElementById("tsumiki-game");
  var dataEl = document.getElementById("tsumiki-data");
  if (!game || !dataEl) return;
  var STAGES = JSON.parse(dataEl.textContent);
  var BEST_KEY = "carepicnic-tsumiki-best";
  var $ = function (s) { return game.querySelector(s); };
  var stackEl = $("[data-ts-stack]");
  var bank = $("[data-ts-bank]");
  var msg = $("[data-ts-msg]");
  var clearBox = $("[data-ts-clear]");
  var goal = $("[data-ts-goal]");
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var stage = 0, placed = 0, locked = false, missAll = 0, missStage = 0, results = [];

  function shuffle(a) {
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }
  function say(t) { msg.innerHTML = t; }

  function steps() {
    var ol = $("[data-ts-steps]");
    ol.innerHTML = "";
    STAGES.forEach(function (s, i) {
      var li = document.createElement("li");
      li.className = i < stage ? "is-done" : i === stage ? "is-now" : "";
      var r = results[i];
      li.innerHTML = "<span>" + (i < stage ? (r && r.miss === 0 ? "⭐" : "✓") : i + 1) + "</span>";
      li.title = s.title;
      ol.appendChild(li);
    });
  }

  function width(level, total) {
    // 下ほど広く、上ほどせまく(ピラミッドの形)
    return 100 - (level / Math.max(total - 1, 1)) * 38;
  }

  function block(label, sub) {
    var b = document.createElement("button");
    b.type = "button";
    b.className = "tsx-block";
    b.innerHTML = '<b></b><span></span>';
    b.firstChild.textContent = label;
    b.lastChild.textContent = sub;
    return b;
  }

  function load(i) {
    stage = i; placed = 0; locked = false; missStage = 0;
    var s = STAGES[i];
    $("[data-ts-who]").textContent = (i + 1) + "つめ ・ " + s.who;
    $("[data-ts-title]").textContent = s.title;
    $("[data-ts-ask]").innerHTML = s.ask;
    stackEl.style.setProperty("--n", s.blocks.length);
    ghosts();
    clearBox.hidden = true;
    goal.hidden = true;
    bank.hidden = false;
    fillBank();
    steps();
    say("👇 土台にするブロックからタップしてね");
  }

  function fillBank() {
    var s = STAGES[stage];
    bank.innerHTML = "";
    var list = s.blocks.map(function (b, k) { return { label: b[0], sub: b[1], order: k }; });
    if (s.decoy) list.push({ label: s.decoy[0], sub: s.decoy[1], order: -1, why: s.decoy[2] });
    shuffle(list).forEach(function (it) {
      var b = block(it.label, it.sub);
      b.setAttribute("data-order", it.order);
      if (it.why) b.setAttribute("data-why", it.why);
      bank.appendChild(b);
    });
  }

  /* まだ積んでいない段を、うすい形で見せておく */
  function ghosts() {
    var n = STAGES[stage].blocks.length;
    stackEl.innerHTML = "";
    for (var k = 0; k < n; k++) {
      var g = document.createElement("div");
      g.className = "tsx-piece is-ghost";
      g.style.width = width(k, n) + "%";
      g.innerHTML = "<b>?</b>";
      stackEl.appendChild(g);
    }
  }

  function pile(label, sub, level, total) {
    var el = document.createElement("div");
    el.className = "tsx-piece tsx-piece--" + (level % 4);
    el.style.width = width(level, total) + "%";
    el.innerHTML = "<b></b><span></span>";
    el.firstChild.textContent = label;
    el.lastChild.textContent = sub;
    var ghost = stackEl.children[level];
    if (ghost && ghost.classList.contains("is-ghost")) stackEl.replaceChild(el, ghost); else stackEl.appendChild(el);
    return el;
  }

  bank.addEventListener("click", function (e) {
    var btn = e.target.closest(".tsx-block");
    if (!btn || locked || btn.disabled) return;
    var s = STAGES[stage];
    var order = +btn.getAttribute("data-order");
    var label = btn.firstChild.textContent;
    if (order === -1) {
      missAll++; missStage++;
      btn.disabled = true;
      btn.classList.add("is-out");
      say("🙅 ひっかけ！ " + btn.getAttribute("data-why") + " このタワーには入らないよ。");
      return;
    }
    var piece = pile(label, btn.lastChild.textContent, placed, s.blocks.length);
    btn.disabled = true;
    btn.classList.add("is-used");
    if (order === placed) {
      placed++;
      if (placed === s.blocks.length) return cleared();
      say(placed === 1 ? "☀️ そのとおり！ しっかりした土台ができたよ。次は？" : "☀️ いいね！ " + label + "がのった。次は？");
      return;
    }
    // 順番ちがい: グラグラ → くずれる
    missAll++; missStage++;
    locked = true;
    var right = s.blocks[placed][0];
    piece.classList.add("is-wrong");
    stackEl.classList.add("is-wobble");
    say("🌥️ わ〜！ ここに「" + label + "」をのせたら、グラグラ…" + (placed === 0 ? "土台にするのは、もっと下の段のブロックだよ。" : "「" + s.blocks[placed - 1][0] + "」のすぐ上にくるのは、ほかのブロックみたい。"));
    setTimeout(function () {
      stackEl.classList.remove("is-wobble");
      Array.prototype.forEach.call(stackEl.querySelectorAll(".tsx-piece:not(.is-ghost)"), function (p, k, all) {
        p.style.setProperty("--fx", (Math.random() * 160 - 80) + "px");
        p.style.setProperty("--fr", (Math.random() * 50 - 25) + "deg");
        p.style.animationDelay = (all.length - k) * 60 + "ms";
        p.classList.add("is-fall");
      });
    }, reduce ? 0 : 700);
    setTimeout(function () {
      ghosts();
      placed = 0;
      locked = false;
      Array.prototype.forEach.call(bank.children, function (b) {
        if (!b.classList.contains("is-out")) { b.disabled = false; b.classList.remove("is-used"); }
      });
      say("もう一回！ いちばん下に置くのはどれかな？ (ヒント: さっきは「" + right + "」を置く番だったよ)");
    }, reduce ? 300 : 1900);
  });

  function cleared() {
    var s = STAGES[stage];
    results[stage] = { miss: missStage };
    locked = true;
    bank.hidden = true;
    stackEl.classList.add("is-done");
    say("");
    $("[data-ts-clear-title]").textContent = (missStage === 0 ? "⭐ ノーミスで" : "🎉 ") + "「" + s.title + "」が建ったね！";
    $("[data-ts-clear-text]").innerHTML = s.clear;
    $("[data-ts-point]").innerHTML = s.point;
    var link = $("[data-ts-link]");
    link.href = s.link[0];
    link.innerHTML = s.link[1];
    $("[data-ts-next]").textContent = stage + 1 < STAGES.length ? "次のタワーへ →" : "結果を見る";
    clearBox.hidden = false;
    steps();
    setTimeout(function () { clearBox.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "nearest" }); }, 300);
  }

  $("[data-ts-next]").addEventListener("click", function () {
    stackEl.classList.remove("is-done");
    if (stage + 1 < STAGES.length) {
      load(stage + 1);
      game.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
    } else {
      finish();
    }
  });

  function finish() {
    clearBox.hidden = true;
    stage = STAGES.length;
    steps();
    var stars = results.filter(function (r) { return r.miss === 0; }).length;
    $("[data-ts-final]").textContent = "⭐ " + stars + " / " + STAGES.length + "(ノーミスのタワー) ・ ミス " + missAll + "回";
    var best = null;
    try { var v = localStorage.getItem(BEST_KEY); best = v === null ? null : +v; } catch (e) { /* 保存できない環境 */ }
    var bestEl = $("[data-ts-best]");
    if (best === null || missAll < best) {
      try { localStorage.setItem(BEST_KEY, String(missAll)); } catch (e) { /* 保存できない環境 */ }
      bestEl.textContent = best === null ? "🏅 きょうの記録を、自己ベストとして残したよ。" : "🏅 自己ベスト更新！(前回までのいちばん少ないミスは " + best + "回)";
    } else {
      bestEl.textContent = "これまでの自己ベスト: ミス " + best + "回";
    }
    var ul = $("[data-ts-recap]");
    ul.innerHTML = "";
    STAGES.forEach(function (s, i) {
      var li = document.createElement("li");
      li.innerHTML = "<b></b><span></span>";
      li.firstChild.textContent = (results[i].miss === 0 ? "⭐ " : "✓ ") + s.title;
      li.lastChild.textContent = s.blocks.map(function (b) { return b[0]; }).join(" → ");
      ul.appendChild(li);
    });
    $(".tsx__head").hidden = true;
    $(".tsx__stage").hidden = true;
    goal.hidden = false;
    goal.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "nearest" });
  }

  $("[data-ts-retry]").addEventListener("click", function () {
    missAll = 0; results = [];
    $(".tsx__head").hidden = false;
    $(".tsx__stage").hidden = false;
    load(0);
    game.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
  });

  load(0);
})();

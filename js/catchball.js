/* ことばのキャッチボール: モヤンとチャットで1球ずつやりとりする
   - 選択肢の並びは毎回入れかえる
   - まちがえたら、モヤンの反応とサニー先生の解説を見てから選び直せる
   - 1回目で正解すると「ナイスキャッチ」。こころの天気が晴れていく */
(function () {
  "use strict";
  var game = document.getElementById("cb-game");
  var dataEl = document.getElementById("cb-data");
  if (!game || !dataEl) return;
  var BALLS = JSON.parse(dataEl.textContent);
  var WEATHER = [["🌧️", "雨"], ["☁️", "くもり"], ["🌥️", "うす日"], ["🌤️", "晴れ間"], ["☀️", "晴れ"]];
  var FACE = "../../img/parts/07_moyan_school_hat_crying.png";
  var BEST_KEY = "carepicnic-catchball-best";

  var $ = function (s) { return game.querySelector(s); };
  var chat = $("[data-cb-chat]");
  var answer = $("[data-cb-answer]");
  var choicesEl = $("[data-cb-choices]");
  var coach = $("[data-cb-coach]");
  var nextBtn = $("[data-cb-next]");
  var goal = $("[data-cb-goal]");
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var ball, score, weather, missed, results;
  var touched = false; // 読みこんだ直後は、画面を勝手に動かさない

  function shuffle(a) {
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }
  function wait(ms) { return new Promise(function (r) { setTimeout(r, reduce ? 0 : ms); }); }

  function line(kind, htmlText) {
    var row = document.createElement("div");
    row.className = "cbx-line cbx-line--" + kind;
    if (kind === "moyan") {
      row.innerHTML = '<img class="cbx-line__face" src="' + FACE + '" width="40" height="40" alt=""><p class="cbx-line__bubble"><b class="cbx-line__who">モヤン</b></p>';
      row.querySelector(".cbx-line__bubble").insertAdjacentHTML("beforeend", htmlText);
    } else {
      row.innerHTML = '<p class="cbx-line__bubble"></p>';
      row.firstChild.innerHTML = htmlText;
    }
    chat.appendChild(row);
    return row;
  }

  /* モヤンが「…」と打ってから話す */
  function moyanSays(htmlText) {
    var typing = line("moyan", '<span class="cbx-typing" aria-label="入力中"><i></i><i></i><i></i></span>');
    keepInView(typing);
    return wait(700).then(function () {
      typing.remove();
      var row = line("moyan", htmlText);
      keepInView(row);
      return row;
    });
  }

  function keepInView(el) {
    if (!touched) return;
    var r = el.getBoundingClientRect();
    if (r.bottom > window.innerHeight - 90 || r.top < 120) {
      window.scrollBy({ top: r.bottom - window.innerHeight + 180, behavior: reduce ? "auto" : "smooth" });
    }
  }

  function setWeather(d) {
    weather = Math.max(0, Math.min(WEATHER.length - 1, weather + d));
    var el = $("[data-cb-weather]");
    el.textContent = WEATHER[weather][0];
    el.parentNode.title = "モヤンのこころの天気: " + WEATHER[weather][1];
    el.classList.remove("is-change");
    void el.offsetWidth;
    el.classList.add("is-change");
  }

  function bar() {
    $("[data-cb-no]").textContent = Math.min(ball + 1, BALLS.length) + "球目 / " + BALLS.length + "球";
    $("[data-cb-score]").textContent = String(score);
  }

  function play(i) {
    ball = i;
    missed = false;
    tried = [];
    bar();
    coach.hidden = true;
    answer.hidden = true;
    var b = BALLS[i];
    var p = Promise.resolve();
    if (b.scene) {
      p = p.then(function () { var s = line("scene", b.scene); keepInView(s); return wait(500); });
    }
    p.then(function () { return moyanSays(b.say); }).then(function () { showChoices(); });
  }

  function showChoices(skip) {
    var b = BALLS[ball];
    choicesEl.innerHTML = "";
    shuffle(b.choices.map(function (c, k) { return k; })).forEach(function (k) {
      var c = b.choices[k];
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "cbx__choice";
      btn.innerHTML = c.text;
      if (skip && skip.indexOf(k) >= 0) { btn.disabled = true; btn.classList.add("is-tried"); }
      btn.addEventListener("click", function () { choose(k); });
      choicesEl.appendChild(btn);
    });
    answer.hidden = false;
    keepInView(answer);
  }

  var tried = [];
  function choose(k) {
    touched = true;
    var b = BALLS[ball];
    var c = b.choices[k];
    answer.hidden = true;
    var mine = line("me", c.text);
    keepInView(mine);
    if (!c.ok) tried.push(k);
    wait(250).then(function () { return moyanSays(c.react); }).then(function (row) {
      if (!c.ok) {
        mine.classList.add("is-miss");
        row.classList.add("is-miss");
        if (!missed) { missed = true; setWeather(-1); }
      } else {
        if (!missed) { score++; setWeather(+1); }
        results.push({ say: b.say, text: c.text, giho: c.giho, first: !missed });
        tried = [];
      }
      bar();
      showCoach(c, b);
    });
  }

  function showCoach(c, b) {
    $("[data-cb-verdict]").textContent = c.ok
      ? (missed ? "☀️ そう、その返し方！" : "⚾ ナイスキャッチ！")
      : "🌥️ あっ、そらしちゃった…";
    $("[data-cb-verdict]").className = "cbx__verdict " + (c.ok ? "is-ok" : "is-ng");
    $("[data-cb-giho]").innerHTML = "この返し方は… <b></b>";
    $("[data-cb-giho] b").textContent = c.giho;
    $("[data-cb-why]").innerHTML = c.why;
    var a = $("[data-cb-link]");
    a.href = b.link;
    a.innerHTML = b.linkText + ' <span class="arw" aria-hidden="true">▶︎</span>';
    nextBtn.textContent = c.ok
      ? (ball + 1 < BALLS.length ? "つぎの球へ →" : "キャッチボールを終える")
      : "ほかの返し方を選び直す";
    nextBtn.setAttribute("data-mode", c.ok ? "next" : "retry");
    coach.hidden = false;
    keepInView(coach);
    nextBtn.focus({ preventScroll: true });
  }

  nextBtn.addEventListener("click", function () {
    coach.hidden = true;
    if (nextBtn.getAttribute("data-mode") === "retry") return showChoices(tried);
    if (ball + 1 < BALLS.length) play(ball + 1); else finish();
  });

  function finish() {
    answer.hidden = true;
    var n = BALLS.length;
    var rate = Math.round((score / n) * 100);
    $("[data-cb-final]").textContent = n + "球中 " + score + "球ナイスキャッチ ・ こころの天気 " + WEATHER[weather][0] + " " + WEATHER[weather][1];
    $("[data-cb-note]").textContent =
      rate === 100 ? "パーフェクト！ 面接対策の土台はバッチリだよ。"
      : rate >= 75 ? "いい調子！ そらした球の技法名だけ、用語ページで復習しておこう。"
      : rate >= 50 ? "半分キャッチできたね。「まず受けとめる」を合言葉に、もう一回投げ合ってみよう。"
      : "だいじょうぶ、最初はみんなアドバイスしたくなるもの。「受けとめてから質問」を意識してもう一回！";
    var best = 0;
    try { best = +localStorage.getItem(BEST_KEY) || 0; } catch (e) { /* 保存できない環境 */ }
    var bestEl = $("[data-cb-best]");
    if (score > best) {
      try { localStorage.setItem(BEST_KEY, String(score)); } catch (e) { /* 保存できない環境 */ }
      bestEl.textContent = best ? "🏅 自己ベスト更新！(前回までは " + best + "球)" : "🏅 きょうの記録 " + score + "球を、自己ベストとして残したよ。";
    } else {
      bestEl.textContent = "これまでの自己ベスト: " + best + "球";
    }
    var list = $("[data-cb-review]");
    list.innerHTML = "";
    results.forEach(function (r) {
      var li = document.createElement("li");
      li.className = r.first ? "is-ok" : "is-retry";
      li.innerHTML = '<p class="cbx__review-moyan"></p><p class="cbx__review-me"></p><p class="cbx__review-giho"></p>';
      li.children[0].innerHTML = "モヤン「" + r.say + "」";
      li.children[1].innerHTML = "→ " + r.text;
      li.children[2].textContent = (r.first ? "⚾ " : "↻ 選び直して正解 ・ ") + r.giho;
      list.appendChild(li);
    });
    goal.hidden = false;
    goal.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
  }

  function start() {
    chat.innerHTML = "";
    goal.hidden = true;
    score = 0;
    weather = 1;
    results = [];
    tried = [];
    setWeather(0);
    play(0);
  }

  /* ヘッダーの下にスコアの帯を貼りつける */
  function fitBar() {
    var h = document.querySelector(".site-header");
    game.style.setProperty("--cb-top", (h && getComputedStyle(h).position === "sticky" ? h.offsetHeight + 8 : 8) + "px");
  }
  window.addEventListener("resize", fitBar);
  fitBar();

  $("[data-cb-retry]").addEventListener("click", function () {
    start();
    game.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
  });
  start();
})();

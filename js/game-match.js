/* 理論家カードあわせ。
 * 全カードはHTMLに描画済み(hidden)。毎ラウンド6組を選んで表示し、
 * 理論家カードと理論カードのペアをそろえる。 */
(function () {
  var game = document.getElementById("match-game");
  if (!game) return;

  var PAIRS_PER_ROUND = 6;
  var theoristCol = game.querySelector('[data-col="theorist"]');
  var theoryCol = game.querySelector('[data-col="theory"]');
  var theoristCards = Array.prototype.slice.call(
    theoristCol.querySelectorAll(".match-card")
  );
  var theoryCards = Array.prototype.slice.call(
    theoryCol.querySelectorAll(".match-card")
  );
  var progressEl = game.querySelector("[data-match-progress]");
  var missEl = game.querySelector("[data-match-miss]");
  var feedbackEl = game.querySelector("[data-match-feedback]");
  var clearEl = game.querySelector("[data-match-clear]");
  var clearTextEl = game.querySelector("[data-match-clear-text]");

  var selected = { theorist: null, theory: null };
  var matched = 0;
  var miss = 0;
  var locked = false;

  var CHEERS = [
    "そのとおり!",
    "いいね、覚えてるね!",
    "すごい、正解!",
    "ばっちり!",
    "その調子!",
  ];
  var OOPS = [
    "あれ?ちがうみたい。もう一回!",
    "おしい!べつの組み合わせかも。",
    "だいじょうぶ、まちがいは覚えるチャンス!",
  ];

  function shuffle(arr) {
    var a = arr.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i];
      a[i] = a[j];
      a[j] = t;
    }
    return a;
  }

  function bySlug(cards, slug) {
    for (var i = 0; i < cards.length; i++) {
      if (cards[i].getAttribute("data-slug") === slug) return cards[i];
    }
    return null;
  }

  function startRound() {
    matched = 0;
    miss = 0;
    locked = false;
    selected.theorist = null;
    selected.theory = null;
    clearEl.hidden = true;
    feedbackEl.textContent = "";

    var slugs = shuffle(
      theoristCards.map(function (c) {
        return c.getAttribute("data-slug");
      })
    ).slice(0, PAIRS_PER_ROUND);

    theoristCards.concat(theoryCards).forEach(function (c) {
      c.hidden = true;
      c.classList.remove("is-selected", "is-matched", "is-wrong");
      c.disabled = false;
    });

    // 列ごとに別のシャッフル順で並べ直す
    shuffle(slugs).forEach(function (slug) {
      var c = bySlug(theoristCards, slug);
      c.hidden = false;
      theoristCol.appendChild(c);
    });
    shuffle(slugs).forEach(function (slug) {
      var c = bySlug(theoryCards, slug);
      c.hidden = false;
      theoryCol.appendChild(c);
    });

    updateStatus();
  }

  function updateStatus() {
    progressEl.textContent = matched + " / " + PAIRS_PER_ROUND;
    missEl.textContent = "ミス: " + miss;
  }

  function select(kind, card) {
    if (locked || card.classList.contains("is-matched")) return;
    if (selected[kind] === card) {
      card.classList.remove("is-selected");
      selected[kind] = null;
      return;
    }
    if (selected[kind]) selected[kind].classList.remove("is-selected");
    selected[kind] = card;
    card.classList.add("is-selected");
    if (selected.theorist && selected.theory) check();
  }

  function check() {
    var a = selected.theorist;
    var b = selected.theory;
    var ok = a.getAttribute("data-slug") === b.getAttribute("data-slug");
    locked = true;
    if (ok) {
      a.classList.remove("is-selected");
      b.classList.remove("is-selected");
      a.classList.add("is-matched");
      b.classList.add("is-matched");
      a.disabled = true;
      b.disabled = true;
      matched++;
      feedbackEl.textContent = "☀️ " + CHEERS[Math.floor(Math.random() * CHEERS.length)];
      selected.theorist = null;
      selected.theory = null;
      locked = false;
      updateStatus();
      if (matched === PAIRS_PER_ROUND) finish();
    } else {
      a.classList.add("is-wrong");
      b.classList.add("is-wrong");
      miss++;
      feedbackEl.textContent = "🌥️ " + OOPS[Math.floor(Math.random() * OOPS.length)];
      updateStatus();
      setTimeout(function () {
        a.classList.remove("is-selected", "is-wrong");
        b.classList.remove("is-selected", "is-wrong");
        selected.theorist = null;
        selected.theory = null;
        locked = false;
      }, 700);
    }
  }

  function finish() {
    var text;
    if (miss === 0) {
      text = "ノーミス!完璧だよ、テストでも大丈夫!";
    } else if (miss <= 2) {
      text = "ミス" + miss + "回。いい感じ!まちがえた組み合わせだけ、図鑑で見直そう。";
    } else {
      text = "ミス" + miss + "回。だいじょうぶ、くり返すほど強くなるよ。もう一回いってみよう!";
    }
    clearTextEl.textContent = "☀️ " + text;
    clearEl.hidden = false;
    clearEl.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  theoristCards.forEach(function (c) {
    c.addEventListener("click", function () {
      select("theorist", c);
    });
  });
  theoryCards.forEach(function (c) {
    c.addEventListener("click", function () {
      select("theory", c);
    });
  });
  game.querySelector("[data-match-restart]").addEventListener("click", startRound);
  game.querySelector("[data-match-again]").addEventListener("click", startRound);

  startRound();
})();

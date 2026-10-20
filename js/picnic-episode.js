/* 理論家とお弁当: 用語モーダル・一問一答・復習バスケット
 * ページ内の <script type="application/json" id="episode-data"> から
 * 用語(glossary)と問題(questions)を読み込む(データ駆動)。
 * 復習バスケットはこの端末のlocalStorageのみに保存する。 */
(function () {
  var dataEl = document.querySelector("#episode-data");
  if (!dataEl) return;
  var data = JSON.parse(dataEl.textContent);
  var glossary = data.glossary || {};
  var questions = data.questions || [];

  /* ---------- 用語モーダル ---------- */
  var modal = document.querySelector("#term-modal");

  function closeModal() {
    modal.classList.remove("open");
    document.body.style.overflow = "";
  }

  Array.prototype.forEach.call(
    document.querySelectorAll("[data-term]"),
    function (button) {
      button.addEventListener("click", function () {
        var item = glossary[button.dataset.term];
        if (!item) return;
        document.querySelector("#term-title").textContent = item.label;
        document.querySelector("#term-short").textContent = item.short;
        document.querySelector("#term-easy").textContent = item.easy;
        document.querySelector("#term-exam").textContent = item.exam;
        var link = document.querySelector("#term-link");
        if (link) link.href = item.url.replace(/^\//, "../../");
        modal.classList.add("open");
        document.body.style.overflow = "hidden";
      });
    }
  );

  document.querySelector("#close-modal").addEventListener("click", closeModal);
  document
    .querySelector("#back-to-picnic")
    .addEventListener("click", closeModal);
  modal.addEventListener("click", function (e) {
    if (e.target === modal) closeModal();
  });

  /* ---------- 会話アニメーション ----------
   * 2026-10-18 見直し: 「画面に何も出ていない」時間をなくす。
   * - 各ブロックの最初の3言は、はじめから表示する
   * - 残りは会話ブロックが画面に入ったら、1言ずつ「…」→本文(以前の半分の速さで待つ)
   * - 読む速さに追いつかないときは、画面の上の方まで来た言葉をすぐ出す。
   *   ブロックを通りすぎたら、残りをぜんぶ表示
   * - 会話をタップすると、残りを一気に表示(最初のブロックの上に小さな案内)
   * - reduced-motion環境やIntersectionObserverがない環境では動かさない(全文表示) */
  (function () {
    var reduced =
      window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduced || !("IntersectionObserver" in window)) return;

    var SHOW_FIRST = 3; // はじめから見せる言葉の数
    var TYPING_MS = 380; // 「…」を見せる時間
    var GAP_MS = 220; // 次の一言までの間
    var controllers = [];

    Array.prototype.forEach.call(
      document.querySelectorAll(".lines"),
      function (block, blockIndex) {
        var lines = Array.prototype.slice.call(
          block.querySelectorAll(".line")
        );
        if (!lines.length) return;
        var after = block.parentElement.querySelector(".dialogue-after");
        var hint = null;

        var index = Math.min(SHOW_FIRST, lines.length);
        lines.slice(0, index).forEach(function (line) {
          line.classList.add("is-visible");
        });
        if (index >= lines.length) return; // 全部はじめから見えている

        block.setAttribute("data-animate", "");
        if (after) after.classList.add("is-waiting");

        // 最初の会話ブロックにだけ「タップで ぜんぶ表示」の小さな案内
        if (!controllers.length) {
          hint = document.createElement("p");
          hint.className = "lines-hint";
          hint.textContent = "タップで ぜんぶ表示";
          block.parentElement.insertBefore(hint, block);
        }

        var timer = null;
        var started = false;
        var done = false;

        function reveal(line) {
          line.classList.add("is-visible");
          line.classList.remove("is-typing");
        }

        function finishAll() {
          if (done) return;
          done = true;
          if (timer) clearTimeout(timer);
          lines.forEach(reveal);
          if (after) after.classList.remove("is-waiting");
          if (hint) hint.classList.add("is-done");
        }

        function playNext() {
          if (done) return;
          if (index >= lines.length) {
            finishAll();
            return;
          }
          var line = lines[index];
          index++;
          line.classList.add("is-visible", "is-typing");
          timer = setTimeout(function () {
            line.classList.remove("is-typing");
            timer = setTimeout(playNext, GAP_MS);
          }, TYPING_MS);
        }

        // 読む人が先に進んでいたら、待たせずに出す
        function catchUp() {
          if (done) return;
          var vh = window.innerHeight || document.documentElement.clientHeight;
          var rect = block.getBoundingClientRect();
          if (rect.bottom < 0 || (after && after.getBoundingClientRect().top < vh * 0.85)) {
            finishAll(); // ブロックを通りすぎた/会話の下まで来た
            return;
          }
          if (!started) return;
          while (index < lines.length && lines[index].getBoundingClientRect().top < vh * 0.6) {
            if (timer) clearTimeout(timer);
            timer = null;
            reveal(lines[index]);
            if (index > 0) reveal(lines[index - 1]);
            index++;
          }
          if (index >= lines.length) finishAll();
          else if (!timer) timer = setTimeout(playNext, GAP_MS);
        }

        // 途中で待ちたくない人のために、会話タップで全部表示
        block.addEventListener("click", function (e) {
          if (e.target.closest && e.target.closest("[data-term]")) return;
          finishAll();
        });
        if (hint) hint.addEventListener("click", finishAll);

        var observer = new IntersectionObserver(
          function (entries) {
            entries.forEach(function (entry) {
              if (entry.isIntersecting && !started) {
                started = true;
                observer.disconnect();
                playNext();
                catchUp();
              }
            });
          },
          { threshold: 0, rootMargin: "0px 0px -20% 0px" }
        );
        observer.observe(block);
        controllers.push(catchUp);
      }
    );

    if (!controllers.length) return;
    var ticking = false;
    function onScroll() {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(function () {
        ticking = false;
        controllers.forEach(function (fn) {
          fn();
        });
      });
    }
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll, { passive: true });
    // ページ内リンク(#story など)でとんできた時にも追いつく
    onScroll();
  })();

  /* ---------- 復習バスケット(端末内のみ) ---------- */
  var storageKey = "career-picnic-review-basket";
  var basket = [];
  try {
    basket = JSON.parse(localStorage.getItem(storageKey) || "[]");
  } catch (_e) {
    basket = [];
  }
  // 旧形式(id文字列の配列)を新形式({id, text})へそろえる
  basket = basket
    .map(function (item) {
      if (typeof item === "string") {
        var q = questions.find(function (x) {
          return x.id === item;
        });
        return q ? { id: q.id, text: q.text } : null;
      }
      return item && item.id ? item : null;
    })
    .filter(Boolean);

  function saveBasket() {
    localStorage.setItem(storageKey, JSON.stringify(basket));
  }

  function renderBasket() {
    var list = document.querySelector("#basket-list");
    var emptyMsg = document.querySelector("#basket-empty");
    var clear = document.querySelector("#clear-basket");
    list.innerHTML = "";
    basket.forEach(function (item) {
      var li = document.createElement("li");
      li.textContent = item.text;
      list.appendChild(li);
    });
    emptyMsg.hidden = basket.length > 0;
    clear.hidden = basket.length === 0;
  }
  renderBasket();

  document.querySelector("#clear-basket").addEventListener("click", function () {
    basket = [];
    localStorage.removeItem(storageKey);
    renderBasket();
  });

  function addToBasket(q) {
    var exists = basket.some(function (item) {
      return item.id === q.id;
    });
    if (!exists) basket.push({ id: q.id, text: q.text });
  }

  function removeFromBasket(id) {
    basket = basket.filter(function (item) {
      return item.id !== id;
    });
  }

  /* ---------- 一問一答 ----------
   * 2026-10-18: 答えたら「正解！/ざんねん」と正しい答えをはっきり出す。
   * 最後に「N問中M問 正解」と「もう一回」ボタン */
  var current = 0;
  var score = 0;
  var quiz = document.querySelector("#quiz");
  var next = document.querySelector("#next-question");
  var feedback = document.querySelector("#feedback");
  var restart = document.createElement("button");
  restart.type = "button";
  restart.className = "primary quiz-restart";
  restart.id = "restart-quiz";
  restart.textContent = "もう一回";
  restart.hidden = true;
  next.parentNode.insertBefore(restart, next.nextSibling);

  function setFeedback(ok, q) {
    feedback.innerHTML = "";
    feedback.className = "feedback " + (ok ? "is-correct" : "is-wrong");
    var label = document.createElement("span");
    label.className = "feedback__label";
    label.textContent = ok ? "正解！" : "ざんねん";
    feedback.appendChild(label);
    var answer = document.createElement("span");
    answer.className = "feedback__answer";
    answer.textContent =
      "正解は「" + (q.answer + 1) + ". " + q.choices[q.answer] + "」";
    feedback.appendChild(answer);
    var note = document.createElement("span");
    note.className = "feedback__note";
    note.textContent =
      (ok ? "晴れ間が見えたね。" : "いまは小さな雨。ここが次の「わかった」になるよ。") +
      (q.explanation || "");
    feedback.appendChild(note);
  }

  function showQuestion() {
    var q = questions[current];
    document.querySelector("#question-count").textContent =
      current + 1 + " / " + questions.length + " 問";
    document.querySelector("#question-text").textContent = q.text;
    document.querySelector("#progress-bar").style.width =
      (current / questions.length) * 100 + "%";
    feedback.textContent = "";
    feedback.className = "feedback";
    next.hidden = true;
    restart.hidden = true;
    var box = document.querySelector("#choices");
    box.innerHTML = "";
    q.choices.forEach(function (label, index) {
      var button = document.createElement("button");
      button.className = "choice";
      button.textContent = index + 1 + ". " + label;
      button.addEventListener("click", function () {
        Array.prototype.forEach.call(
          box.querySelectorAll("button"),
          function (x) {
            x.disabled = true;
          }
        );
        var ok = index === q.answer;
        if (ok) {
          score++;
          button.classList.add("correct");
          removeFromBasket(q.id);
        } else {
          button.classList.add("wrong");
          box.children[q.answer].classList.add("correct");
          addToBasket(q);
        }
        setFeedback(ok, q);
        saveBasket();
        renderBasket();
        next.textContent =
          current + 1 < questions.length ? "次のタネへ" : "結果を見る";
        next.hidden = false;
      });
      box.appendChild(button);
    });
  }

  function startQuiz() {
    current = 0;
    score = 0;
    quiz.classList.add("active");
    showQuestion();
  }

  document.querySelector("#start-quiz").addEventListener("click", function (e) {
    e.currentTarget.hidden = true;
    startQuiz();
  });

  restart.addEventListener("click", function () {
    startQuiz();
    var text = document.querySelector("#question-text");
    if (quiz.scrollIntoView) quiz.scrollIntoView({ block: "start" });
    if (text) {
      text.setAttribute("tabindex", "-1");
      text.focus({ preventScroll: true });
    }
  });

  next.addEventListener("click", function () {
    current++;
    if (current < questions.length) {
      showQuestion();
    } else {
      document.querySelector("#progress-bar").style.width = "100%";
      document.querySelector("#question-count").textContent = "おしまい";
      document.querySelector("#question-text").textContent =
        questions.length + "問中" + score + "問 正解";
      document.querySelector("#choices").innerHTML = "";
      feedback.className = "feedback feedback--result";
      feedback.textContent =
        score === questions.length
          ? "ぜんぶに晴れ間が見えました。今日のことばのタネを、持ち帰れました。"
          : "雨のしずくは復習バスケットへ。また晴れ間を見つけに来てね。";
      next.hidden = true;
      restart.hidden = false;
    }
  });
})();

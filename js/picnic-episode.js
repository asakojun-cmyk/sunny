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
        if (link) link.href = item.url;
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
   * 会話ブロックが画面に入ったら、1言ずつ「…」→本文の順で表示する。
   * クリックで残りを一気に表示。reduced-motion環境では動かさない。 */
  (function () {
    var reduced =
      window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduced || !("IntersectionObserver" in window)) return;

    var TYPING_MS = 750; // 「…」を見せる時間
    var GAP_MS = 420; // 次の一言までの間

    Array.prototype.forEach.call(
      document.querySelectorAll(".lines"),
      function (block) {
        var lines = Array.prototype.slice.call(
          block.querySelectorAll(".line")
        );
        if (!lines.length) return;
        var after = block.parentElement.querySelector(".dialogue-after");
        block.setAttribute("data-animate", "");
        if (after) after.classList.add("is-waiting");

        var index = 0;
        var timer = null;
        var done = false;

        function finishAll() {
          if (done) return;
          done = true;
          if (timer) clearTimeout(timer);
          lines.forEach(function (line) {
            line.classList.add("is-visible");
            line.classList.remove("is-typing");
          });
          if (after) after.classList.remove("is-waiting");
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

        // 途中で待ちたくない人のために、会話クリックで全部表示
        block.addEventListener("click", function (e) {
          if (e.target.closest && e.target.closest("[data-term]")) return;
          finishAll();
        });

        var observer = new IntersectionObserver(
          function (entries) {
            entries.forEach(function (entry) {
              if (entry.isIntersecting) {
                observer.disconnect();
                playNext();
              }
            });
          },
          { threshold: 0.35 }
        );
        observer.observe(block);
      }
    );
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

  /* ---------- 一問一答 ---------- */
  var current = 0;
  var quiz = document.querySelector("#quiz");
  var next = document.querySelector("#next-question");

  function showQuestion() {
    var q = questions[current];
    document.querySelector("#question-count").textContent =
      current + 1 + " / " + questions.length + " 問";
    document.querySelector("#question-text").textContent = q.text;
    document.querySelector("#progress-bar").style.width =
      (current / questions.length) * 100 + "%";
    document.querySelector("#feedback").textContent = "";
    next.hidden = true;
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
        if (index === q.answer) {
          button.classList.add("correct");
          document.querySelector("#feedback").textContent =
            "晴れ間が見えたね。" + q.explanation;
          removeFromBasket(q.id);
        } else {
          button.classList.add("wrong");
          box.children[q.answer].classList.add("correct");
          document.querySelector("#feedback").textContent =
            "いまは小さな雨。ここが次の「わかった」になるよ。" + q.explanation;
          addToBasket(q);
        }
        saveBasket();
        renderBasket();
        next.hidden = false;
      });
      box.appendChild(button);
    });
  }

  document.querySelector("#start-quiz").addEventListener("click", function (e) {
    e.currentTarget.hidden = true;
    quiz.classList.add("active");
    showQuestion();
  });

  next.addEventListener("click", function () {
    current++;
    if (current < questions.length) {
      showQuestion();
    } else {
      document.querySelector("#progress-bar").style.width = "100%";
      document.querySelector("#question-count").textContent = "おしまい";
      document.querySelector("#question-text").textContent =
        "今日のことばのタネを、持ち帰れました。";
      document.querySelector("#choices").innerHTML = "";
      document.querySelector("#feedback").textContent = basket.length
        ? "雨のしずくは復習バスケットへ。また晴れ間を見つけに来てね。"
        : "ぜんぶに晴れ間が見えました。";
      next.hidden = true;
    }
  });
})();

/* お守りページ: 試験日カウントダウン + 学習チェック(この端末のみに保存) */
(function () {
  var root = document.getElementById("omamori-countdown");
  if (!root) return;

  var KEY_DATE = "kotoba-exam-date";
  var KEY_CHECKS = "kotoba-omamori-checks";

  function load(key) {
    try {
      return localStorage.getItem(key);
    } catch (_e) {
      return null;
    }
  }
  function save(key, val) {
    try {
      localStorage.setItem(key, val);
    } catch (_e) {
      /* プライベートブラウズ等では保存されない */
    }
  }

  /* ---------- カウントダウン ---------- */
  var input = document.getElementById("exam-date");
  var saveBtn = root.querySelector("[data-date-save]");
  var daysWrap = root.querySelector("[data-days-display]");
  var daysNum = root.querySelector("[data-days-num]");
  var cheer = root.querySelector("[data-cheer]");
  var focus = root.querySelector("[data-focus]");

  function render() {
    var v = load(KEY_DATE);
    if (!v) {
      cheer.textContent = "試験日を入れると、あと何日かがいつでも見られるよ。";
      return;
    }
    input.value = v;
    var today = new Date();
    today.setHours(0, 0, 0, 0);
    var exam = new Date(v + "T00:00:00");
    var days = Math.round((exam - today) / 86400000);
    daysWrap.hidden = false;
    focus.hidden = true;

    if (days > 1) {
      daysNum.textContent = "あと " + days + " 日";
    } else if (days === 1) {
      daysNum.textContent = "あした!";
    } else if (days === 0) {
      daysNum.textContent = "きょう!";
    } else {
      daysNum.textContent = "おつかれさま!";
    }

    if (days < 0) {
      cheer.textContent = "☀️ 試験、本当におつかれさま。どんな結果でも、ここまでの学びはぜんぶあなたの力になっているよ。";
    } else if (days === 0) {
      cheer.textContent = "☀️ いってらっしゃい!深呼吸して、いつものあなたで大丈夫。";
    } else if (days <= 21) {
      cheer.textContent = "☀️ ここまできたら、あとは、うかるだけ。新しいことより「見直し」の時期だよ。";
      focus.hidden = false;
    } else if (days <= 60) {
      cheer.textContent = "🌤️ いいペース。過去問と用語の行き来をくり返そう。わからない言葉はすぐ検索!";
    } else {
      cheer.textContent = "⛅ まだ時間はたっぷり。1日ひとつ、ことばと仲良くなるところから始めよう。";
    }
  }

  saveBtn.addEventListener("click", function () {
    if (!input.value) return;
    save(KEY_DATE, input.value);
    render();
  });
  input.addEventListener("change", function () {
    if (!input.value) return;
    save(KEY_DATE, input.value);
    render();
  });

  /* ---------- チェックリスト ---------- */
  var boxes = Array.prototype.slice.call(
    document.querySelectorAll("[data-check]")
  );
  var fill = document.querySelector("[data-progress-fill]");
  var label = document.querySelector("[data-progress-label]");

  function loadChecks() {
    try {
      return JSON.parse(load(KEY_CHECKS) || "[]");
    } catch (_e) {
      return [];
    }
  }

  function renderChecks() {
    var done = boxes.filter(function (b) {
      return b.checked;
    }).length;
    var pct = boxes.length ? Math.round((done / boxes.length) * 100) : 0;
    fill.style.width = pct + "%";
    label.textContent = done + " / " + boxes.length;
  }

  var saved = loadChecks();
  boxes.forEach(function (b) {
    if (saved.indexOf(b.getAttribute("data-check")) !== -1) b.checked = true;
    b.addEventListener("change", function () {
      var ids = boxes
        .filter(function (x) {
          return x.checked;
        })
        .map(function (x) {
          return x.getAttribute("data-check");
        });
      save(KEY_CHECKS, JSON.stringify(ids));
      renderChecks();
    });
  });

  render();
  renderChecks();
})();

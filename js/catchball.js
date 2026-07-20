/* ことばのキャッチボール: 1球ずつ応答を選ぶ */
(function () {
  "use strict";
  var rallies = [].slice.call(document.querySelectorAll("[data-cb-rally]"));
  var goal = document.querySelector("[data-cb-goal]");
  if (!rallies.length) return;

  var score = 0;
  var done = 0;
  var scoreEl = document.querySelector("[data-cb-score]");
  var doneEl = document.querySelector("[data-cb-done]");

  function next(i) {
    if (i < rallies.length) {
      rallies[i].classList.remove("is-locked");
      rallies[i].scrollIntoView({ behavior: "smooth", block: "start" });
    } else if (goal) {
      goal.hidden = false;
      var rate = Math.round((score / rallies.length) * 100);
      document.querySelector("[data-cb-final]").textContent =
        rallies.length + "球中 " + score + "球ナイスキャッチ(" + rate + "%)";
      document.querySelector("[data-cb-note]").textContent =
        rate === 100 ? "パーフェクト! 面接対策の土台はバッチリだよ。"
        : rate >= 75 ? "いい調子! まちがえた球の技法名だけ、用語ページで復習しておこう。"
        : rate >= 50 ? "半分キャッチできたね。「まず受けとめる」を合言葉に、もう一回投げ合ってみよう。"
        : "だいじょうぶ、最初はみんなアドバイスしたくなるもの。「受けとめてから質問」を意識してもう一回!";
      goal.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  rallies.forEach(function (r, i) {
    var answered = false;
    r.querySelectorAll("[data-cb-choice]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        if (r.classList.contains("is-locked") || answered) return;
        answered = true;
        var ok = btn.getAttribute("data-ok") === "true";
        if (ok) score++;
        done++;
        if (scoreEl) scoreEl.textContent = String(score);
        if (doneEl) doneEl.textContent = String(done);
        r.querySelectorAll("[data-cb-choice]").forEach(function (b) {
          b.disabled = true;
          if (b.getAttribute("data-ok") === "true") b.classList.add("is-correct");
        });
        if (!ok) btn.classList.add("is-wrong");
        r.querySelector("[data-cb-verdict]").textContent = ok
          ? "⚾ ナイスキャッチ!"
          : "🌥️ あっ、そらしちゃった! 正解の返し方は色がついているよ";
        r.querySelector("[data-cb-verdict]").className =
          "cb-feedback__verdict " + (ok ? "is-ok" : "is-ng");
        r.querySelector("[data-cb-giho]").textContent = btn.getAttribute("data-giho") || "";
        r.querySelector("[data-cb-why]").textContent = btn.getAttribute("data-why") || "";
        r.querySelector("[data-cb-feedback]").hidden = false;
      });
    });
    r.querySelectorAll("[data-cb-next]").forEach(function (btn) {
      btn.addEventListener("click", function () { next(i + 1); });
    });
  });

  var retry = document.querySelector("[data-cb-retry]");
  if (retry) {
    retry.addEventListener("click", function () { window.location.reload(); });
  }
})();

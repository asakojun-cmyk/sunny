/* 今日の3分学習 — 日付に応じて登録済みデータをローテーション表示 */
(function () {
  "use strict";

  function dayIndex(length) {
    var days = Math.floor(Date.now() / 86400000);
    return length > 0 ? days % length : 0;
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      }[c];
    });
  }

  document.querySelectorAll("[data-daily]").forEach(function (card) {
    var items;
    try {
      items = JSON.parse(card.getAttribute("data-items") || "[]");
    } catch (_e) {
      return;
    }
    if (!items.length) return;
    var fixed = card.getAttribute("data-fixed-index");
    var idx = fixed !== null ? Number(fixed) % items.length : dayIndex(items.length);
    var item = items[idx];
    var body = card.querySelector("[data-daily-body]");
    if (!body || !item) return;

    var kind = card.getAttribute("data-daily");
    if (kind === "quiz") {
      body.innerHTML =
        '<p class="daily-card__question">' +
        escapeHtml(item.question) +
        "</p>" +
        '<div class="daily-card__quiz-actions">' +
        '<button type="button" class="button button--ghost" data-quiz-answer="true">○</button>' +
        '<button type="button" class="button button--ghost" data-quiz-answer="false">×</button>' +
        "</div>" +
        '<p class="daily-card__result" data-quiz-result hidden></p>';
      var result = body.querySelector("[data-quiz-result]");
      body.querySelectorAll("[data-quiz-answer]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          var chosen = btn.getAttribute("data-quiz-answer") === "true";
          var prefix = chosen === item.answer ? "正解です。" : "おしい!";
          result.innerHTML =
            escapeHtml(prefix + " " + item.explanation) +
            ' <a href="' +
            escapeHtml(item.url) +
            '">「' +
            escapeHtml(item.termName) +
            "」の解説を読む →</a>";
          result.hidden = false;
        });
      });
    } else {
      body.innerHTML =
        '<p class="daily-card__title"><a href="' +
        escapeHtml(item.url) +
        '">' +
        escapeHtml(item.name) +
        "</a></p>" +
        '<p class="daily-card__desc">' +
        escapeHtml(item.oneLiner) +
        "</p>";
    }
  });
})();

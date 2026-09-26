/* 「あなたは目指すべき?」診断 — 記事内の判定軸をそのまま使う簡易セルフチェック */
(function () {
  "use strict";
  var root = document.querySelector("[data-shindan]");
  if (!root) return;

  var form = root.querySelector("[data-shindan-form]");
  var resultBox = root.querySelector("[data-shindan-result]");
  var submitBtn = root.querySelector("[data-shindan-submit]");
  var retryBtn = root.querySelector("[data-shindan-retry]");
  var progress = root.querySelector("[data-shindan-progress]");
  var qs = [].slice.call(root.querySelectorAll("[data-shindan-q]"));
  var total = qs.length;

  function answered() {
    return qs.filter(function (q) {
      return !!q.querySelector("input:checked");
    }).length;
  }

  function updateProgress() {
    var n = answered();
    if (progress) progress.textContent = n + " / " + total;
    if (submitBtn) submitBtn.disabled = n < total;
  }

  root.addEventListener("change", function (e) {
    if (e.target && e.target.name && e.target.name.indexOf("sd-") === 0) updateProgress();
  });

  var RESULTS = {
    a: {
      label: "🌞 いま申し込んでも、たぶん無駄になりません",
      body: "使う場所が具体的で、学ぶ時間と維持のコストも織り込めています。この資格でいちばん失敗しやすいのは「取ってから考える」順番ですが、あなたはその逆になっています。次は費用の実額と、学校ごとの違いを確かめる段階です。",
      cls: "is-go"
    },
    b: {
      label: "🌤️ 方向は合っています。決めていないことが残っています",
      body: "向いていない、という結果ではありません。ただ「どこで使うか」「時間をどこに入れるか」のどちらかが、まだ言葉になっていないようです。ここが空いたまま申し込むと、講習の途中でしんどくなります。先に埋めてから進むほうが、結果的に早いです。",
      cls: "is-hold"
    },
    c: {
      label: "🌥️ いまは、やめておいたほうがいいかもしれません",
      body: "この資格には独占業務がなく、取っただけでは仕事につながりません。5年ごとの更新も続きます。いまの答えだと、35〜50万円と150時間に見合うものが返ってこない可能性が高いです。やめるというより、「使う場面が見えてから、また来てください」という意味に受け取ってもらえたらうれしいです。",
      cls: "is-stop"
    }
  };

  function judge() {
    var v = {};
    qs.forEach(function (q) {
      var c = q.querySelector("input:checked");
      if (c) v[c.name] = c.value;
    });
    // 1問でも「決定的に向かない」に当たったら c
    if (v["sd-use"] === "none" || v["sd-solo"] === "yes" || v["sd-escape"] === "yes") return "c";
    // 時間か更新に不安が残るなら b
    if (v["sd-time"] === "no" || v["sd-renew"] === "no" || v["sd-listen"] === "no") return "b";
    return "a";
  }

  if (submitBtn) {
    submitBtn.addEventListener("click", function () {
      var key = judge();
      var r = RESULTS[key];
      resultBox.className = "shindan__result " + r.cls;
      resultBox.querySelector("[data-shindan-label]").textContent = r.label;
      resultBox.querySelector("[data-shindan-body]").textContent = r.body;
      resultBox.hidden = false;
      resultBox.setAttribute("tabindex", "-1");
      resultBox.focus({ preventScroll: true });
      resultBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
    });
  }

  if (retryBtn) {
    retryBtn.addEventListener("click", function () {
      if (form) form.reset();
      resultBox.hidden = true;
      updateProgress();
      root.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }

  updateProgress();
})();

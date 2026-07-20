/* 論述ボードゲーム: マスを1つずつ進む */
(function () {
  "use strict";
  var stations = [].slice.call(document.querySelectorAll("[data-ron-station]"));
  var goal = document.querySelector("[data-ron-goal]");
  var nowEl = document.querySelector("[data-ron-now]");
  if (!stations.length) return;

  function unlock(i) {
    if (i < stations.length) {
      stations[i].classList.remove("is-locked");
      if (nowEl) nowEl.textContent = String(i + 1);
      stations[i].scrollIntoView({ behavior: "smooth", block: "start" });
    } else if (goal) {
      goal.hidden = false;
      if (nowEl) nowEl.textContent = String(stations.length);
      goal.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  stations.forEach(function (st, i) {
    // 選択式
    st.querySelectorAll("[data-ron-choice]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        if (st.classList.contains("is-locked")) return;
        var ok = btn.getAttribute("data-ok") === "true";
        var fb = st.querySelector("[data-ron-feedback]");
        st.querySelector("[data-ron-verdict]").textContent = ok
          ? "🌞 ナイス! その読み方でOK!"
          : "🌥️ おしい! もう一度考えてみよう";
        st.querySelector("[data-ron-verdict]").className =
          "ron-feedback__verdict " + (ok ? "is-ok" : "is-ng");
        st.querySelector("[data-ron-why]").textContent = btn.getAttribute("data-why") || "";
        fb.hidden = false;
        var nextBtn = st.querySelector("[data-ron-next]");
        if (nextBtn) nextBtn.hidden = !ok; // 正解したら次へ進める
        btn.classList.add(ok ? "is-correct" : "is-wrong");
        if (ok) {
          st.querySelectorAll("[data-ron-choice]").forEach(function (b) { b.disabled = true; });
          st.classList.add("is-clear");
        }
      });
    });
    // 書く練習
    var reveal = st.querySelector("[data-ron-reveal]");
    if (reveal) {
      reveal.addEventListener("click", function () {
        st.querySelector("[data-ron-model]").hidden = false;
        reveal.hidden = true;
      });
    }
    // 次のマスへ
    st.querySelectorAll("[data-ron-next]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        unlock(i + 1);
      });
    });
  });

  var retry = document.querySelector("[data-ron-retry]");
  if (retry) {
    retry.addEventListener("click", function () {
      window.location.reload();
    });
  }
})();

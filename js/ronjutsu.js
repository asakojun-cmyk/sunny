/* 論述ボードゲーム: すごろくの盤の上を、マスを1つずつ進む
   - 上の盤に、いまいるマスとクリアしたマスを出す(クリアしたマスを押すとそこへ戻れる)
   - まだのマスは出さない(ぼかしで並べると、ページが長くなるため)
   - 「事例を見る」で、逐語記録をいつでも見直せる */
(function () {
  "use strict";
  var stations = [].slice.call(document.querySelectorAll("[data-ron-station]"));
  var goal = document.querySelector("[data-ron-goal]");
  var nowEl = document.querySelector("[data-ron-now]");
  var rb = document.querySelector("[data-rb]");
  if (!stations.length) return;
  var squares = rb ? [].slice.call(rb.querySelectorAll("[data-rb-sq]")) : [];
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var now = 0;

  function board() {
    squares.forEach(function (sq, i) {
      sq.classList.toggle("is-done", i < now);
      sq.classList.toggle("is-now", i === now);
      sq.querySelector("button").disabled = i > now;
    });
    var g = rb && rb.querySelector("[data-rb-goal]");
    if (g) g.classList.toggle("is-now", now >= stations.length);
    if (nowEl) nowEl.textContent = String(Math.min(now + 1, stations.length));
  }

  function go(el) {
    var top = rb ? rb.getBoundingClientRect().height + 90 : 90;
    var y = el.getBoundingClientRect().top + window.scrollY - top;
    window.scrollTo({ top: y, behavior: reduce ? "auto" : "smooth" });
  }

  function unlock(i) {
    now = i;
    if (i < stations.length) {
      stations[i].classList.remove("is-locked");
      board();
      go(stations[i]);
    } else if (goal) {
      board();
      goal.hidden = false;
      go(goal);
    }
  }

  squares.forEach(function (sq, i) {
    sq.querySelector("button").addEventListener("click", function () {
      if (i <= now && stations[i]) go(stations[i]);
    });
  });

  stations.forEach(function (st, i) {
    // 選択式
    st.querySelectorAll("[data-ron-choice]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        if (st.classList.contains("is-locked")) return;
        var ok = btn.getAttribute("data-ok") === "true";
        var fb = st.querySelector("[data-ron-feedback]");
        st.querySelector("[data-ron-verdict]").textContent = ok
          ? "🌞 ナイス！ その読み方でOK!"
          : "🌥️ おしい！ もう一度考えてみよう";
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
        if (now === i) unlock(i + 1); else go(stations[now] || goal);
      });
    });
  });

  /* 事例(逐語記録)をいつでも見直せるように */
  var caseBtn = rb && rb.querySelector("[data-rb-case]");
  var sheet = rb && rb.querySelector("[data-rb-sheet]");
  var source = document.querySelector(".ron-case");
  if (caseBtn && sheet && source) {
    var copy = source.cloneNode(true);
    copy.removeAttribute("id");
    copy.className = "rb__case-copy";
    sheet.appendChild(copy);
    caseBtn.addEventListener("click", function () {
      sheet.hidden = !sheet.hidden;
      caseBtn.setAttribute("aria-expanded", String(!sheet.hidden));
      caseBtn.textContent = sheet.hidden ? "📄 事例を見る" : "✕ 事例をとじる";
    });
  }

  /* ヘッダーの下に盤を貼りつける */
  function fit() {
    var h = document.querySelector(".site-header");
    if (rb) rb.style.top = (h && getComputedStyle(h).position === "sticky" ? h.offsetHeight + 6 : 6) + "px";
  }
  window.addEventListener("resize", fit);
  fit();
  board();

  var retry = document.querySelector("[data-ron-retry]");
  if (retry) {
    retry.addEventListener("click", function () {
      window.location.reload();
    });
  }
})();

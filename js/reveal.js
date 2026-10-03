/* 広告リンク(A8)が押された場所をGA4に記録する。イベント名: aff_<学校>_<場所> */
(function () {
  "use strict";
  var SCHOOLS = {
    "459JRK+G3ASDU": "chiiki",
    "4B7XX4+BD0U56": "pasona",
    "45BQMV+6WV8EY": "manpower"
  };
  document.addEventListener(
    "click",
    function (e) {
      var a = e.target && e.target.closest ? e.target.closest('a[href*="px.a8.net"]') : null;
      if (!a || typeof window.gtag !== "function") return;
      var m = a.href.match(/a8mat=([A-Z0-9]+\+[A-Z0-9]+)/);
      var school = (m && SCHOOLS[m[1]]) || "other";
      var pos = a.closest(".school-header")
        ? "top"
        : a.closest("table")
        ? "table"
        : a.classList.contains("button")
        ? "button"
        : "text";
      window.gtag("event", "aff_" + school + "_" + pos, {
        school: school,
        link_position: pos,
        link_text: (a.textContent || "").replace(/\s+/g, "").slice(0, 40)
      });
    },
    true
  );
})();

/* スクロールで要素がふわっと現れる演出(reduced-motion 設定時は無効) */
(function () {
  "use strict";
  if (
    !("IntersectionObserver" in window) ||
    window.matchMedia("(prefers-reduced-motion: reduce)").matches
  ) {
    return;
  }
  var targets = document.querySelectorAll(
    [
      ".section-header",
      ".category-item",
      ".daily-card",
      ".school-card",
      ".featured-article",
      ".pillar",
      ".term-list__item",
      ".theorist-list__item",
      ".chara-guide",
      ".learning-path__step",
      ".article-list-item",
      ".study-journal",
      ".author-profile",
      ".hero__balloon",
    ].join(",")
  );
  targets.forEach(function (el) {
    el.classList.add("reveal");
  });
  var io = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        }
      });
    },
    { rootMargin: "0px 0px -8% 0px", threshold: 0.05 }
  );
  targets.forEach(function (el) {
    io.observe(el);
  });
  // 保険: 何らかの理由で監視が働かなくても、数秒後には必ず全て表示する
  setTimeout(function () {
    targets.forEach(function (el) {
      el.classList.add("is-visible");
    });
  }, 4000);
})();

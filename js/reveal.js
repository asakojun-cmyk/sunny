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

/* 広告リンク(A8)が押された場所をGA4に記録する。
   - aff_click：どの学校でも同じ名前。GA4の「キーイベント（成果）」にするのはこれ。中身に 学校・場所・ページ を入れる
   - aff_<学校>_<場所>：前からある細かい名前（そのまま残す） */
(function () {
  "use strict";
  var SCHOOLS = {
    "459JRK+G3ASDU": "chiiki",
    "459JRK+G3AT5M": "chiiki",
    "4B7XX4+BD0U56": "pasona",
    "4B7XX4+BD0TDE": "pasona",
    "45BQMV+6WV8EY": "manpower",
    "45BQMV+6WV7N6": "manpower",
    "4BCMO3+2VLGT6": "lec",
    "4BE7SX+HV1P6": "recurrent",
    "4BE7SX+DP0GQ": "cmca",
    "4B1O1P+8V4D0Y": "coconala"
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
        : a.closest(".camp-banners,.camp-details")
        ? "campaign"
        : a.closest(".cta-fab,[data-ev^='fab_']")
        ? "fab"
        : a.classList.contains("button")
        ? "button"
        : "text";
      var text = (a.textContent || "").replace(/\s+/g, "").slice(0, 40);
      window.gtag("event", "aff_click", {
        school: school,
        link_position: pos,
        link_text: text,
        page_path: location.pathname
      });
      window.gtag("event", "aff_" + school + "_" + pos, {
        school: school,
        link_position: pos,
        link_text: (a.textContent || "").replace(/\s+/g, "").slice(0, 40)
      });
    },
    true
  );
})();

/* Amazon（本）のリンクが押されたら記録する。イベント名: amazon_click（本の名前・ページつき） */
(function () {
  "use strict";
  document.addEventListener(
    "click",
    function (e) {
      var a = e.target && e.target.closest ? e.target.closest('a[href*="amazon.co.jp"],a[href*="amzn.to"],a[href*="af.moshimo.com"]') : null;
      if (!a || typeof window.gtag !== "function") return;
      var card = a.closest(".book-card,li,section");
      var t = card && card.querySelector(".book-card__title,h3,h4,b,strong");
      window.gtag("event", "amazon_click", {
        book: ((t && t.textContent) || a.textContent || "").replace(/\s+/g, "").slice(0, 60),
        page_path: location.pathname
      });
    },
    true
  );
})();

/* data-ev="名前" のついたリンクやボタンが押されたら、その名前でGA4に記録する */
(function () {
  "use strict";
  document.addEventListener(
    "click",
    function (e) {
      var el = e.target && e.target.closest ? e.target.closest("[data-ev]") : null;
      if (!el || typeof window.gtag !== "function") return;
      var name = el.getAttribute("data-ev");
      var params = { link_text: (el.textContent || "").replace(/\s+/g, "").slice(0, 40) };
      /* アクセス解析は最初のタップのあとに読むので、すぐ別のページへ移るときは、記録を次のページで送る */
      var leaving = false;
      if (el.tagName === "A" && el.target !== "_blank" && el.href) {
        try {
          var u = new URL(el.href, location.href);
          leaving = u.origin === location.origin && (u.pathname !== location.pathname || u.search !== location.search);
        } catch (x) {}
      }
      if (leaving && !window.google_tag_manager) {
        try {
          var q = JSON.parse(sessionStorage.getItem("ev-queue") || "[]");
          q.push([name, params]);
          sessionStorage.setItem("ev-queue", JSON.stringify(q.slice(-10)));
          return;
        } catch (x) {}
      }
      window.gtag("event", name, params);
    },
    true
  );
  /* 前のページで送りきれなかった記録を送る */
  try {
    var q = JSON.parse(sessionStorage.getItem("ev-queue") || "[]");
    sessionStorage.removeItem("ev-queue");
    if (typeof window.gtag === "function") q.forEach(function (x) { window.gtag("event", x[0], x[1]); });
  } catch (x) {}
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

/* 2026-11-01 試験日のあいさつを読みこむ。11/2以降、このかたまりと js/exam-day-open.js・css/exam-day-open.css は消してよい */
(function () {
  var c = document.currentScript, s = document.createElement("script");
  s.src = c.src.replace(/reveal\.js.*$/, "exam-day-open.js");
  document.head.appendChild(s);
})();

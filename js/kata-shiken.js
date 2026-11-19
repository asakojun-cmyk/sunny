/* 試験の側の新しい型（2026-11-20）の動き。<main> の中だけを見る（授業の音声で次の言葉へ進み、
 * <main> が入れかわったあとも、lesson-player.js がこのスクリプトをもう一度読むので、そのつど動く）。
 * - 頭の「授業をきく」：ページの中の授業のプレーヤーを動かす（プレーヤーが出たときだけボタンを出す）
 * - 1問1答：1問ずつ（えらぶ → 答えと解説 → 次の問題へ）。しくみは js/quiz.js のまま
 * - しおり：いま読んでいる段に色
 * - .rise：画面に入ったらふわっと出す */
(function () {
  "use strict";
  var main = document.querySelector("main");
  if (!main || main.getAttribute("data-k") === String(main.childElementCount) + location.pathname) return;
  main.setAttribute("data-k", String(main.childElementCount) + location.pathname);

  /* ---- 授業をきく ---- */
  var go = main.querySelectorAll("[data-lesson-go]");
  var mount = main.querySelector("[data-lesson]");
  if (go.length && mount) {
    var tries = 0;
    (function wait() {
      var play = mount.querySelector("[data-lesson-play]");
      if (!play) { if (++tries < 40) setTimeout(wait, 250); return; }
      Array.prototype.forEach.call(main.querySelectorAll("[data-lesson-hint]"), function (h) { h.hidden = false; });
      Array.prototype.forEach.call(go, function (b) {
        b.hidden = false;
        b.addEventListener("click", function () {
          play.click();
          mount.scrollIntoView({ behavior: "smooth", block: "center" });
        });
      });
      var sync = function () {
        var on = play.classList.contains("is-playing");
        Array.prototype.forEach.call(go, function (b) {
          b.classList.toggle("on", on);
          var lb = b.querySelector(".lb");
          if (lb) lb.textContent = on ? "とめる" : "授業をきく";
        });
      };
      if ("MutationObserver" in window) new MutationObserver(sync).observe(play, { attributes: true, attributeFilter: ["class"] });
    })();
  }

  /* ---- 1問1答を1問ずつ ---- */
  Array.prototype.forEach.call(main.querySelectorAll("[data-qz-steps]"), function (wrap) {
    var boxes = Array.prototype.slice.call(wrap.querySelectorAll("[data-quiz]"));
    if (boxes.length < 2) return;
    var i = 0;
    var top = document.createElement("div");
    top.className = "qz-top";
    top.innerHTML = '<p class="qz-c">問題 <span class="num"></span> / ' + boxes.length + '</p><ol class="qz-dots" aria-hidden="true">' +
      boxes.map(function () { return "<li></li>"; }).join("") + "</ol>";
    wrap.insertBefore(top, wrap.firstChild);
    var nav = document.createElement("div");
    nav.className = "qz-nav";
    nav.innerHTML = '<button type="button" class="qz-prev">← 前の問題</button><button type="button" class="qz-next">次の問題へ →</button>';
    wrap.appendChild(nav);
    var dots = top.querySelectorAll("li");
    var num = top.querySelector(".num");
    var prev = nav.querySelector(".qz-prev");
    var next = nav.querySelector(".qz-next");
    wrap.classList.add("is-steps");
    function answered(b) { var r = b.querySelector("[data-quiz-result]"); return r && !r.hidden; }
    function show() {
      boxes.forEach(function (b, k) { b.classList.toggle("is-now", k === i); });
      Array.prototype.forEach.call(dots, function (d, k) {
        d.classList.toggle("now", k === i);
        d.classList.toggle("done", answered(boxes[k]));
      });
      num.textContent = i + 1;
      prev.hidden = i === 0;
      next.hidden = i === boxes.length - 1;
      next.classList.toggle("ready", answered(boxes[i]));
    }
    prev.addEventListener("click", function () { if (i > 0) { i--; show(); } });
    next.addEventListener("click", function () { if (i < boxes.length - 1) { i++; show(); wrap.scrollIntoView({ behavior: "smooth", block: "start" }); } });
    if ("MutationObserver" in window) {
      boxes.forEach(function (b) {
        var r = b.querySelector("[data-quiz-result]");
        if (r) new MutationObserver(show).observe(r, { attributes: true, attributeFilter: ["hidden"] });
      });
    }
    show();
  });

  /* ---- しおり ---- */
  var links = Array.prototype.slice.call(main.querySelectorAll(".shiori a"));
  if (links.length && "IntersectionObserver" in window) {
    var secs = links.map(function (a) { return main.querySelector(a.getAttribute("href")); });
    var o = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        var k = secs.indexOf(e.target);
        links.forEach(function (l, j) { l.classList.toggle("on", j === k); });
        var a = links[k];
        if (a && window.innerWidth <= 760) a.closest("ol").scrollTo({ left: a.offsetLeft - 16, behavior: "smooth" });
      });
    }, { rootMargin: "-30% 0px -60% 0px" });
    secs.forEach(function (s) { if (s) o.observe(s); });
    links[0].classList.add("on");
  }

  /* ---- ふわっと ---- */
  var rise = main.querySelectorAll(".rise");
  if (!("IntersectionObserver" in window)) {
    Array.prototype.forEach.call(rise, function (e) { e.classList.add("on"); });
  } else {
    var ro = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("on"); ro.unobserve(e.target); } });
    }, { threshold: 0.3 });
    Array.prototype.forEach.call(rise, function (e) { ro.observe(e); });
  }
})();

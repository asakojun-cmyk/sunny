/* 2026-11-01 学科試験の日に、ページを開いたとき1回だけ出す、モヤンとサニー先生の掛け合い。
   箱・余白・文字・色・ボタンは、トップの「学科試験の最初の画面」(index.html の #exam-open)にそろえた。
   閉じ方も同じ：「サイトを見る」・箱の外を押す・Esc。自動では消えない(せりふの途中でも閉じられる)。
   ・日本時間の 11/1、UNTIL の時刻まで。そのあとは何もしない(このファイルの通信だけ残るので、後日消してよい)
   ・同じ人に1回(localStorage)
   ・トップの最初の画面が出ているときは重ねない
   ・絵や文字が1.2秒で用意できなければ、出さない(読みはじめた人の前に遅れて出さないため)
   ・確認用：URLに ?preview=1 をつけると、日付と「1回だけ」に関係なく出る */
(function () {
  "use strict";

  var FROM = Date.parse("2026-11-01T00:00:00+09:00");
  /* 出すのをやめる時刻。変えるときはここだけ。
     いまの値は第33回 実技(論述)の集合時刻 14:10(出典：JCDA 第33回受験案内 1ページ・
     協議会とJCDAの試験日程ページ)。公式に試験の終了時刻の記載は見つからなかった。
     このあとに開く人は、もう試験を受けている途中か、受け終わった人なので、「力を出し切ろう」が合わない。 */
  var UNTIL = Date.parse("2026-11-01T14:10:00+09:00");
  var KEY = "cp-exam-1101-open-seen";
  var WAIT_MS = 1200; /* 絵と文字を待つ上限 */
  var START_MS = 400; /* 2人が出てから最初のせりふまで */

  /* せりふ。who は話す側、lines は文節の改行、ms はそのせりふを出しておく長さ。
     吹き出しが出そろってから1字あたり約0.15秒＋入れかわりの分。最後のせりふは閉じるまで残す */
  var TALK = [
    { who: "moyan", lines: ["今日はついに", "試験日だね！"], ms: 2300 },
    { who: "sunny", lines: ["時計、受験票、", "筆記用具は持った？"], ms: 3000 },
    { who: "moyan", lines: ["うん、持ったよ！"], ms: 1700 },
    { who: "sunny", lines: ["落ち着いて", "力を出し切ろう！"], ms: 2500 },
    { who: "moyan", lines: ["みんな頑張ってね！"], ms: 0 }
  ];

  var script = document.currentScript;
  if (!script || !script.src) return;

  var preview = /[?&]preview=1(&|$)/.test(location.search);
  var now = Date.now();
  if (!preview && (now < FROM || now >= UNTIL)) return;

  function seen() {
    try {
      return localStorage.getItem(KEY) === "1";
    } catch (e) {
      /* 使えないときは、サイトの外から来た1ページ目だけ出す */
      return document.referrer.indexOf(location.origin) === 0;
    }
  }
  function markSeen() {
    try { localStorage.setItem(KEY, "1"); } catch (e) {}
  }

  var probe = document.createElement("dialog");
  if (typeof probe.showModal !== "function") return;

  if (!preview) {
    if (seen()) return;
    /* ページ内リンクで特定の場所へ来た人は、その場所をすぐ見たい人なので出さない */
    if (location.hash) return;
    /* トップの「学科試験の最初の画面」が出ているときは、重ねない */
    var other = document.getElementById("exam-open");
    if (other && other.open) { markSeen(); return; }
  }

  var base = script.src.replace(/js\/[^\/]*$/, "");
  var reduce = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  var html = document.documentElement;
  var root, cancelled = false, timer = 0;

  function build() {
    var says = TALK.map(function (t) {
      return '<div class="exam-day-open__say exam-day-open__say--' + t.who + '"><span>' + t.lines.join("<br>") + "</span></div>";
    }).join("");
    root = document.createElement("dialog");
    root.className = "exam-day-open";
    root.setAttribute("aria-label", "学科試験の日の、モヤンとサニー先生の話");
    root.tabIndex = -1;
    root.innerHTML =
      '<span class="exam-day-open__hill" aria-hidden="true"></span>' +
      '<img class="exam-day-open__cloud exam-day-open__cloud--l" alt="" src="' + base + 'img/parts/01_sky_cloud_left.webp">' +
      '<img class="exam-day-open__cloud exam-day-open__cloud--r" alt="" src="' + base + 'img/parts/03_sky_cloud_right.webp">' +
      '<div class="exam-day-open__panel"><div class="exam-day-open__inner">' +
        '<div class="exam-day-open__stage">' +
          '<div class="exam-day-open__says">' + says + "</div>" +
          '<div class="exam-day-open__chara exam-day-open__chara--moyan"><img alt="" src="' + base + 'img/parts/moyan_school_hat_smile.webp"></div>' +
          '<div class="exam-day-open__chara exam-day-open__chara--sunny"><img alt="" src="' + base + 'img/parts/06_sun_character.webp"></div>' +
        "</div>" +
        '<button class="exam-day-open__close" type="button">サイトを見る</button>' +
      "</div></div>";
  }

  /* 読みはじめたら、用意の途中でも出すのをやめる */
  function stopWaiting() { cancelled = true; removeWaitListeners(); }
  function addWaitListeners() {
    addEventListener("wheel", stopWaiting, { passive: true });
    addEventListener("touchmove", stopWaiting, { passive: true });
    addEventListener("keydown", stopWaiting);
  }
  function removeWaitListeners() {
    removeEventListener("wheel", stopWaiting);
    removeEventListener("touchmove", stopWaiting);
    removeEventListener("keydown", stopWaiting);
  }

  function prepare(done) {
    var finished = false;
    build();
    var imgs = root.querySelectorAll("img");
    var left = imgs.length + 1; /* 絵の数＋CSSと文字 */
    var giveUp = setTimeout(function () { finished = true; removeWaitListeners(); }, WAIT_MS);
    function one() {
      left -= 1;
      if (left > 0 || finished) return;
      finished = true;
      clearTimeout(giveUp);
      removeWaitListeners();
      if (!cancelled) done();
    }
    function fail() { finished = true; clearTimeout(giveUp); removeWaitListeners(); }

    var link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = base + "css/exam-day-open.css?v=20261101c";
    link.onload = function () {
      /* CSSのあとで文字を読みこむ(文字が入れかわるのを見せないため) */
      if (document.fonts && document.fonts.load) {
        var text = TALK.map(function (t) { return t.lines.join(""); }).join("");
        document.fonts.load('700 18px "exam-day-maru"', text).then(one, one);
      } else {
        one();
      }
    };
    link.onerror = fail;
    document.head.appendChild(link);

    [].forEach.call(imgs, function (img) {
      if (img.complete && img.naturalWidth) { one(); return; }
      img.onload = one;
      img.onerror = fail;
    });
  }

  /* 話す側の吹き出しだけを出す。話している側は少しだけゆれる。最後のせりふは閉じるまで残す */
  function speak(i) {
    var says = root.querySelectorAll(".exam-day-open__say");
    [].forEach.call(says, function (el, n) { el.classList.toggle("is-on", n === i); });
    var who = TALK[i].who;
    ["moyan", "sunny"].forEach(function (name) {
      root.querySelector(".exam-day-open__chara--" + name).classList.toggle("is-talking", name === who);
    });
    if (i + 1 < TALK.length) {
      timer = setTimeout(function () { speak(i + 1); }, TALK[i].ms);
    }
  }

  function show() {
    markSeen();
    root.addEventListener("close", function () {
      clearTimeout(timer);
      html.classList.remove("exam-day-open-on");
      if (root.parentNode) root.parentNode.removeChild(root);
    });
    root.addEventListener("click", function (e) {
      if (e.target === root || e.target.closest(".exam-day-open__close")) root.close();
    });
    document.body.appendChild(root);
    html.classList.add("exam-day-open-on");
    root.showModal();
    root.focus();
    timer = setTimeout(function () { speak(0); }, reduce ? 0 : START_MS);
  }

  function start() {
    addWaitListeners();
    prepare(show);
  }

  /* 裏のタブで開かれたときは、見えるようになってから */
  if (document.hidden) {
    document.addEventListener("visibilitychange", function once() {
      if (document.hidden) return;
      document.removeEventListener("visibilitychange", once);
      start();
    });
  } else {
    start();
  }
})();

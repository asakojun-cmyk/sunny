/* 「授業できく」: ページの本文を、サニー先生とモヤン、理論家役の声で読み上げる。
 * 音声と時間の表は scripts/make-lesson-audio.py で先に作っておく(audio/<ページ>/lesson.m4a と lesson.json)。
 * 読んでいる段落に色をつけて、画面を追いかける。再生中に段落を押すと、そこから読む。
 * ページ側には <div data-lesson="../../audio/theorists/holland/"></div> を置くだけ。 */
(function () {
  var mount = document.querySelector("[data-lesson]");
  if (!mount || !window.fetch) return;
  var base = mount.getAttribute("data-lesson");
  var imgBase = base.split("audio/")[0] + "img/parts/";

  /* scripts/make-lesson-audio.py の SELECTOR と同じにする */
  var SELECTOR = [
    ".picnic-intro__line p",
    ".term-oneliner .term-section-title", ".term-oneliner .chara-guide__bubble", ".term-oneliner .term-prose p",
    ".term-kids .term-section-title", ".term-kids .term-prose p",
    ".term-analogy .term-section-title", ".term-analogy .term-prose p",
    ".term-life .term-section-title", ".term-life .term-prose p",
    ".term-formal .term-section-title", ".term-formal__box > p:not(.term-update)", ".term-kakomon li",
    ".term-stages .term-section-note:first-of-type", ".term-formal dl > div", ".term-riasec .term-section-note",
    ".term-try .term-section-title", ".term-try .mini-say__bubble",
    ".kw-talk .mini-say__bubble",
    ".term-exam-points .term-section-title", ".term-exam-points li",
    ".term-exam-advice .chara-guide__bubble", ".term-exam-advice .exam-advice__list li",
    ".term-oboekata .term-section-title", ".term-oboekata .term-prose p",
    ".term-pitfall .term-section-title", ".term-pitfall__box p",
    ".term-similar .term-section-title", ".term-similar dl > div",
    ".term-episode .term-section-title", ".term-episode .term-section-note", ".term-episode .episode-list li"
  ].join(", ");

  var WHO = {
    sunny: { name: "サニー先生", img: "06_sun_character.png" },
    moyan: { name: "モヤン", img: "07_moyan_school_hat_crying.png" }
  };
  var SPEEDS = [1.2, 1.5, 0.8, 1];
  var KEY_SPEED = "lesson-speed";
  var KEY_POS = "lesson-pos:" + location.pathname;

  function load(key) { try { return localStorage.getItem(key); } catch (e) { return null; } }
  function save(key, val) { try { localStorage.setItem(key, val); } catch (e) {} }
  function clock(sec) {
    sec = Math.max(0, Math.round(sec));
    return Math.floor(sec / 60) + ":" + ("0" + (sec % 60)).slice(-2);
  }

  fetch(base + "lesson.json", { cache: "no-cache" })
    .then(function (res) { return res.ok ? res.json() : Promise.reject(); })
    .then(init)
    .catch(function () {});

  function init(data) {
    var els = Array.prototype.slice.call(document.querySelectorAll(SELECTOR));
    var segs = data.segs;
    if (els.length !== segs.length) return; /* 本文を直して音声と合わなくなったら、出さない */

    var audio = new Audio();
    audio.preload = "none";
    var started = false;
    var current = -1;
    var speedIdx = SPEEDS.indexOf(parseFloat(load(KEY_SPEED)));
    if (speedIdx < 0) speedIdx = 0; /* はじめての人は1.2倍から */
    /* 音声を作り直したら、前の「つづき」の位置は使わない(h は音声の版) */
    var saved = (load(KEY_POS) || "").split("@");
    var resumeAt = saved[1] === String(data.h) ? parseFloat(saved[0]) || 0 : 0;
    function savePos(t) { save(KEY_POS, t + "@" + data.h); }
    if (resumeAt < 5 || resumeAt > data.total - 5) resumeAt = 0;
    var handScrollAt = 0;
    /* 理論家本人のセリフ(segs の s が "guest")を読んでいるあいだ、下のバーに出す名前 */
    var guestLabel = document.querySelector(".picnic-intro__line--guest b");
    var guestName = guestLabel ? guestLabel.textContent.trim() : "ゲスト";
    var minutes = Math.max(1, Math.round(data.total / 60));

    mount.className = "lesson";
    mount.setAttribute("role", "group");
    mount.setAttribute("aria-label", "このページを授業できく");
    mount.innerHTML =
      '<div class="lesson__who" aria-hidden="true">' +
        '<img src="' + imgBase + WHO.sunny.img + '" alt="" width="56" height="56">' +
        '<img src="' + imgBase + WHO.moyan.img + '" alt="" width="56" height="56">' +
      '</div>' +
      '<div class="lesson__body">' +
        '<p class="lesson__title">このページを、授業できく</p>' +
        '<p class="lesson__lead">サニー先生とモヤン、理論家さん役の声で読み上げます(約' + minutes + '分)。読んでいるところに色がつきます。</p>' +
        '<div class="lesson__controls">' +
          '<button type="button" class="lesson__play" data-lesson-play><span class="lesson__icon" aria-hidden="true"></span><span data-lesson-label></span></button>' +
          '<button type="button" class="lesson__speed" data-lesson-speed></button>' +
        '</div>' +
        '<div class="lesson__seek" hidden>' +
          '<input type="range" min="0" max="' + Math.floor(data.total) + '" step="1" value="0" aria-label="授業の再生位置">' +
          '<span class="lesson__time"></span>' +
        '</div>' +
        '<p class="lesson__note" role="status" hidden>音声を読みこめませんでした。少し待ってから、もう一度押してみてください。</p>' +
        '<p class="lesson__credit">音声: ' + data.credit + '</p>' +
      '</div>';

    var dock = document.createElement("div");
    dock.className = "lesson-dock";
    dock.setAttribute("role", "group");
    dock.setAttribute("aria-label", "授業の再生");
    dock.innerHTML =
      '<button type="button" class="lesson-dock__play" data-lesson-play><span class="lesson__icon" aria-hidden="true"></span><span class="visually-hidden" data-lesson-label></span></button>' +
      '<img class="lesson-dock__face" src="' + imgBase + WHO.sunny.img + '" alt="" width="34" height="34">' +
      '<span class="lesson-dock__text"><b class="lesson-dock__name"></b><span class="lesson-dock__time"></span></span>' +
      '<button type="button" class="lesson__speed" data-lesson-speed></button>' +
      '<button type="button" class="lesson-dock__close" aria-label="授業をおわる">×</button>';
    document.body.appendChild(dock);

    var seekWrap = mount.querySelector(".lesson__seek");
    var seek = seekWrap.querySelector("input");
    var timeEl = mount.querySelector(".lesson__time");
    var note = mount.querySelector(".lesson__note");
    var playBtns = document.querySelectorAll("[data-lesson-play]");
    var labels = document.querySelectorAll("[data-lesson-label]");
    var speedBtns = document.querySelectorAll("[data-lesson-speed]");
    var face = dock.querySelector(".lesson-dock__face");
    var nameEl = dock.querySelector(".lesson-dock__name");
    var dockTime = dock.querySelector(".lesson-dock__time");

    function setLabel() {
      var text = !audio.paused ? "とめる" : started ? "つづきをきく" : resumeAt ? "つづきからきく" : "授業をはじめる";
      for (var i = 0; i < labels.length; i++) labels[i].textContent = text;
      for (var j = 0; j < playBtns.length; j++) playBtns[j].classList.toggle("is-playing", !audio.paused);
    }
    function setSpeed() {
      audio.playbackRate = SPEEDS[speedIdx];
      for (var i = 0; i < speedBtns.length; i++) {
        speedBtns[i].textContent = "はやさ ×" + SPEEDS[speedIdx];
        speedBtns[i].setAttribute("aria-label", "読むはやさ " + SPEEDS[speedIdx] + "倍。押すと変わります");
      }
    }
    function mark(idx) {
      if (idx === current) return;
      if (current >= 0) els[current].classList.remove("is-speaking");
      current = idx;
      if (idx < 0) return;
      var el = els[idx];
      var w = WHO[segs[idx].s] || { name: guestName };
      el.classList.add("is-speaking");
      face.hidden = !w.img;
      if (w.img) face.src = imgBase + w.img;
      nameEl.textContent = w.name;
      if (!audio.paused && Date.now() - handScrollAt > 4000) {
        var calm = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
        el.scrollIntoView({ block: "center", behavior: calm ? "auto" : "smooth" });
      }
    }
    function tick() {
      var t = audio.currentTime;
      var idx = current;
      /* 段落のあいだの無音では、前の段落に色をつけたままにする */
      for (var i = 0; i < segs.length; i++) { if (t >= segs[i].t - 0.05) idx = i; else break; }
      mark(idx);
      seek.value = Math.floor(t);
      seek.style.setProperty("--lesson-done", (t / data.total * 100).toFixed(1) + "%");
      timeEl.textContent = clock(t) + " / " + clock(data.total);
      dockTime.textContent = "あと" + clock((data.total - t) / SPEEDS[speedIdx]);
    }
    function start() {
      if (!started) {
        started = true;
        audio.src = base + "lesson.m4a?h=" + data.h; /* 作り直したら、古い音声の控えを使わせない */
        if (resumeAt) audio.currentTime = resumeAt;
        seekWrap.hidden = false;
        document.documentElement.classList.add("lesson-on");
        if (window.gtag) gtag("event", "lesson_play", { page_path: location.pathname });
      }
      setSpeed();
      var playing = audio.play();
      if (playing && playing.catch) playing.catch(failed);
    }
    function failed() {
      if (!started) return;
      stop();
      note.hidden = false;
    }
    function toggle() { if (audio.paused) start(); else audio.pause(); }
    function stop() {
      audio.pause();
      mark(-1);
      dock.classList.remove("is-show");
      document.documentElement.classList.remove("lesson-on");
      started = false;
      resumeAt = audio.currentTime > 5 && audio.currentTime < data.total - 5 ? audio.currentTime : 0;
      seekWrap.hidden = true;
      setLabel();
    }

    for (var p = 0; p < playBtns.length; p++) playBtns[p].addEventListener("click", toggle);
    for (var s = 0; s < speedBtns.length; s++) {
      speedBtns[s].addEventListener("click", function () {
        speedIdx = (speedIdx + 1) % SPEEDS.length;
        save(KEY_SPEED, SPEEDS[speedIdx]);
        setSpeed();
        if (started) tick();
      });
    }
    dock.querySelector(".lesson-dock__close").addEventListener("click", stop);
    seek.addEventListener("input", function () { audio.currentTime = +seek.value; tick(); });

    /* 再生をはじめたあとは、段落を押すとそこから読む(リンクやボタンはそのまま) */
    els.forEach(function (el, i) {
      el.addEventListener("click", function (ev) {
        if (!started || ev.target.closest("a, button")) return;
        if (String(window.getSelection && getSelection())) return;
        audio.currentTime = segs[i].t;
        handScrollAt = Date.now();
        if (audio.paused) audio.play();
        tick();
      });
    });

    audio.addEventListener("play", setLabel);
    audio.addEventListener("pause", function () { setLabel(); savePos(audio.currentTime); });
    audio.addEventListener("error", failed);
    audio.addEventListener("playing", function () { note.hidden = true; });
    audio.addEventListener("timeupdate", function () {
      tick();
      if (Math.floor(audio.currentTime) % 5 === 0) savePos(audio.currentTime);
    });
    audio.addEventListener("ended", function () { savePos(0); audio.currentTime = 0; stop(); });

    /* 自分でスクロールしているあいだは、画面を追いかけない */
    ["wheel", "touchmove", "keydown"].forEach(function (type) {
      window.addEventListener(type, function () { handScrollAt = Date.now(); }, { passive: true });
    });

    /* 上のプレーヤーが画面から外れたら、下に小さい操作バーを出す */
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (entries) {
        dock.classList.toggle("is-show", started && !entries[0].isIntersecting);
      }).observe(mount);
      audio.addEventListener("play", function () {
        var r = mount.getBoundingClientRect();
        dock.classList.toggle("is-show", r.bottom < 0 || r.top > innerHeight);
      });
    }

    if ("mediaSession" in navigator && window.MediaMetadata) {
      var h1 = document.querySelector("h1");
      navigator.mediaSession.metadata = new MediaMetadata({
        title: (h1 ? h1.textContent.trim() : document.title) + "の授業",
        artist: "キャリコン学びピクニック"
      });
    }

    setSpeed();
    setLabel();
  }
})();

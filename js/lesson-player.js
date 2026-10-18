/* 「授業できく」: ページの本文を、サニー先生とモヤン、理論家役の声で読み上げる。
 * 音声と時間の表は scripts/make-lesson-audio.py で先に作っておく(audio/<ページ>/lesson.m4a と lesson.json)。
 * 読んでいる段落に色をつけて、画面を追いかける。再生中に段落を押すと、そこから読む。
 * 聞き終わったら、一覧の順(audio/playlist.json)で次のページへ進む。スマホで聞き流しても途切れないよう、
 * ページは開き直さず、本文だけ入れかえて同じ音声プレーヤーで続ける。
 * ページ側には <div data-lesson="../../audio/theorists/holland/"></div> を置くだけ。 */
(function () {
  if (!window.fetch || !document.querySelector("[data-lesson]")) return;

  /* scripts/make-lesson-audio.py の SELECTOR と同じにする */
  var SELECTOR = [
    ".picnic-intro__line p",
    ".episode > h2", ".line__msg", ".okawari > h2", ".okawari__card > p",
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
  var KEY_AUTO = "lesson-auto";
  /* 本文を入れかえたあとに、もう一度動かす必要があるスクリプト(1問1答・ピクニックの用語カード) */
  var RERUN = /\/js\/(quiz|picnic-episode)\.js/;

  function load(key) { try { return localStorage.getItem(key); } catch (e) { return null; } }
  function save(key, val) { try { localStorage.setItem(key, val); } catch (e) {} }
  function clock(sec) {
    sec = Math.max(0, Math.round(sec));
    return Math.floor(sec / 60) + ":" + ("0" + (sec % 60)).slice(-2);
  }
  function esc(text) {
    return String(text).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; });
  }

  var audio = new Audio();
  audio.preload = "none";
  var speedIdx = SPEEDS.indexOf(parseFloat(load(KEY_SPEED)));
  if (speedIdx < 0) speedIdx = 0; /* はじめての人は1.2倍から */
  var auto = load(KEY_AUTO) !== "off"; /* 聞き終わったら次のページへ進むか */
  var handScrollAt = 0;
  var S = null;        /* いまのページのプレーヤーの状態 */
  var playlist = null; /* audio/playlist.json */
  var watcher = null;

  /* ---------- 下に出る小さい操作バー(1つを使いまわす) ---------- */
  var dock = document.createElement("div");
  dock.className = "lesson-dock";
  dock.setAttribute("role", "group");
  dock.setAttribute("aria-label", "授業の再生");
  dock.innerHTML =
    '<button type="button" class="lesson-dock__play" data-lesson-play><span class="lesson__icon" aria-hidden="true"></span><span class="visually-hidden" data-lesson-label></span></button>' +
    '<img class="lesson-dock__face" alt="" width="34" height="34">' +
    '<span class="lesson-dock__text"><b class="lesson-dock__name"></b><span class="lesson-dock__time"></span></span>' +
    '<button type="button" class="lesson__speed" data-lesson-speed></button>' +
    '<button type="button" class="lesson-dock__close" aria-label="授業をおわる">×</button>';
  document.body.appendChild(dock);
  var face = dock.querySelector(".lesson-dock__face");
  var nameEl = dock.querySelector(".lesson-dock__name");
  var dockTime = dock.querySelector(".lesson-dock__time");

  function each(sel, fn) { Array.prototype.forEach.call(document.querySelectorAll(sel), fn); }

  function setLabel() {
    if (!S) return;
    var text = !audio.paused ? "とめる" : S.started ? "つづきをきく" : S.resumeAt ? "つづきからきく" : "授業をはじめる";
    each("[data-lesson-label]", function (el) { el.textContent = text; });
    each("[data-lesson-play]", function (el) { el.classList.toggle("is-playing", !audio.paused); });
  }
  function setSpeed() {
    audio.playbackRate = SPEEDS[speedIdx];
    each("[data-lesson-speed]", function (el) {
      el.textContent = "はやさ ×" + SPEEDS[speedIdx];
      el.setAttribute("aria-label", "読むはやさ " + SPEEDS[speedIdx] + "倍。押すと変わります");
    });
  }
  function setAuto() {
    each("[data-lesson-auto]", function (el) {
      el.setAttribute("aria-pressed", auto ? "true" : "false");
      el.textContent = auto ? "オン" : "オフ";
    });
  }
  function savePos(t) { if (S) save(S.keyPos, t + "@" + S.data.h); }

  function mark(idx) {
    if (!S || idx === S.current) return;
    if (S.current >= 0) S.els[S.current].classList.remove("is-speaking");
    S.current = idx;
    if (idx < 0) return;
    var el = S.els[idx];
    var w = WHO[S.data.segs[idx].s] || { name: S.guestName };
    el.classList.add("is-speaking");
    face.hidden = !w.img;
    if (w.img) face.src = S.imgBase + faceOf(el, w);
    nameEl.textContent = w.name;
    if (!audio.paused && Date.now() - handScrollAt > 4000) {
      var calm = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
      el.scrollIntoView({ block: "center", behavior: calm ? "auto" : "smooth" });
    }
  }
  function tick() {
    if (!S || !S.started) return;
    var t = audio.currentTime;
    var segs = S.data.segs;
    var idx = S.current;
    /* 段落のあいだの無音では、前の段落に色をつけたままにする */
    for (var i = 0; i < segs.length; i++) { if (t >= segs[i].t - 0.05) idx = i; else break; }
    mark(idx);
    S.seek.value = Math.floor(t);
    S.seek.style.setProperty("--lesson-done", (t / S.data.total * 100).toFixed(1) + "%");
    S.timeEl.textContent = clock(t) + " / " + clock(S.data.total);
    dockTime.textContent = "あと" + clock((S.data.total - t) / SPEEDS[speedIdx]);
  }
  function begin() { /* このページの音声を、プレーヤーにのせる */
    S.started = true;
    S.seekWrap.hidden = false;
    document.documentElement.classList.add("lesson-on");
    if (window.gtag) gtag("event", "lesson_play", { page_path: location.pathname });
    fetchNext();
  }
  function start() {
    if (!S.started) {
      audio.src = S.src; /* 作り直したら、古い音声の控えを使わせない(?h=版) */
      if (S.resumeAt) audio.currentTime = S.resumeAt;
      begin();
    }
    setSpeed();
    var playing = audio.play();
    if (playing && playing.catch) playing.catch(failed);
  }
  function failed() {
    if (!S || !S.started) return;
    stop();
    S.note.hidden = false;
  }
  function toggle() { if (audio.paused) start(); else audio.pause(); }
  function stop() {
    audio.pause();
    mark(-1);
    dock.classList.remove("is-show");
    document.documentElement.classList.remove("lesson-on");
    S.started = false;
    S.resumeAt = audio.currentTime > 5 && audio.currentTime < S.data.total - 5 ? audio.currentTime : 0;
    S.seekWrap.hidden = true;
    setLabel();
  }

  /* ---------- 次のページ ---------- */
  function findNext() {
    if (!playlist) return null;
    var path = location.pathname.replace(/index\.html$/, "");
    for (var key in playlist) {
      var list = playlist[key];
      for (var i = 0; i < list.length - 1; i++) if (list[i].u === path) return list[i + 1];
    }
    return null;
  }
  /* 次のページの本文と音声の表を、聞いているあいだに取っておく。
   * スマホの画面を消していても、聞き終わった瞬間に次の音声をかけられるようにするため */
  function prepareNext() {
    var mine = S;
    var next = findNext();
    mine.next = next;
    mine.ready = null;
    var line = mine.mount.querySelector(".lesson__next");
    if (line) {
      line.hidden = !next;
      if (next) line.querySelector("a").textContent = "「" + next.t + "」", line.querySelector("a").href = next.u;
    }
    if (next && mine.started) fetchNext();
  }
  function fetchNext() {
    var mine = S;
    var next = mine.next;
    if (!next || mine.fetching) return;
    mine.fetching = true;
    fetch(next.u).then(function (res) { return res.ok ? res.text() : Promise.reject(); }).then(function (html) {
      var doc = new DOMParser().parseFromString(html, "text/html");
      var m = doc.querySelector("[data-lesson]");
      if (!m || !doc.querySelector("main")) return Promise.reject();
      var base = new URL(m.getAttribute("data-lesson"), new URL(next.u, location.href)).href;
      return fetch(base + "lesson.json", { cache: "no-cache" }).then(function (res) { return res.ok ? res.json() : Promise.reject(); }).then(function (data) {
        if (doc.querySelectorAll(SELECTOR).length !== data.segs.length) return Promise.reject();
        if (S === mine) mine.ready = { doc: doc, data: data, base: base };
      });
    }).catch(function () {});
  }
  function goNext() {
    var next = S.next;
    var ready = S.ready;
    if (!ready) { location.href = next.u; return; } /* 取っておけなかったときは、ふつうにページを開く */
    /* 先に次の音声をかけてから、本文を入れかえる */
    audio.src = ready.base + "lesson.m4a?h=" + ready.data.h;
    setSpeed();
    var playing = audio.play();
    if (playing && playing.catch) playing.catch(function () {});
    mark(-1);

    history.pushState({ lesson: 1 }, "", next.u);
    document.title = ready.doc.title;
    document.querySelector("main").innerHTML = ready.doc.querySelector("main").innerHTML;
    each('script[type="application/json"][id]', function (old) {
      var fresh = ready.doc.getElementById(old.id);
      if (fresh) old.textContent = fresh.textContent;
    });
    Array.prototype.forEach.call(ready.doc.querySelectorAll("script[src]"), function (sc) {
      if (!RERUN.test(sc.getAttribute("src"))) return;
      var again = document.createElement("script");
      again.src = sc.getAttribute("src");
      document.body.appendChild(again);
    });
    window.scrollTo(0, 0);
    handScrollAt = 0;
    if (window.gtag) gtag("event", "page_view", { page_location: location.href, page_title: document.title });

    if (setup(document.querySelector("[data-lesson]"), ready.data)) begin();
    setLabel();
    tick();
  }

  /* 「ひとことでいうと」をタイトルのすぐ下へ移した(2026-10)。それより前に作った音声は
   * 「ピクニックのはじまり」のあいさつ → ひとこと の順で読んでいるので、色をつける順もそれに合わせる。
   * 音声を作り直したら(ページの順で読むようになったら)、ページの順のまま使う */
  function readOrder(els, segs) {
    var intro = [], one = [], rest = [];
    els.forEach(function (el) {
      if (el.closest(".picnic-intro")) intro.push(el);
      else if (el.closest(".term-oneliner")) one.push(el);
      else rest.push(el);
    });
    if (!intro.length || !one.length || els[0] !== one[0]) return els;
    var alt = intro.concat(one, rest);
    function score(list) {
      var n = 0;
      intro.forEach(function (el) {
        var line = el.closest(".picnic-intro__line");
        var who = line && /--guest/.test(line.className) ? "guest" : "sunny";
        var seg = segs[list.indexOf(el)];
        if (seg && seg.s === who) n++;
      });
      return n;
    }
    return score(alt) > score(els) ? alt : els;
  }
  /* うれしい・わかった、のセリフでは、下のバーのモヤンも笑顔にする */
  function faceOf(el, w) {
    if (w !== WHO.moyan) return w.img;
    var fig = el.closest(".chara-guide--moyan, .mini-say--moyan");
    var img = fig && fig.querySelector("img");
    return img && /smile/.test(img.getAttribute("src") || "") ? "t/moyan_school_hat_smile-200.webp" : w.img;
  }

  /* ---------- ページの中のプレーヤー ---------- */
  function setup(mount, data) {
    var els = readOrder(Array.prototype.slice.call(document.querySelectorAll(SELECTOR)), data.segs);
    if (!mount || els.length !== data.segs.length) return false; /* 本文を直して音声と合わなくなったら、出さない */
    var base = new URL(mount.getAttribute("data-lesson"), location.href).href;
    var guestLabel = document.querySelector(".picnic-intro__line--guest b, .line--guest .line__msg b");
    var keyPos = "lesson-pos:" + location.pathname;
    /* 音声を作り直したら、前の「つづき」の位置は使わない(h は音声の版) */
    var saved = (load(keyPos) || "").split("@");
    var resumeAt = saved[1] === String(data.h) ? parseFloat(saved[0]) || 0 : 0;
    if (resumeAt < 5 || resumeAt > data.total - 5) resumeAt = 0;
    var imgBase = base.split("audio/")[0] + "img/parts/";
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
        '<p class="lesson__next" hidden>つぎは<a href="#"></a>。聞き終わったら自動で進む <button type="button" class="lesson__auto" data-lesson-auto></button></p>' +
        '<p class="lesson__note" role="status" hidden>音声を読みこめませんでした。少し待ってから、もう一度押してみてください。</p>' +
        '<p class="lesson__credit">音声: ' + esc(data.credit) + '</p>' +
      '</div>';

    S = {
      mount: mount, data: data, els: els, keyPos: keyPos, resumeAt: resumeAt, imgBase: imgBase,
      src: base + "lesson.m4a?h=" + data.h, started: false, current: -1, next: null, ready: null,
      guestName: guestLabel ? guestLabel.textContent.trim() : "ゲスト",
      seekWrap: mount.querySelector(".lesson__seek"), seek: mount.querySelector(".lesson__seek input"),
      timeEl: mount.querySelector(".lesson__time"), note: mount.querySelector(".lesson__note")
    };
    face.src = imgBase + WHO.sunny.img;

    mount.querySelector("[data-lesson-play]").addEventListener("click", toggle);
    mount.querySelector("[data-lesson-speed]").addEventListener("click", nextSpeed);
    mount.querySelector("[data-lesson-auto]").addEventListener("click", function () {
      auto = !auto;
      save(KEY_AUTO, auto ? "on" : "off");
      setAuto();
    });
    S.seek.addEventListener("input", function () { audio.currentTime = +S.seek.value; tick(); });

    /* 再生をはじめたあとは、段落を押すとそこから読む(リンクやボタンはそのまま) */
    els.forEach(function (el, i) {
      el.addEventListener("click", function (ev) {
        if (!S || !S.started || ev.target.closest("a, button")) return;
        if (String(window.getSelection && getSelection())) return;
        audio.currentTime = data.segs[i].t;
        handScrollAt = Date.now();
        if (audio.paused) audio.play();
        tick();
      });
    });

    /* 上のプレーヤーが画面から外れたら、下に小さい操作バーを出す */
    if ("IntersectionObserver" in window) {
      if (watcher) watcher.disconnect();
      watcher = new IntersectionObserver(function (entries) {
        dock.classList.toggle("is-show", !!S && S.started && !entries[0].isIntersecting);
      });
      watcher.observe(mount);
    }

    if ("mediaSession" in navigator && window.MediaMetadata) {
      var h1 = document.querySelector("h1");
      navigator.mediaSession.metadata = new MediaMetadata({
        title: (h1 ? h1.textContent.trim() : document.title) + "の授業",
        artist: "キャリコン学びピクニック"
      });
    }

    setSpeed();
    setAuto();
    setLabel();
    if (playlist) prepareNext();
    return true;
  }
  function nextSpeed() {
    speedIdx = (speedIdx + 1) % SPEEDS.length;
    save(KEY_SPEED, SPEEDS[speedIdx]);
    setSpeed();
    tick();
  }

  /* ---------- プレーヤー全体で1回だけつなぐもの ---------- */
  dock.querySelector("[data-lesson-play]").addEventListener("click", toggle);
  dock.querySelector("[data-lesson-speed]").addEventListener("click", nextSpeed);
  dock.querySelector(".lesson-dock__close").addEventListener("click", stop);

  audio.addEventListener("play", function () {
    setLabel();
    if (!S) return;
    var r = S.mount.getBoundingClientRect();
    dock.classList.toggle("is-show", r.bottom < 0 || r.top > innerHeight);
  });
  audio.addEventListener("pause", function () { setLabel(); if (S && S.started && !audio.ended) savePos(audio.currentTime); });
  audio.addEventListener("error", failed);
  audio.addEventListener("playing", function () { if (S) S.note.hidden = true; });
  audio.addEventListener("timeupdate", function () {
    tick();
    if (S && S.started && Math.floor(audio.currentTime) % 5 === 0) savePos(audio.currentTime);
  });
  audio.addEventListener("ended", function () {
    savePos(0);
    if (auto && S.next) { goNext(); return; }
    audio.currentTime = 0;
    stop();
  });

  /* 自分でスクロールしているあいだは、画面を追いかけない */
  ["wheel", "touchmove", "keydown"].forEach(function (type) {
    window.addEventListener(type, function () { handScrollAt = Date.now(); }, { passive: true });
  });
  /* 続けて聞いて進んだあとに「戻る」を押したら、そのページを開き直す */
  window.addEventListener("popstate", function () { location.reload(); });

  if ("mediaSession" in navigator) {
    try {
      navigator.mediaSession.setActionHandler("play", start);
      navigator.mediaSession.setActionHandler("pause", function () { audio.pause(); });
      navigator.mediaSession.setActionHandler("nexttrack", function () { if (S && S.started && S.next) goNext(); });
    } catch (e) {}
  }

  var mount = document.querySelector("[data-lesson]");
  var here = new URL(mount.getAttribute("data-lesson"), location.href).href;
  fetch(here + "lesson.json", { cache: "no-cache" })
    .then(function (res) { return res.ok ? res.json() : Promise.reject(); })
    .then(function (data) {
      if (!setup(mount, data)) return;
      return fetch(here.split("audio/")[0] + "audio/playlist.json", { cache: "no-cache" })
        .then(function (res) { return res.ok ? res.json() : Promise.reject(); })
        .then(function (list) { playlist = list; prepareNext(); });
    })
    .catch(function () {});
})();

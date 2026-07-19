/* マップのモヤン&サニーが、カーソルをゆっくり追いかけて散歩する。
 * - タッチ端末・prefers-reduced-motion では動かない(定位置のまま)
 * - pointer-events:none なので、看板のクリックは一切じゃましない */
(function () {
  "use strict";
  var stage = document.querySelector(".map-stage");
  var sunny = document.getElementById("map-sunny");
  var moyan = document.getElementById("map-moyan");
  if (!stage || !sunny || !moyan) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  if (!window.matchMedia("(hover: hover) and (pointer: fine)").matches) return;

  // 目標(カーソル位置。ステージ内の 0〜1)
  var tx = 0.5, ty = 0.5, active = false, raf = null;
  // 現在位置(lerp でゆっくり近づく)
  var s = { x: 0.5, y: 0.5, k: 0.035, max: 0.09 }; // サニー:のんびり
  var m = { x: 0.5, y: 0.5, k: 0.06, max: 0.12 };  // モヤン:ちょっと速い

  function onMove(e) {
    var r = stage.getBoundingClientRect();
    tx = (e.clientX - r.left) / r.width;
    ty = (e.clientY - r.top) / r.height;
    active = true;
    if (!raf) tick();
  }

  function step(c, homeX, homeY) {
    // カーソルに向かうが、定位置から max 以上は離れない(施設の看板を隠さない)
    var gx = active ? tx : homeX;
    var gy = active ? ty : homeY;
    var dx = gx - homeX, dy = gy - homeY;
    var len = Math.sqrt(dx * dx + dy * dy);
    if (len > c.max) { dx = (dx / len) * c.max; dy = (dy / len) * c.max; }
    var aimX = homeX + dx, aimY = homeY + dy;
    c.vx = (aimX - c.x) * c.k;
    c.x += c.vx;
    c.y += (aimY - c.y) * c.k;
    return c;
  }

  var HOME = { sx: 0.48, sy: 0.46, mx: 0.55, my: 0.52 };

  function tick() {
    raf = window.requestAnimationFrame(tick);
    var r = stage.getBoundingClientRect();
    step(s, HOME.sx, HOME.sy);
    step(m, HOME.mx, HOME.my);
    var tilt = Math.max(-6, Math.min(6, (m.vx || 0) * 2600));
    sunny.style.transform =
      "translate(" + ((s.x - HOME.sx) * r.width) + "px," + ((s.y - HOME.sy) * r.height) + "px)";
    moyan.style.transform =
      "translate(" + ((m.x - HOME.mx) * r.width) + "px," + ((m.y - HOME.my) * r.height) + "px) rotate(" + tilt + "deg)";
  }

  stage.addEventListener("mousemove", onMove);
  stage.addEventListener("mouseleave", function () { active = false; });
})();

/* はじまりの劇:クリックでスキップ */
(function () {
  var hero = document.querySelector(".picnic-hero--note");
  if (!hero) return;
  hero.addEventListener("click", function () { hero.classList.add("is-done"); }, { once: true });
  /* 劇が終わったら舞台を素通しに */
  window.setTimeout(function () { hero.classList.add("is-done"); }, 27500);
})();

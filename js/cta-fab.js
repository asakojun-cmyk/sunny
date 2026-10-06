/* 右下にいつも出ている「説明会は無料」の雲のボタン(絵はサイトの水彩の素材)。カーソルを合わせると、雲の後ろからサニー先生がのぞく。
 * 少しスクロールしたら現れ、ページ内の説明会の案内やフッターが見えている間は引っこむ。
 * × で閉じると、そのタブを開いている間は出さない。 */
(function () {
  var KEY = "cta-fab-closed";
  try { if (sessionStorage.getItem(KEY)) return; } catch (e) {}

  var wrap = document.createElement("div");
  wrap.className = "cta-fab";
  wrap.innerHTML =
    '<a class="cta-fab__link" href="/schools/chiiki-renkei-platform/" data-ev="fab_setsumeikai" aria-label="養成学校の無料説明会を見てみる。オンラインで参加できます(広告を含むページへ)">' +
      '<span class="cta-fab__note" aria-hidden="true">＼ オンラインでOK！ ／</span>' +
      '<img class="cta-fab__sunny" src="/img/parts/06_sun_character.png" alt="" width="66" height="66">' +
      '<span class="cta-fab__sign"><small>養成学校の<i class="cta-fab__pr">PR</i></small><b>説明会は無料</b></span>' +
    '</a>' +
    '<button class="cta-fab__close" type="button" aria-label="このボタンを閉じる">×</button>';
  document.body.appendChild(wrap);

  var scrolled = false;
  var covered = 0;
  function update() {
    wrap.classList.toggle("is-show", scrolled && covered === 0);
  }
  function onScroll() {
    var now = window.scrollY > 480;
    if (now !== scrolled) { scrolled = now; update(); }
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        var was = en.target.__fabSeen || false;
        if (en.isIntersecting !== was) {
          en.target.__fabSeen = en.isIntersecting;
          covered += en.isIntersecting ? 1 : -1;
        }
      });
      update();
    });
    var hide = document.querySelectorAll(".lp-cta, .site-footer");
    for (var i = 0; i < hide.length; i++) io.observe(hide[i]);
  }

  wrap.querySelector(".cta-fab__close").addEventListener("click", function () {
    wrap.classList.remove("is-show");
    try { sessionStorage.setItem(KEY, "1"); } catch (e) {}
    setTimeout(function () { wrap.remove(); }, 300);
  });
})();

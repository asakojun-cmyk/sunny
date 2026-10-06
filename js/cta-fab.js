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

  /* 行き先: 紹介リンク(A8)の無料説明会ページ。
   * ただし「この記事に紹介リンクは含みません」と明記しているページでは、
   * その表示と食い違わないよう、サイト内の講座ページへ送る。 */
  var AFF = "https://px.a8.net/svt/ejp?a8mat=459JRK+G3AT5M+59PG+BW8O2&a8ejpredirect=https%3A%2F%2Fcareerjp.work%2Fcc1%2Fsetsumeikai";
  var PIXEL = "https://www17.a8.net/0.gif?a8mat=459JRK+G3AT5M+59PG+BW8O2";
  var link = wrap.querySelector(".cta-fab__link");
  var disc = document.querySelector(".disclosure");
  var noAff = !!(disc && /含みません/.test(disc.textContent.replace(/\s+/g, "")));
  var pixelDone = noAff;
  if (!noAff) {
    link.href = AFF;
    link.target = "_blank";
    link.rel = "sponsored nofollow noopener noreferrer";
    link.setAttribute("data-ev", "fab_setsumeikai_aff");
    link.setAttribute("aria-label", "養成学校の無料説明会のページを開く。オンラインで参加できます(広告・外部サイト)");
  }

  var scrolled = false;
  var covered = 0;
  function update() {
    var show = scrolled && covered === 0;
    wrap.classList.toggle("is-show", show);
    if (show && !pixelDone) {
      /* A8の表示計測用の1pxの画像。ボタンが初めて見えたときに1回だけ読み込む */
      pixelDone = true;
      var px = new Image(1, 1);
      px.alt = "";
      px.style.cssText = "position:absolute;width:1px;height:1px;border:0;opacity:0;pointer-events:none";
      px.src = PIXEL;
      wrap.appendChild(px);
    }
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

/* 説明会の申込み先へのボタン(スマホでは下のタブのすぐ上の細い帯、PCでは右下の雲)。
 * 行き先は、比較表の7校の説明会の申込み先(/schools/compare/#apply-h)。特定の1校には送らない
 * (このサイトは紹介料の有無で学校を選ばない。2026-10-18に1校の紹介リンクから変更)。
 * 2026-10-18 読みもののページでは出さない。出すのは学校選びのページ(/schools/・/school-guides/)だけ。
 *   さらに、ページの半分ほど読みすすめてから出す。比較リスト(比較バー)が出ているあいだは引っこめる。
 * × で閉じると、そのタブを開いている間は出さない。
 * あわせて、下のタブの「いま開いているページ」に aria-current="page" をつける。 */
(function () {
  "use strict";

  /* 下のタブ: いまのページのリンクに印をつける(# だけのリンク・ページ内リンクは対象外) */
  try {
    var here = location.pathname.replace(/index\.html$/, "");
    document.querySelectorAll(".bottom-nav__item[href]").forEach(function (a) {
      var href = a.getAttribute("href");
      if (!href || href.charAt(0) === "#" || href.indexOf("#") !== -1) return;
      var p = new URL(href, location.href).pathname.replace(/index\.html$/, "");
      if (p === here) a.setAttribute("aria-current", "page");
    });
  } catch (e) {}

  var KEY = "cta-fab-closed";
  try { if (sessionStorage.getItem(KEY)) return; } catch (e) {}
  /* 申込み先の一覧があるページ(比較ページ)では出さない */
  if (document.getElementById("apply-h")) return;
  /* 学校選びのページだけで出す */
  if (!/^\/(schools|school-guides)\//.test(location.pathname)) return;

  var wrap = document.createElement("div");
  wrap.className = "cta-fab";
  wrap.innerHTML =
    '<a class="cta-fab__link" href="/schools/compare/#apply-h" data-ev="fab_setsumeikai" aria-label="比較表の7校の無料説明会の申込み先を見る。オンラインで参加できる学校が多いです">' +
      '<span class="cta-fab__note" aria-hidden="true">＼ オンラインでOK！ ／</span>' +
      '<img class="cta-fab__sunny" src="/img/parts/06_sun_character.webp" alt="" width="66" height="66">' +
      '<span class="cta-fab__sign"><small>7校の無料説明会</small><b>申込み先を見る <span aria-hidden="true">▶︎</span></b></span>' +
    '</a>' +
    '<button class="cta-fab__close" type="button" aria-label="このボタンを閉じる">×</button>';
  document.body.appendChild(wrap);

  var bar = document.querySelector("[data-compare-bar]");
  var closed = false;

  function barVisible() {
    if (!bar || bar.hidden) return false;
    var r = bar.getBoundingClientRect();
    return r.height > 0 && r.bottom > 0 && r.top < window.innerHeight;
  }

  function update() {
    if (closed) return;
    var doc = document.documentElement;
    var max = Math.max(1, doc.scrollHeight - window.innerHeight);
    var read = (window.scrollY || doc.scrollTop) / max;
    var show = read >= 0.5 && !barVisible();
    wrap.classList.toggle("is-show", show);
    /* 見えていないあいだはキーボードでも選べないように */
    if (show) wrap.removeAttribute("inert"); else wrap.setAttribute("inert", "");
  }

  var ticking = false;
  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () { ticking = false; update(); });
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll);
  if (bar && "MutationObserver" in window) {
    new MutationObserver(onScroll).observe(bar, { attributes: true, attributeFilter: ["hidden"] });
  }
  update();

  wrap.querySelector(".cta-fab__close").addEventListener("click", function () {
    closed = true;
    wrap.classList.remove("is-show");
    try { sessionStorage.setItem(KEY, "1"); } catch (e) {}
    window.removeEventListener("scroll", onScroll);
    window.removeEventListener("resize", onScroll);
    setTimeout(function () { wrap.remove(); }, 300);
  });
})();

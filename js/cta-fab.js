/* 右下にいつも出ている「説明会は無料」の雲のボタン(絵はサイトの水彩の素材)。カーソルを合わせると、雲の後ろからサニー先生がのぞく。
 * 行き先は、比較表の7校の説明会の申込み先(/schools/compare/#apply-h)。特定の1校には送らない
 * (このサイトは紹介料の有無で学校を選ばない。2026-10-18に1校の紹介リンクから変更)。
 * ページを開いたときから、いつも出しておく(出たり消えたりしない)。
 * × で閉じると、そのタブを開いている間は出さない。 */
(function () {
  var KEY = "cta-fab-closed";
  try { if (sessionStorage.getItem(KEY)) return; } catch (e) {}
  /* 申込み先の一覧があるページ(比較ページ)では出さない */
  if (document.getElementById("apply-h")) return;

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
  wrap.classList.add("is-show");

  wrap.querySelector(".cta-fab__close").addEventListener("click", function () {
    wrap.classList.remove("is-show");
    try { sessionStorage.setItem(KEY, "1"); } catch (e) {}
    setTimeout(function () { wrap.remove(); }, 300);
  });
})();

/* 右下のサニー先生 検索ボックス。
 * 吹き出し「ここをおすと、わからない言葉を調べられるよ」を押すと
 * その場で検索ボックスが開く。JSが無い場合は検索ページへのリンクのまま。 */
(function () {
  var fab = document.getElementById("search-fab");
  if (!fab) return;
  var toggle = fab.querySelector(".search-fab__toggle");
  var panel = fab.querySelector(".search-fab__panel");
  var close = fab.querySelector(".search-fab__close");
  var input = fab.querySelector('input[type="search"]');
  if (!toggle || !panel) return;

  function setOpen(open) {
    panel.hidden = !open;
    fab.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", String(open));
    if (open && input) input.focus();
  }

  toggle.addEventListener("click", function (e) {
    e.preventDefault();
    setOpen(panel.hidden);
  });
  if (close) {
    close.addEventListener("click", function () {
      setOpen(false);
    });
  }
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !panel.hidden) setOpen(false);
  });
})();

/* キャリア理論家とピクニックランチ: 理論家・理論の検索絞り込み
 * 「いま読めるお話」(カード)と「もうすぐ来る先生」(たたんだ名前の一覧)の両方をしぼる。
 * さがしている間は、当たった先生がいれば「もうすぐ来る先生」を開き、
 * 当たりがない側の見出しごと隠す。検索をやめたら、開け閉めは元にもどす。 */
(() => {
  const input = document.querySelector("[data-obento-search]");
  if (!input) return;
  const cards = [...document.querySelectorAll("[data-obento-card]")];
  const empty = document.querySelector("[data-obento-empty]");
  const now = document.querySelector("[data-obento-now]");
  const soon = document.querySelector("[data-obento-soon]");
  let soonWasOpen = soon ? soon.open : false;
  let searching = false;

  input.addEventListener("input", () => {
    const query = input.value.trim().toLowerCase().replace(/\s+/g, "");
    if (query && !searching && soon) soonWasOpen = soon.open;
    searching = !!query;
    let visible = 0;
    let visibleNow = 0;
    let visibleSoon = 0;
    cards.forEach((card) => {
      const text = (card.dataset.obentoText || "").toLowerCase().replace(/\s+/g, "");
      const matches = !query || text.includes(query);
      card.hidden = !matches;
      if (!matches) return;
      visible += 1;
      if (soon && soon.contains(card)) visibleSoon += 1;
      else visibleNow += 1;
    });
    if (now) now.hidden = !!query && visibleNow === 0;
    if (soon) {
      soon.hidden = !!query && visibleSoon === 0;
      soon.open = query ? visibleSoon > 0 : soonWasOpen;
    }
    if (empty) empty.hidden = visible !== 0;
  });
})();

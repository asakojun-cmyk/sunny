/* キャリア理論家とピクニックランチ: 理論家・理論の検索絞り込み */
(() => {
  const input = document.querySelector("[data-obento-search]");
  if (!input) return;
  const cards = [...document.querySelectorAll("[data-obento-card]")];
  const empty = document.querySelector("[data-obento-empty]");

  input.addEventListener("input", () => {
    const query = input.value.trim().toLowerCase().replace(/\s+/g, "");
    let visible = 0;
    cards.forEach((card) => {
      const text = (card.dataset.obentoText || "").toLowerCase().replace(/\s+/g, "");
      const matches = !query || text.includes(query);
      card.hidden = !matches;
      if (matches) visible += 1;
    });
    if (empty) empty.hidden = visible !== 0;
  });
})();

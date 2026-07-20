(() => {
  const input = document.querySelector("[data-library-search]");
  if (!input) return;
  const books = [...document.querySelectorAll("[data-library-book]")];
  const empty = document.querySelector("[data-library-empty]");
  const gyos = [...document.querySelectorAll("[data-library-gyo]")];

  input.addEventListener("input", () => {
    const query = input.value.trim().toLowerCase().replace(/\s+/g, "");
    let visible = 0;
    books.forEach((book) => {
      const text = (book.dataset.libraryText || "").toLowerCase().replace(/\s+/g, "");
      const matches = !query || text.includes(query);
      book.hidden = !matches;
      if (matches) visible += 1;
    });
    gyos.forEach((g) => { g.hidden = !!query; });
    if (empty) empty.hidden = visible !== 0;
  });
})();

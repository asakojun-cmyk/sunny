(() => {
  const input = document.querySelector("[data-library-search]");
  if (!input) return;
  const books = [...document.querySelectorAll("[data-library-book]")];
  const empty = document.querySelector("[data-library-empty]");

  input.addEventListener("input", () => {
    const query = input.value.trim().toLowerCase().replace(/\s+/g, "");
    let visible = 0;
    books.forEach((book) => {
      const text = (book.dataset.libraryText || "").toLowerCase().replace(/\s+/g, "");
      const matches = !query || text.includes(query);
      book.hidden = !matches;
      if (matches) visible += 1;
    });
    if (empty) empty.hidden = visible !== 0;
  });
})();

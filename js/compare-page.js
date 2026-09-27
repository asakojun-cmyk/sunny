/* 養成学校の比較ページ — 表はHTMLに書いてあり、ここでは「表示する学校をしぼる」だけを行う
   何も選ばなければ全校を表示。選択は URL(?schools=a,b,c)とローカルストレージで保持 */
(function () {
  "use strict";
  var table = document.querySelector(".cmp");
  var checkboxes = document.querySelectorAll("[data-compare-checkbox]");
  var status = document.querySelector("[data-compare-status]");
  if (!table || !checkboxes.length) return;

  var store = window.kyarikonCompare;
  var MAX = store ? store.MAX : 3;
  var total = checkboxes.length;

  function currentSelection() {
    var params = new URLSearchParams(location.search);
    var fromUrl = (params.get("schools") || "").split(",").filter(function (s) {
      return s;
    });
    if (fromUrl.length) return fromUrl.slice(0, MAX);
    return store ? store.getSelection() : [];
  }

  function persist(sel) {
    if (store) store.setSelection(sel);
    var url = new URL(location.href);
    if (sel.length) url.searchParams.set("schools", sel.join(","));
    else url.searchParams.delete("schools");
    history.replaceState(null, "", url.toString());
  }

  function apply(sel) {
    checkboxes.forEach(function (cb) {
      cb.checked = sel.indexOf(cb.value) !== -1;
      cb.disabled = !cb.checked && sel.length >= MAX;
    });
    var showAll = sel.length === 0;
    table.querySelectorAll("[data-school]").forEach(function (cell) {
      cell.hidden = !showAll && sel.indexOf(cell.getAttribute("data-school")) === -1;
    });
    var shown = showAll ? total : sel.length;
    table.querySelectorAll(".cmp__group th").forEach(function (th) {
      th.colSpan = shown + 1;
    });
    if (status) {
      status.innerHTML = showAll
        ? total + "校すべてを表示しています。"
        : shown + "校にしぼって表示しています。 <button type=\"button\" class=\"cmp__reset\">すべて表示に戻す</button>";
      var reset = status.querySelector(".cmp__reset");
      if (reset) {
        reset.addEventListener("click", function () {
          persist([]);
          apply([]);
        });
      }
    }
  }

  checkboxes.forEach(function (cb) {
    cb.addEventListener("change", function () {
      var sel = [];
      checkboxes.forEach(function (c) {
        if (c.checked) sel.push(c.value);
      });
      sel = sel.slice(0, MAX);
      persist(sel);
      apply(sel);
    });
  });

  apply(currentSelection());
})();

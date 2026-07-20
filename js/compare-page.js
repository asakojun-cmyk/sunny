/* 学校比較ページ — 選んだ最大3校を項目ごとのカードで表示
   選択状態は URL クエリ(?schools=a,b,c)とローカルストレージで保持 */
(function () {
  "use strict";
  var result = document.querySelector("[data-compare-result]");
  var empty = document.querySelector("[data-compare-empty]");
  var checkboxes = document.querySelectorAll("[data-compare-checkbox]");
  if (!result || !checkboxes.length) return;

  var store = window.kyarikonCompare;
  var MAX = store ? store.MAX : 3;
  var data = null;

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      }[c];
    });
  }

  function currentSelection() {
    var params = new URLSearchParams(location.search);
    var fromUrl = (params.get("schools") || "")
      .split(",")
      .filter(function (s) {
        return s;
      });
    if (fromUrl.length) return fromUrl.slice(0, MAX);
    return store ? store.getSelection() : [];
  }

  function persist(sel) {
    if (store) store.setSelection(sel);
    var url = new URL(location.href);
    if (sel.length) {
      url.searchParams.set("schools", sel.join(","));
    } else {
      url.searchParams.delete("schools");
    }
    history.replaceState(null, "", url.toString());
  }

  function render(sel) {
    checkboxes.forEach(function (cb) {
      cb.checked = sel.indexOf(cb.value) !== -1;
      cb.disabled = !cb.checked && sel.length >= MAX;
    });
    if (!data || sel.length === 0) {
      result.innerHTML = "";
      if (empty) empty.hidden = false;
      return;
    }
    if (empty) empty.hidden = true;

    var chosen = sel
      .map(function (slug) {
        return data.schools.find(function (s) {
          return s.slug === slug;
        });
      })
      .filter(function (s) {
        return s;
      });

    var header =
      '<div class="compare-item"><p class="compare-item__label">選択中の学校</p>' +
      chosen
        .map(function (s) {
          return (
            '<div class="compare-item__row"><span class="compare-item__school">' +
            (s.isPr ? '<span class="pr-label">PR</span> ' : "") +
            escapeHtml(s.name) +
            '</span><span class="compare-item__value"><a href="/schools/' +
            escapeHtml(s.slug) +
            '/">詳細ページ</a> / <a href="' +
            escapeHtml(s.officialUrl) +
            '" rel="' + (s.isPr ? 'sponsored ' : '') + 'noopener nofollow" target="_blank">公式サイト' + (s.isPr ? '(広告)' : '') + '</a></span></div>'
          );
        })
        .join("") +
      "</div>";

    var items = data.itemOrder
      .map(function (label) {
        var rows = chosen
          .map(function (s) {
            var value = s.items[label] || "未確認・調査中";
            return (
              '<div class="compare-item__row"><span class="compare-item__school">' +
              escapeHtml(s.name) +
              '</span><span class="compare-item__value">' +
              escapeHtml(value) +
              "</span></div>"
            );
          })
          .join("");
        return (
          '<section class="compare-item"><h3 class="compare-item__label">' +
          escapeHtml(label) +
          "</h3>" +
          rows +
          "</section>"
        );
      })
      .join("");

    result.innerHTML = header + items;
  }

  checkboxes.forEach(function (cb) {
    cb.addEventListener("change", function () {
      var sel = [];
      checkboxes.forEach(function (c) {
        if (c.checked) sel.push(c.value);
      });
      sel = sel.slice(0, MAX);
      persist(sel);
      render(sel);
    });
  });

  // /schools/compare/ ページからの相対パス(サブパス配信・GitHub Pages対応)
  fetch("../../data/schools.json")
    .then(function (res) {
      return res.json();
    })
    .then(function (json) {
      data = json;
      render(currentSelection());
    })
    .catch(function () {
      if (empty) empty.textContent = "比較データを読み込めませんでした。";
    });
})();

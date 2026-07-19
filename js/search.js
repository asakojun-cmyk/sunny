/* サイト内検索 — /search-index.json をクライアント側で絞り込む */
(function () {
  "use strict";
  var input = document.getElementById("site-search-input");
  var status = document.querySelector("[data-search-status]");
  var list = document.querySelector("[data-search-results]");
  if (!input || !status || !list) return;

  var index = null;

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

  function normalize(s) {
    // カタカナ→ひらがな、全角英数の正規化、小文字化
    return String(s)
      .toLowerCase()
      .replace(/[ァ-ヶ]/g, function (c) {
        return String.fromCharCode(c.charCodeAt(0) - 0x60);
      })
      .replace(/\s+/g, "");
  }

  function search(query) {
    var q = normalize(query);
    if (!q) {
      status.textContent = "キーワードを入力してください。";
      list.innerHTML = "";
      return;
    }
    if (!index) return;
    var results = index.filter(function (doc) {
      var haystack = normalize(
        [doc.title, doc.reading || "", doc.description, (doc.keywords || []).join(" ")].join(" ")
      );
      return haystack.indexOf(q) !== -1;
    });
    status.textContent =
      results.length === 0
        ? "「" + query + "」に一致する内容は見つかりませんでした。別の言葉やひらがなでも試してみてください。"
        : results.length + "件見つかりました。";
    list.innerHTML = results
      .slice(0, 50)
      .map(function (doc) {
        return (
          '<li><a href="' +
          escapeHtml(doc.url.replace(/^\//, "../")) +
          '"><span class="search-result__type">' +
          escapeHtml(doc.type) +
          '</span><span class="search-result__title">' +
          escapeHtml(doc.title) +
          (doc.reading
            ? ' <small>(' + escapeHtml(doc.reading) + ")</small>"
            : "") +
          '</span><span class="search-result__desc">' +
          escapeHtml(doc.description) +
          "</span></a></li>"
        );
      })
      .join("");
  }

  function init() {
    var params = new URLSearchParams(location.search);
    var q = params.get("q") || "";
    if (q) input.value = q;

    // /search/ ページからの相対パス(サブパス配信・GitHub Pages対応)
    fetch("../search-index.json")
      .then(function (res) {
        return res.json();
      })
      .then(function (data) {
        index = data;
        if (input.value) search(input.value);
      })
      .catch(function () {
        status.textContent = "検索データを読み込めませんでした。";
      });

    var timer = null;
    input.addEventListener("input", function () {
      if (timer) clearTimeout(timer);
      timer = setTimeout(function () {
        search(input.value);
        var url = new URL(location.href);
        if (input.value) {
          url.searchParams.set("q", input.value);
        } else {
          url.searchParams.delete("q");
        }
        history.replaceState(null, "", url.toString());
      }, 200);
    });

    var form = input.closest("form");
    if (form) {
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        search(input.value);
      });
    }
  }

  init();
})();

/* キャリコンNOW掲示板: news-feed.json(毎朝自動更新)を読み込んで表示 */
(function () {
  "use strict";
  var root = document.querySelector("[data-now-board]");
  if (!root) return;
  var list = root.querySelector("[data-now-list]");
  var moreBtn = root.querySelector("[data-now-more]");
  var updatedEl = root.querySelector("[data-now-updated]");
  var FIRST = 8;

  function isNew(dateStr) {
    if (!dateStr) return false;
    var d = new Date(dateStr + "T00:00:00");
    return Date.now() - d.getTime() < 8 * 24 * 60 * 60 * 1000;
  }

  fetch("../news-feed.json", { cache: "no-store" })
    .then(function (r) { return r.json(); })
    .then(function (feed) {
      var items = (feed && feed.items) || [];
      if (!items.length) {
        list.innerHTML =
          '<li class="now-empty">掲示板の自動更新は、ただいま準備中。動き始めると、ここに厚生労働省の最新ニュースが毎朝はり出されるよ 📌</li>';
        return;
      }
      if (updatedEl && feed.updated) {
        updatedEl.textContent = "最終更新 " + feed.updated + "(毎朝自動更新)";
      }
      function render(count) {
        list.innerHTML = items
          .slice(0, count)
          .map(function (it) {
            return (
              '<li class="now-item">' +
              '<span class="now-item__date">' + (it.date || "") +
              (isNew(it.date) ? ' <b class="now-item__new">NEW</b>' : "") +
              "</span>" +
              '<a class="now-item__title" href="' + it.url + '" target="_blank" rel="noopener nofollow">' +
              it.title +
              '<span class="visually-hidden">(新しいタブで開きます)</span></a>' +
              '<span class="now-item__source">' + (it.source || "") + "</span>" +
              "</li>"
            );
          })
          .join("");
      }
      render(FIRST);
      if (moreBtn) {
        if (items.length <= FIRST) {
          moreBtn.hidden = true;
        } else {
          moreBtn.textContent = "もっと見る(全" + items.length + "件) ▼";
          moreBtn.addEventListener("click", function () {
            render(items.length);
            moreBtn.hidden = true;
          });
        }
      }
    })
    .catch(function () {
      list.innerHTML = '<li class="now-empty">ニュースの読み込みに失敗しちゃった。時間をおいて、また見にきてね。</li>';
    });
})();

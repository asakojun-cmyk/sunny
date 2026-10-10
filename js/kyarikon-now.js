/* キャリコンNOW掲示板: news-feed.json(毎朝自動更新)を読み込んで表示 */
(function () {
  "use strict";
  var root = document.querySelector("[data-now-board]");
  if (!root) return;
  var list = root.querySelector("[data-now-list]");
  var moreBtn = root.querySelector("[data-now-more]");
  var updatedEl = root.querySelector("[data-now-updated]");
  var FIRST = 8;

  /* 題名から、関係のうすいものを外し、「何の話か」の札を付ける。
   * 厚生労働省の配信には説明文がないので、題名の言葉だけで決めている(中身の要約ではない)。
   * 外す言葉は scripts/fetch-news.mjs の EXCLUDE と同じにしておく。 */
  var EXCLUDE = /記者会見|表彰|採用案内|採用情報|募集|功労者|ねんりんピック|食品|薬事|栄養|人口動態|石綿|医師|看護|薬剤|介護給付|医療/;
  var TAGS = [
    { id: "career", name: "学び・キャリコン", note: "キャリアコンサルタントの制度や、学び直し・職業訓練の話", re: /キャリアコンサル|キャリア形成|ジョブ・?カード|職業能力|人材開発|能力開発|教育訓練|職業訓練|リスキリング|技能検定/ },
    { id: "stat", name: "統計・調査", note: "賃金や雇用などの、数字の発表", re: /統計|調査|白書|有効求人倍率|労働力|速報|労働経済の分析/ },
    { id: "rule", name: "法律・制度", note: "法律や制度が変わる話", re: /制度変更|改正|施行|法律|指針|ガイドライン|最低賃金|助成金|給付金/ },
    { id: "meet", name: "会議・資料", note: "国の会議の開催案内と、その資料", re: /審議会|分科会|部会|検討会|委員会|研究会|議事録/ },
    { id: "info", name: "お知らせ", note: "そのほかのお知らせ", re: /./ }
  ];
  function tagOf(title) {
    for (var i = 0; i < TAGS.length; i++) if (TAGS[i].re.test(title)) return TAGS[i];
    return TAGS[TAGS.length - 1];
  }
  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function isNew(dateStr) {
    if (!dateStr) return false;
    var d = new Date(dateStr + "T00:00:00");
    return Date.now() - d.getTime() < 8 * 24 * 60 * 60 * 1000;
  }

  fetch("../news-feed.json", { cache: "no-store" })
    .then(function (r) { return r.json(); })
    .then(function (feed) {
      var all = ((feed && feed.items) || []).filter(function (it) {
        return it && it.title && !EXCLUDE.test(it.title);
      });
      all.forEach(function (it) {
        it.tag = tagOf(it.title);
      });
      var items = all;
      var shown = FIRST;
      if (!items.length) {
        list.innerHTML =
          '<li class="now-empty">掲示板の自動更新は、ただいま準備中。動き始めると、ここに厚生労働省の最新ニュースが毎朝はり出されるよ 📌</li>';
        return;
      }
      if (updatedEl && feed.updated) {
        updatedEl.textContent = "厚生労働省の新着から ・ 最終更新 " + feed.updated + "(毎朝自動更新)";
      }
      function render(count) {
        list.innerHTML = items
          .slice(0, count)
          .map(function (it) {
            return (
              '<li class="now-item">' +
              '<span class="now-item__date">' + esc(it.date || "") +
              (isNew(it.date) ? ' <b class="now-item__new">NEW</b>' : "") +
              ' <i class="now-tag now-tag--' + it.tag.id + '">' + it.tag.name + "</i>" +
              "</span>" +
              '<a class="now-item__title" href="' + esc(it.url) + '" target="_blank" rel="noopener nofollow">' +
              esc(it.title) +
              '<span class="visually-hidden">(新しいタブで開きます)</span></a>' +
              '<span class="now-item__source">' + (it.source || "") + "</span>" +
              "</li>"
            );
          })
          .join("");
      }
      function refresh() {
        render(shown);
        if (!moreBtn) return;
        moreBtn.hidden = items.length <= shown;
        moreBtn.textContent = "もっと見る(全" + items.length + "件) ▼";
      }
      if (moreBtn) {
        moreBtn.addEventListener("click", function () {
          shown = items.length;
          refresh();
        });
      }

      /* 札でしぼるボタン。件数が0の札は出さない */
      var bar = document.createElement("div");
      bar.className = "now-filter";
      bar.setAttribute("role", "group");
      bar.setAttribute("aria-label", "ニュースの種類でしぼる");
      var note = document.createElement("p");
      note.className = "now-filter__note";
      var chips = [{ id: "", name: "すべて", note: "関係のうすいお知らせ(記者会見・表彰・採用など)は外してあります" }].concat(
        TAGS.filter(function (t) {
          return all.some(function (it) {
            return it.tag === t;
          });
        })
      );
      bar.innerHTML = chips
        .map(function (c, i) {
          return '<button type="button" class="now-filter__chip" data-tag="' + c.id + '" aria-pressed="' + (i === 0) + '">' + c.name + "</button>";
        })
        .join("");
      note.textContent = chips[0].note;
      bar.addEventListener("click", function (e) {
        var btn = e.target.closest(".now-filter__chip");
        if (!btn) return;
        var id = btn.getAttribute("data-tag");
        [].forEach.call(bar.children, function (b) {
          b.setAttribute("aria-pressed", String(b === btn));
        });
        items = id
          ? all.filter(function (it) {
              return it.tag.id === id;
            })
          : all;
        shown = FIRST;
        note.textContent = chips.filter(function (c) {
          return c.id === id;
        })[0].note;
        refresh();
      });
      list.parentNode.insertBefore(bar, list);
      list.parentNode.insertBefore(note, list);
      refresh();
    })
    .catch(function () {
      list.innerHTML = '<li class="now-empty">ニュースの読み込みに失敗しちゃった。時間をおいて、また見にきてね。</li>';
    });
})();

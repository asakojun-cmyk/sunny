/* ＼NEW／のお知らせは、のせた日から1か月(30日)たったら自動で出さない。
   お知らせの <a class="newsflash"> に data-news-date="YYYY-MM-DD"(のせた日)をつける */
(function () {
  "use strict";
  var DAYS = 30;
  var today = new Date();
  today.setHours(0, 0, 0, 0);
  [].forEach.call(document.querySelectorAll("[data-news-date]"), function (el) {
    var p = el.getAttribute("data-news-date").split("-");
    var end = new Date(+p[0], +p[1] - 1, +p[2] + DAYS);
    if (today > end) el.remove();
  });
})();

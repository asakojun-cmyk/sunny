/* 30日の逆算プラン: 毎日の1問1答カレンダー。
   1問1答ドリルで解いた数(日付ごと)を読んで、30問で花丸、50問でキラキラ花丸をつける。
   記録はこの端末のブラウザにだけある(carepicnic-quiz-days-v1)。 */
(function () {
  "use strict";
  var root = document.querySelector("[data-dcal]");
  if (!root) return;
  var GOAL = 30, BIG = 50;
  var START = new Date(2026, 9, 16);  // 10月16日(金)
  var EXAM = new Date(2026, 10, 1);   // 11月1日(日) 第33回
  var days = {};
  try { days = JSON.parse(window.localStorage.getItem("carepicnic-quiz-days-v1") || "{}") || {}; } catch (_e) { days = {}; }

  function key(d) {
    return d.getFullYear() + "-" + ("0" + (d.getMonth() + 1)).slice(-2) + "-" + ("0" + d.getDate()).slice(-2);
  }
  var now = new Date();
  var today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  var WEEK = ["日", "月", "火", "水", "木", "金", "土"];

  var grid = document.createElement("div");
  grid.setAttribute("role", "list");
  grid.setAttribute("aria-label", "10月16日から11月1日までのカレンダー");
  grid.className = "dcal__grid";
  WEEK.forEach(function (w, i) {
    var h = document.createElement("div");
    h.className = "dcal__wd" + (i === 0 ? " is-sun" : i === 6 ? " is-sat" : "");
    h.setAttribute("aria-hidden", "true");
    h.textContent = w;
    grid.appendChild(h);
  });
  for (var b = 0; b < START.getDay(); b++) {
    var blank = document.createElement("div");
    blank.className = "dcal__blank";
    blank.setAttribute("aria-hidden", "true");
    grid.appendChild(blank);
  }

  var total = 0, maru = 0;
  for (var d = new Date(START); d <= EXAM; d.setDate(d.getDate() + 1)) {
    var li = document.createElement("div");
    li.setAttribute("role", "listitem");
    var n = days[key(d)] || 0;
    var isExam = d.getTime() === EXAM.getTime();
    var isToday = d.getTime() === today.getTime();
    var isFuture = d > today;
    var label = (d.getMonth() + 1) + "月" + d.getDate() + "日";
    li.className = "dcal__day";
    var mark = "", note = "";
    if (isExam) {
      li.className += " is-exam";
      mark = "試験";
      note = "本番の日";
    } else {
      total += n;
      if (n >= GOAL) maru++;
      if (n >= BIG) { li.className += " is-big"; mark = "💮"; note = n + "問。キラキラ花丸"; }
      else if (n >= GOAL) { li.className += " is-ok"; mark = "💮"; note = n + "問。花丸"; }
      else if (n > 0) { li.className += " is-some"; mark = n + "問"; note = n + "問"; }
      else if (isFuture) { li.className += " is-future"; note = "まだ先"; }
      else { note = "記録なし"; }
    }
    if (isToday) { li.className += " is-today"; note = "きょう。" + note; }
    li.setAttribute("aria-label", label + " " + note);
    li.innerHTML = '<span class="dcal__date" aria-hidden="true">' + (d.getDate() === 1 ? (d.getMonth() + 1) + "/" : "") + d.getDate() + "</span>" +
      '<span class="dcal__mark" aria-hidden="true">' + mark + "</span>" +
      (n >= BIG && !isExam ? '<span class="dcal__kira" aria-hidden="true">✨</span>' : "");
    grid.appendChild(li);
  }
  root.appendChild(grid);

  var todayN = days[key(today)] || 0;
  function set(sel, v) { var el = document.querySelector(sel); if (el) el.textContent = String(v); }
  set("[data-dcal-today]", todayN);
  set("[data-dcal-total]", total);
  set("[data-dcal-maru]", maru);
  var msg = document.querySelector("[data-dcal-msg]");
  if (msg) {
    if (today > EXAM) msg.textContent = "第33回の試験は終わりました。おつかれさまでした。";
    else if (today.getTime() === EXAM.getTime()) msg.textContent = "きょうが試験日。いってらっしゃい！";
    else if (todayN >= BIG) msg.textContent = "きょうはキラキラ花丸。すごい！";
    else if (todayN >= GOAL) msg.textContent = "きょうは花丸。あと" + (BIG - todayN) + "問でキラキラ花丸。";
    else msg.textContent = "きょうの花丸まで、あと" + (GOAL - todayN) + "問。";
  }

})();

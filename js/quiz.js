/* 用語・理論家ページの1問1答(○×と4択)。
 * 1ページに何問あってもよい。答えると正解数を数え、全部とき終わると結果と「もう一度」を出す。
 * 2026-10-18: 答えたあとは、いちばん上に「正解は 4」「正解は ○」を1回だけ出す。
 *             正解の選択肢に ✓、まちがえて選んだものに ✗ をつける。最後にサニー先生のひとこと。 */
(function () {
  "use strict";
  var boxes = Array.prototype.slice.call(document.querySelectorAll("[data-quiz]"));
  if (!boxes.length) return;

  /* サニー先生の画像: このスクリプトの場所(…/js/quiz.js)から img/parts/ を探す */
  var SUNNY_SRC = (function () {
    var s = document.currentScript || document.querySelector('script[src*="js/quiz.js"]');
    try { return new URL("../img/parts/06_sun_character.webp", s && s.src ? s.src : location.href).href; }
    catch (_e) { return ""; }
  })();

  var groups = [];
  boxes.forEach(function (box) {
    var parent = box.parentNode;
    var g = null;
    for (var i = 0; i < groups.length; i++) if (groups[i].parent === parent) g = groups[i];
    if (!g) { g = { parent: parent, boxes: [], done: 0, ok: 0, score: parent.querySelector("[data-quiz-score]") }; groups.push(g); }
    g.boxes.push(box);
  });

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  function showScore(g) {
    if (!g.score || g.boxes.length < 2) return;
    g.score.hidden = false;
    if (g.done < g.boxes.length) {
      g.score.classList.remove("is-final");
      g.score.textContent = g.boxes.length + "問中 " + g.done + "問とき終わりました";
      return;
    }
    var all = g.ok === g.boxes.length;
    g.score.textContent = "";
    g.score.classList.add("is-final");
    g.score.appendChild(el("b", "quiz-score__num", g.boxes.length + "問中 " + g.ok + "問 正解"));
    var say = el("span", "quiz-score__sunny");
    if (SUNNY_SRC) {
      var img = el("img", "quiz-score__face");
      img.src = SUNNY_SRC; img.width = 48; img.height = 48; img.alt = "サニー先生"; img.decoding = "async";
      say.appendChild(img);
    }
    var bubble = el("span", "quiz-score__say");
    bubble.appendChild(el("span", "quiz-score__who", "サニー先生"));
    bubble.appendChild(document.createTextNode(all ? "満点！すごいね。" : "まちがえたところを、読みなおそう。"));
    say.appendChild(bubble);
    g.score.appendChild(say);
    var btn = el("button", "quiz-score__retry", "もう一度とく");
    btn.type = "button";
    btn.addEventListener("click", function () { g.boxes.forEach(function (bx) { bx.__reset(); }); g.done = 0; g.ok = 0; g.score.hidden = true; g.score.classList.remove("is-final"); g.boxes[0].scrollIntoView({ behavior: "smooth", block: "center" }); });
    g.score.appendChild(btn);
  }

  /* 解説の本文を組み立てる。
     ○×: 元の文の先頭「正解は ○ — 」は上の見出しと重なるので外す。
     4択: 「ほかのNつは誤りです。・…・…」の部分は、読みやすいように箇条書きにする。
          (どの選択肢の説明かは元データに書かれていないので、番号はつけない) */
  function buildBody(text, isChoice) {
    var frag = document.createDocumentFragment();
    var t = text.replace(/\s+/g, " ").trim();
    if (!isChoice) {
      t = t.replace(/^正解は\s*[○×]\s*[—―-]\s*/, "");
      frag.appendChild(el("span", "quiz-box__exp", t));
      return frag;
    }
    var m = /ほかの\s*\d+\s*つは誤りです。/.exec(t);
    if (!m) { frag.appendChild(el("span", "quiz-box__exp", t)); return frag; }
    var head = t.slice(0, m.index).trim();
    var rest = t.slice(m.index + m[0].length);
    var parts = rest.replace(/^\s*・/, "").split(/。\s*・/);
    var items = parts.map(function (s, i) { s = s.trim(); return s && i < parts.length - 1 ? s + "。" : s; }).filter(Boolean);
    if (head) frag.appendChild(el("span", "quiz-box__exp", head));
    if (items.length < 2) { frag.appendChild(el("span", "quiz-box__exp", m[0] + rest)); return frag; }
    frag.appendChild(el("span", "quiz-box__others-label", m[0].replace(/\s+/g, "")));
    var ul = el("ul", "quiz-box__others");
    items.forEach(function (s) { ul.appendChild(el("li", null, s)); });
    frag.appendChild(ul);
    return frag;
  }

  groups.forEach(function (g) {
    g.boxes.forEach(function (box) {
      var result = box.querySelector("[data-quiz-result]");
      if (!result) return;
      var original = result.textContent;
      var originalHTML = result.innerHTML;
      var answered = false;
      var btns = Array.prototype.slice.call(box.querySelectorAll("[data-quiz-choice],[data-quiz-answer]"));
      var qEl = box.querySelector(".quiz-box__question");
      var futekisetsu = qEl && /不適切/.test(qEl.textContent);

      /* key: 「4」「○」など正解の表し方 */
      function finish(ok, picked, right, key, isChoice) {
        if (answered) return;
        answered = true;
        btns.forEach(function (b) { b.disabled = true; });
        if (picked) { picked.classList.add(ok ? "is-correct" : "is-wrong"); picked.classList.add("is-picked"); }
        if (right) right.classList.add("is-correct");
        box.classList.add(ok ? "is-ok" : "is-ng", "is-answered");
        result.textContent = "";
        var head = el("span", "quiz-box__key");
        head.appendChild(el("b", "quiz-box__keyans", "正解は " + key));
        if (isChoice && futekisetsu) head.appendChild(el("span", "quiz-box__keynote", "(これがまちがっている文)"));
        head.appendChild(el("span", "quiz-box__verdict " + (ok ? "is-ok" : "is-ng"), ok ? "あたり！" : "おしい！"));
        result.appendChild(head);
        result.appendChild(buildBody(original, isChoice));
        result.hidden = false;
        g.done++; if (ok) g.ok++;
        showScore(g);
      }
      box.__reset = function () {
        answered = false;
        btns.forEach(function (b) { b.disabled = false; b.classList.remove("is-correct", "is-wrong", "is-picked"); });
        box.classList.remove("is-ok", "is-ng", "is-answered");
        result.innerHTML = originalHTML;
        result.hidden = true;
      };

      var choices = Array.prototype.slice.call(box.querySelectorAll("[data-quiz-choice]"));
      if (choices.length) {
        var correctIdx = parseInt(box.getAttribute("data-correct"), 10);
        choices.forEach(function (btn, i) {
          btn.addEventListener("click", function () { finish(i === correctIdx, btn, choices[correctIdx], String(correctIdx + 1), true); });
        });
        return;
      }
      var answer = box.getAttribute("data-answer") === "true";
      var ans = Array.prototype.slice.call(box.querySelectorAll("[data-quiz-answer]"));
      ans.forEach(function (btn) {
        btn.setAttribute("aria-label", btn.getAttribute("data-quiz-answer") === "true" ? "○(正しい)" : "×(まちがい)");
        btn.addEventListener("click", function () {
          var chosen = btn.getAttribute("data-quiz-answer") === "true";
          var right = ans.filter(function (b) { return (b.getAttribute("data-quiz-answer") === "true") === answer; })[0];
          finish(chosen === answer, btn, right, answer ? "○" : "×", false);
        });
      });
    });
  });
})();

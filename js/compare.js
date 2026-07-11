/* 「比較に追加」ボタンと比較バー(選択はローカルストレージに保持、最大3校) */
(function () {
  "use strict";
  var KEY = "kyarikon-compare-schools";
  var MAX = 3;

  function getSelection() {
    try {
      var raw = localStorage.getItem(KEY);
      var arr = raw ? JSON.parse(raw) : [];
      return Array.isArray(arr) ? arr.slice(0, MAX) : [];
    } catch (_e) {
      return [];
    }
  }

  function setSelection(arr) {
    try {
      localStorage.setItem(KEY, JSON.stringify(arr.slice(0, MAX)));
    } catch (_e) {
      /* プライベートモードなどでは保持しない */
    }
  }

  window.kyarikonCompare = { getSelection: getSelection, setSelection: setSelection, MAX: MAX };

  var buttons = document.querySelectorAll("[data-compare-add]");
  var bar = document.querySelector("[data-compare-bar]");
  var count = document.querySelector("[data-compare-count]");
  var clear = document.querySelector("[data-compare-clear]");

  function render() {
    var sel = getSelection();
    buttons.forEach(function (btn) {
      var slug = btn.getAttribute("data-compare-add");
      var added = sel.indexOf(slug) !== -1;
      btn.textContent = added ? "比較から外す" : "比較に追加";
      btn.setAttribute("aria-pressed", added ? "true" : "false");
    });
    if (bar) {
      bar.hidden = sel.length === 0;
      if (count) count.textContent = String(sel.length);
    }
  }

  buttons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var slug = btn.getAttribute("data-compare-add");
      var sel = getSelection();
      var i = sel.indexOf(slug);
      if (i !== -1) {
        sel.splice(i, 1);
      } else {
        if (sel.length >= MAX) {
          btn.textContent = "3校まで選べます";
          setTimeout(render, 1500);
          return;
        }
        sel.push(slug);
      }
      setSelection(sel);
      render();
    });
  });

  if (clear) {
    clear.addEventListener("click", function () {
      setSelection([]);
      render();
    });
  }

  render();
})();

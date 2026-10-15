/* guide-check.js — ガイドのチェックリストに、実際にチェックを入れられるようにする(2026-10-15)
   チェックした内容は、そのブラウザだけに残す(localStorage)。使えない環境でも、チェック自体はできる */
(function () {
  function load(key) { try { return JSON.parse(localStorage.getItem(key) || '[]'); } catch (e) { return []; } }
  function save(key, val) { try { localStorage.setItem(key, JSON.stringify(val)); } catch (e) {} }
  document.querySelectorAll('[data-gk-check]').forEach(function (list) {
    var key = 'gk-check:' + location.pathname + ':' + list.getAttribute('data-gk-check');
    var boxes = list.querySelectorAll('input[type=checkbox]');
    var count = document.getElementById(list.getAttribute('data-gk-count'));
    var done = load(key);
    boxes.forEach(function (b, i) { b.checked = done.indexOf(i) > -1; });
    function update() {
      var on = [];
      boxes.forEach(function (b, i) { if (b.checked) on.push(i); });
      save(key, on);
      if (count) {
        var label = list.getAttribute('data-gk-label') || '確かめた';
        var all = on.length === boxes.length && label === '確かめた';
        count.textContent = all
          ? 'ぜんぶ確かめられました！ (' + on.length + ' / ' + boxes.length + ')'
          : on.length + ' / ' + boxes.length + ' ' + label;
        count.classList.toggle('is-done', all);
      }
    }
    boxes.forEach(function (b) { b.addEventListener('change', update); });
    update();
  });
})();

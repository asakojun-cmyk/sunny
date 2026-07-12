/* 給付金の実質負担額かんたん計算機(概算・年間上限を反映) */
(function () {
  var root = document.getElementById("kyufu-calc");
  if (!root) return;
  var input = document.getElementById("kyufu-fee");
  var CAPS = { 50: 400000, 70: 560000, 80: 640000 };

  function yen(n) {
    return n.toLocaleString("ja-JP") + "円";
  }

  function render() {
    var fee = parseInt(input.value, 10);
    if (isNaN(fee) || fee < 0) fee = 0;
    [50, 70, 80].forEach(function (rate) {
      var back = Math.min(Math.floor((fee * rate) / 100), CAPS[rate]);
      var self = Math.max(fee - back, 0);
      root.querySelector('[data-kyufu="' + rate + '"]').textContent = yen(back);
      root.querySelector('[data-jifu="' + rate + '"]').textContent = yen(self);
    });
  }

  input.addEventListener("input", render);
  render();
})();

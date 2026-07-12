/* 動的フローチャート: ステップをタップすると説明パネルが切り替わる */
(function () {
  var charts = document.querySelectorAll("[data-flowchart]");
  charts.forEach(function (chart) {
    var steps = chart.querySelectorAll("[data-flow-step]");
    var panels = chart.querySelectorAll("[data-flow-panel]");
    steps.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var i = btn.getAttribute("data-flow-step");
        steps.forEach(function (b) {
          b.classList.toggle("is-active", b === btn);
        });
        panels.forEach(function (p) {
          p.hidden = p.getAttribute("data-flow-panel") !== i;
        });
      });
    });
  });
})();

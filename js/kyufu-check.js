/* 専門実践教育訓練給付金:対象になりそうかの目安チェック(最終判定はハローワーク) */
(function () {
  "use strict";
  var root = document.getElementById("kyufu-check");
  if (!root) return;
  var p = document.getElementById("kc-period"),
    s = document.getElementById("kc-status"),
    u = document.getElementById("kc-used"),
    go = document.getElementById("kc-go"),
    out = document.getElementById("kc-out");

  function show(kind, title, lines) {
    out.className = "kc-out kc-out--" + kind;
    out.innerHTML = "";
    var h = document.createElement("p");
    h.className = "kc-out__title";
    h.textContent = title;
    out.appendChild(h);
    lines.forEach(function (t) {
      var e = document.createElement("p");
      e.textContent = t;
      out.appendChild(e);
    });
    var last = document.createElement("p");
    last.className = "kc-out__note";
    last.textContent = "これは目安です。対象になるかどうかは、ハローワークで確認できます。";
    out.appendChild(last);
    out.hidden = false;
    if (typeof window.gtag === "function") window.gtag("event", "kyufu_check", { result: kind });
  }

  var TOKUTEN = root.getAttribute("data-tokuten") || "";

  go.addEventListener("click", function () {
    if (!p.value || !s.value || !u.value) {
      out.className = "kc-out kc-out--ask";
      out.textContent = "3つとも選んでから、もう一度押してください。";
      out.hidden = false;
      return;
    }
    var need = u.value === "never" ? 2 : 3;
    var years = { none: 0, lt2: 1, y2: 2, y3: 3 }[p.value];
    var no = [];
    if (u.value === "in3") no.push("前に教育訓練給付金を受けてから3年たっていないと、支給されません。");
    if (years < need) {
      no.push(
        years === 0
          ? "雇用保険に入っていた期間がないと、対象になりません。"
          : "雇用保険に入っていた期間が、" + need + "年以上必要です。"
      );
    }
    if (no.length) {
      if (TOKUTEN) no.push(TOKUTEN);
      show("no", "対象にならない可能性が高いです", no);
      return;
    }
    if (s.value === "over1") {
      show("maybe", "そのままでは対象になりませんが、確認をおすすめします", [
        "仕事を辞めてから受講開始まで、1年以内であることが条件です。",
        "ただし、妊娠・出産・育児などで受講を始められなかった人は、ハローワークで手続きをしていれば、この期間を最長20年まで延ばせる制度があります。"
      ]);
      return;
    }
    show("yes", "対象になる可能性があります", [
      "受講開始日の2週間前までに、ハローワークで手続きが必要です。期限を過ぎると受け取れません。",
      "説明会に参加したら、早めにハローワークへ相談しておくと安心です。"
    ]);
  });
})();

/* きょうの、ちいさな一歩: 書き込み→カード画像保存(すべて端末内で完結) */
(function () {
  var box = document.querySelector("[data-fill-step]");
  if (!box) return;
  var input = box.querySelector("[data-fill-input]");
  var saveBtn = box.querySelector("[data-fill-save]");
  var shareA = box.querySelector("[data-fill-share]");
  var canvas = box.querySelector("[data-fill-canvas]");
  var sentence = box.querySelector(".fill-step__sentence");
  var before = sentence ? sentence.childNodes[0].textContent : "";

  function wrapText(ctx, text, maxWidth) {
    var lines = [];
    var line = "";
    for (var i = 0; i < text.length; i++) {
      var test = line + text[i];
      if (ctx.measureText(test).width > maxWidth && line.length > 0) {
        lines.push(line);
        line = text[i];
      } else {
        line = test;
      }
    }
    if (line) lines.push(line);
    return lines;
  }

  function drawCard(word) {
    var ctx = canvas.getContext("2d");
    var W = 1080, H = 1080;
    // 背景
    ctx.fillStyle = "#fffdf8";
    ctx.fillRect(0, 0, W, H);
    // ふち
    ctx.strokeStyle = "#e9e2d2";
    ctx.lineWidth = 6;
    ctx.strokeRect(40, 40, W - 80, H - 80);
    // 太陽
    ctx.fillStyle = "#f8e45c";
    ctx.beginPath();
    ctx.arc(W - 150, 150, 52, 0, Math.PI * 2);
    ctx.fill();
    // 見出し
    ctx.fillStyle = "#9a917f";
    ctx.font = "600 34px 'Hiragino Kaku Gothic ProN','Yu Gothic',sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("わたしのキャリア・アンカー", W / 2, 200);
    // 本文(前半)
    ctx.fillStyle = "#5c5344";
    ctx.font = "44px 'Hiragino Kaku Gothic ProN','Yu Gothic',sans-serif";
    var bodyLines = wrapText(ctx, before, W - 260);
    var y = 330;
    for (var i = 0; i < bodyLines.length; i++) {
      ctx.fillText(bodyLines[i], W / 2, y);
      y += 72;
    }
    // ことば(強調)
    y += 40;
    ctx.fillStyle = "#d95f3b";
    ctx.font = "700 76px 'Hiragino Kaku Gothic ProN','Yu Gothic',sans-serif";
    var wordLines = wrapText(ctx, "「" + word + "」", W - 200);
    for (var j = 0; j < wordLines.length; j++) {
      ctx.fillText(wordLines[j], W / 2, y);
      y += 100;
    }
    // 下線がわりの波
    ctx.strokeStyle = "#f8e45c";
    ctx.lineWidth = 8;
    ctx.beginPath();
    ctx.moveTo(W / 2 - 200, y - 40);
    ctx.quadraticCurveTo(W / 2, y - 20, W / 2 + 200, y - 40);
    ctx.stroke();
    // 草
    ctx.fillStyle = "#f1f6e5";
    ctx.beginPath();
    ctx.ellipse(W / 2, H - 40, 640, 130, 0, 0, Math.PI * 2);
    ctx.fill();
    // クレジット
    ctx.fillStyle = "#9a917f";
    ctx.font = "30px 'Hiragino Kaku Gothic ProN','Yu Gothic',sans-serif";
    ctx.fillText("キャリコン学びピクニック", W / 2, H - 120);
    ctx.font = "26px 'Hiragino Kaku Gothic ProN','Yu Gothic',sans-serif";
    ctx.fillText("carepicnic.com", W / 2, H - 78);
  }

  saveBtn.addEventListener("click", function () {
    var word = (input.value || "").trim();
    if (!word) {
      input.focus();
      input.placeholder = "ここに一言だけ書いてみてね";
      return;
    }
    drawCard(word);
    var a = document.createElement("a");
    a.download = "watashi-no-anchor.png";
    a.href = canvas.toDataURL("image/png");
    a.click();
    // Xシェアボタンを出す
    var text =
      "私が仕事や活動を選ぶとき、これだけは手放したくないものは、「" +
      word +
      "」。 #キャリコン学びピクニック";
    shareA.href =
      "https://twitter.com/intent/tweet?text=" +
      encodeURIComponent(text) +
      "&url=" +
      encodeURIComponent(location.href);
    shareA.hidden = false;
    saveBtn.textContent = "もう一度保存する";
  });
})();

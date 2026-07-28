/* きょうの、ちいさな一歩: 書き込み→アンカーカード保存/シェア */
(function () {
  var box = document.querySelector("[data-fill-step]");
  if (!box) return;
  var input = box.querySelector("[data-fill-input]");
  var saveBtn = box.querySelector("[data-fill-save]");
  var shareA = box.querySelector("[data-fill-share]");
  var canvas = box.querySelector("[data-fill-canvas]");
  var preview = box.querySelector("[data-fill-preview]");
  var sentence = box.querySelector(".fill-step__sentence");
  var before = sentence ? sentence.childNodes[0].textContent : "";

  /* --- Xシェア: 入力のたびにリンクを更新(保存しなくても押せる) --- */
  function updateShare() {
    var word = (input.value || "").trim();
    var text = word
      ? before + "「" + word + "」。 #キャリコン学びピクニック"
      : "自分のキャリア・アンカー、考えてみた。 #キャリコン学びピクニック";
    shareA.href =
      "https://twitter.com/intent/tweet?text=" +
      encodeURIComponent(text) +
      "&url=" +
      encodeURIComponent(location.href);
  }
  input.addEventListener("input", updateShare);
  updateShare();

  /* --- サイトのイラストパーツを読み込んでカードを描く --- */
  var PARTS = {
    sun: "/img/parts/06_sun_character.png",
    cloud: "/img/parts/28_small_cloud_motif.png",
    flowersL: "/img/parts/23_flowers_left_group.png",
    flowersR: "/img/parts/25_flowers_right_group.png",
  };
  var imgs = {};
  var loaded = null;
  function loadParts() {
    if (loaded) return loaded;
    loaded = Promise.all(
      Object.keys(PARTS).map(function (k) {
        return new Promise(function (res) {
          var im = new window.Image();
          im.onload = function () { imgs[k] = im; res(true); };
          im.onerror = function () { res(false); };
          im.src = PARTS[k];
        });
      })
    );
    return loaded;
  }

  function roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }

  function wrapText(ctx, text, maxWidth) {
    var lines = [], line = "";
    for (var i = 0; i < text.length; i++) {
      var t = line + text[i];
      if (ctx.measureText(t).width > maxWidth && line.length > 0) {
        lines.push(line); line = text[i];
      } else line = t;
    }
    if (line) lines.push(line);
    return lines;
  }

  function drawImageScaled(ctx, im, x, y, w) {
    if (!im) return;
    var h = im.height * (w / im.width);
    ctx.drawImage(im, x, y, w, h);
  }

  function drawCard(word) {
    var ctx = canvas.getContext("2d");
    var W = 1080, H = 1080;
    var FONT = "'Hiragino Kaku Gothic ProN','Yu Gothic',sans-serif";

    /* 背景 */
    ctx.fillStyle = "#fffdf8";
    ctx.fillRect(0, 0, W, H);

    /* 空のニュアンス */
    ctx.fillStyle = "#f2f8fb";
    ctx.beginPath();
    ctx.ellipse(W / 2, -140, 900, 330, 0, 0, Math.PI * 2);
    ctx.fill();

    /* 草原(下部) */
    ctx.fillStyle = "#eef3dd";
    ctx.beginPath();
    ctx.ellipse(W / 2, H + 130, 900, 330, 0, 0, Math.PI * 2);
    ctx.fill();

    /* 白いカード面 */
    ctx.save();
    ctx.shadowColor = "rgba(90,80,60,0.10)";
    ctx.shadowBlur = 30;
    ctx.shadowOffsetY = 10;
    ctx.fillStyle = "#ffffff";
    roundRect(ctx, 90, 200, W - 180, 640, 36);
    ctx.fill();
    ctx.restore();
    ctx.strokeStyle = "#efe8d8";
    ctx.lineWidth = 3;
    roundRect(ctx, 90, 200, W - 180, 640, 36);
    ctx.stroke();

    /* パーツ: 雲(左上)・太陽(右上)・花(下両脇) */
    drawImageScaled(ctx, imgs.cloud, 96, 84, 190);
    drawImageScaled(ctx, imgs.sun, W - 300, 44, 220);
    drawImageScaled(ctx, imgs.flowersL, 60, H - 250, 250);
    drawImageScaled(ctx, imgs.flowersR, W - 310, H - 240, 250);

    /* 見出し */
    ctx.textAlign = "center";
    ctx.fillStyle = "#b3a98f";
    ctx.font = "600 26px " + FONT;
    try { ctx.letterSpacing = "8px"; } catch (_e) { /* 非対応環境は無視 */ }
    ctx.fillText("MY CAREER ANCHOR", W / 2, 282);
    try { ctx.letterSpacing = "0px"; } catch (_e) { /* 非対応環境は無視 */ }
    ctx.fillStyle = "#5c5344";
    ctx.font = "700 44px " + FONT;
    ctx.fillText("わたしのキャリア・アンカー", W / 2, 344);

    /* 黄色い点々の飾り */
    ctx.fillStyle = "#f2dd6e";
    [-40, 0, 40].forEach(function (dx) {
      ctx.beginPath();
      ctx.arc(W / 2 + dx, 386, 6, 0, Math.PI * 2);
      ctx.fill();
    });

    /* 本文 */
    ctx.fillStyle = "#7a7263";
    ctx.font = "34px " + FONT;
    var bodyLines = wrapText(ctx, before, W - 340);
    var y = 456;
    bodyLines.forEach(function (l) {
      ctx.fillText(l, W / 2, y);
      y += 56;
    });

    /* ことばのリボン(テラコッタ) */
    var display = "「" + word + "」";
    var size = 62;
    ctx.font = "700 " + size + "px " + FONT;
    while (ctx.measureText(display).width > W - 330 && size > 34) {
      size -= 4;
      ctx.font = "700 " + size + "px " + FONT;
    }
    var tw = ctx.measureText(display).width;
    var rw = Math.min(W - 280, tw + 90);
    var rh = size + 58;
    var ry = y + 8;
    ctx.save();
    ctx.shadowColor = "rgba(217,95,59,0.28)";
    ctx.shadowBlur = 18;
    ctx.shadowOffsetY = 6;
    ctx.fillStyle = "#e2694a";
    roundRect(ctx, W / 2 - rw / 2, ry, rw, rh, rh / 2);
    ctx.fill();
    ctx.restore();
    ctx.fillStyle = "#ffffff";
    ctx.fillText(display, W / 2, ry + rh / 2 + size * 0.35);

    /* クレジット */
    ctx.fillStyle = "#8f8672";
    ctx.font = "600 30px " + FONT;
    ctx.fillText("キャリコン学びピクニック", W / 2, H - 118);
    ctx.fillStyle = "#b3a98f";
    ctx.font = "26px " + FONT;
    ctx.fillText("carepicnic.com", W / 2, H - 74);
  }

  saveBtn.addEventListener("click", function () {
    var word = (input.value || "").trim();
    if (!word) {
      input.focus();
      input.placeholder = "ここに一言だけ書いてみてね";
      return;
    }
    saveBtn.disabled = true;
    loadParts().then(function () {
      drawCard(word);
      var url = canvas.toDataURL("image/png");
      preview.src = url;
      preview.hidden = false;
      var a = document.createElement("a");
      a.download = "watashi-no-anchor.png";
      a.href = url;
      document.body.appendChild(a);
      a.click();
      a.remove();
      saveBtn.disabled = false;
      saveBtn.textContent = "書き直して、もう一度保存";
    });
  });
})();

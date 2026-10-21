/* 論述の模擬試験: 回の選択・タイマー・下書きの保存・自動採点・解説
   形式と解答用紙の行数は、協議会の公開資料に合わせている(picnic-docs/論述対策_公式データベース)。 */
(function () {
  "use strict";
  var CASES = window.RONJUTSU_CASES || [];
  var root = document.querySelector("[data-rm]");
  if (!root || !CASES.length) return;

  var LIMIT = 50 * 60; // 本番と同じ50分
  var PER_LINE = 40;   // 解答用紙1行に書ける字数の目安(公式の決まりはない。当サイトの目安)
  var QS = [
    { k: "q1", no: "設問1", short: "設問1", pt: 10, lines: 2, ask: "事例記録の「相談の概要」【略A】に当たる、相談者がこの面談で相談したいことは何か。事例記録を手がかりに書いてください。" },
    { k: "q2", no: "設問2", short: "設問2", pt: 10, lines: 2, ask: "事例記録の【下線B】について、この事例を担当したキャリアコンサルタントは、どのような意図で応答したと考えますか。" },
    { k: "q3a", no: "設問3 ①問題", short: "設問3①", pt: 10, lines: 2, ask: "あなたが考える、相談者の問題(①)は何ですか。" },
    { k: "q3b", no: "設問3 ②その根拠", short: "設問3②", pt: 10, lines: 3, ask: "①の根拠(②)を、相談者の言動を通じて、具体的に書いてください。" },
    { k: "q4", no: "設問4", short: "設問4", pt: 10, lines: 6, ask: "設問3で答えた内容をふまえて、今後あなたがこのケースを担当するとしたら、どのような方針でキャリアコンサルティングを進めていきますか。" }
  ];
  QS.forEach(function (q) { q.max = q.lines * PER_LINE; });

  /* どの回にも共通する観点のことば */
  var RE = {
    omoi: "思い込|決めつけ|固定観念|とらわれ|一面的|信じ込|ビリーフ|と決めて|と考えて|と思って|と感じて|と捉えて|と信じて|だけで判断|しか見て|しかないと|と比べて|比べて(自分|自身)?を?低く|振り回され|左右され",
    fusoku: "不足|ていない|ておらず|できない|分から|わから|乏し|不十分|抱え|曖昧|あいまい|低|ないまま",
    hataraki: "受け止|受けと|伝え返|返す|返し|言いかえ|言い換え|反映|要約|確かめ|確認|明確|質問|尋ね|たずね|問いかけ|引き出",
    nerai: "見つめ直|見直|考え直|向き合|振り返",
    kankei: "信頼関係|ラポール|関係構築|関係を築|受け止め|受けとめ|傾聴|受容|共感|寄り添",
    junban: "まず.*(次に|つぎに|そのうえ|その上|その後|さらに|あわせて|最後|最終)",
    jiko: "自己決定|自分で|自ら|自身で|主体的|納得|意思決定",
    q1mitate: "自己理解|仕事理解|が不足|思い込み|決めつけ|見立て",
    shiji: "すすめ|勧め|説得|指示(する|し)|べきだと(伝|助言)|(辞め|続け|引き受け|断|承諾)(る)?よう(に)?(伝|促|助言|話)"
  };
  var HINT = {
    jokyo: "「何があって来たのか」を、1つ入れます。",
    kimochi: "相談者自身のことばで、気持ちを入れます。",
    chushin: "相談したいことは、相談者の最後の発言にまとまっています。ここが抜けると、主訴になりません。",
    q1form: "文の終わりを「〜について相談したい。」にすると、設問に答えた形になります。",
    q1pen: "設問1は、相談者が相談したいこと(主訴)です。「自己理解が不足」のような見立ては、設問3に書きます。",
    uketa: "下線Bが、相談者のどのことば・気持ちを受け止めたのかを書きます。",
    hataraki: "「受け止めて伝え返す」「言いかえて確かめる」「開かれた質問で引き出す」のように、応答のはたらきを書きます。",
    nerai: "受け止めた先で、相談者に何に気づいてほしかったのかまで書きます。",
    q2form: "文の終わりを「〜できるよう促すため。」にします。",
    omoi: "相談者が、確かめないまま決めていること(思い込み)を、その事例のことばで書きます。",
    mitate: "相談者に足りていない理解や情報は何かを書きます。",
    omoiQ: "思い込みを示す相談者の発言を挙げます。「 」でそのまま引用すると、いちばん確かです。",
    mitateQ: "見立ての根拠になる相談者の発言を挙げます。「 」でそのまま引用すると、いちばん確かです。",
    two: "問題を2つ挙げたら、根拠も2つ。(a)(b)の記号を、①問題と②根拠でそろえます。",
    q3form: "文の終わりを「〜と述べているため。」にします。",
    kankei: "方針の1文目は、気持ちの受け止めと信頼関係です(出題範囲の「相談場面の設定」)。",
    hOmoi: "設問3で挙げた思い込みに、「捉え方を見直す」「事実で確かめる」支援を対応させます。",
    hMitate: "設問3で挙げた見立てに、「振り返る・言葉にする」「情報を集める・確かめる」支援を対応させます。",
    junban: "「まず」「次に」「そのうえで」を文の頭に置いて、進める順番を示します。",
    jiko: "決めるのは相談者です。相談者が自分で決められるよう支援する、という方向を入れます。",
    q4pen: "決めるのは相談者です。「すすめる」「説得する」「〜するよう伝える」は、キャリコンが答えを決める書き方になります。"
  };

  var $ = function (s, el) { return (el || root).querySelector(s); };
  var $$ = function (s, el) { return [].slice.call((el || root).querySelectorAll(s)); };
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function norm(s) { return String(s || "").normalize("NFKC").replace(/\s+/g, ""); }
  function count(s) { return String(s || "").replace(/\s+/g, "").length; }
  /* 解答用紙の行に入る分だけを残す(行の外に書いたものは採点されないため) */
  function inLines(s, max) {
    var n = 0, out = "", str = String(s || "");
    for (var i = 0; i < str.length; i++) {
      if (!/\s/.test(str[i])) { n++; if (n > max) break; }
      out += str[i];
    }
    return out;
  }
  function store(key, val) {
    try {
      if (val === undefined) { var v = localStorage.getItem("rm2:" + key); return v ? JSON.parse(v) : null; }
      if (val === null) localStorage.removeItem("rm2:" + key); else localStorage.setItem("rm2:" + key, JSON.stringify(val));
    } catch (e) { /* 保存できない環境でも、そのまま動かす */ }
    return null;
  }
  function track(name, value) {
    try { if (typeof window.gtag === "function") window.gtag("event", name, value === undefined ? {} : { value: value }); } catch (e) { /* 計測は失敗しても止めない */ }
  }

  /* ---------- 採点 ---------- */
  function caseText(c) { return norm(c.talk.map(function (t) { return t[1]; }).join("")); }
  /* 解答の「 」のうち、事例に実際にあることばだけを返す */
  function quotes(answer, c) {
    var src = caseText(c), out = [], m, re = /「([^」]{4,})」/g, a = String(answer || "").normalize("NFKC");
    while ((m = re.exec(a))) {
      var q = m[1].replace(/\s+/g, ""), w = Math.min(5, q.length);
      for (var i = 0; i + w <= q.length; i++) { if (src.indexOf(q.slice(i, i + w)) !== -1) { out.push(q); break; } }
    }
    return out;
  }
  function has(text, spec) { return [].concat(spec).every(function (r) { return new RegExp(r).test(text); }); }
  /* 解答例とどれくらい近いか(2文字ずつの重なり)。言い回しがちがっても、中身が近ければ拾うため */
  function grams(t) { var g = {}, n = 0; for (var i = 0; i + 2 <= t.length; i++) { var k = t.slice(i, i + 2); if (!g[k]) { g[k] = 1; n++; } } return { g: g, n: n }; }
  function near(a, b) {
    var x = grams(norm(a)), y = grams(norm(b)), hit = 0;
    if (!x.n || !y.n) return 0;
    Object.keys(x.g).forEach(function (k) { if (y.g[k]) hit++; });
    return 2 * hit / (x.n + y.n);
  }
  var NEAR = 0.5;
  function grade(c, answers) {
    var R = c.rubric, res = { q: {}, over: {} }, t = {}, sim = {}, qs;
    QS.forEach(function (q) {
      var kept = inLines(answers[q.k], q.max);
      res.over[q.k] = count(answers[q.k]) > q.max; t[q.k] = norm(kept); sim[q.k] = near(kept, c.model[q.k]) >= NEAR;
    });
    qs = quotes(inLines(answers.q3b, QS[3].max), c);
    function it(key, label, pt, ok) { return { key: key, l: label, pt: pt, ok: !!ok, hint: HINT[key] }; }
    function spec(o) { return o.all || [o.re]; }
    /* 中身の観点: ことばが合うか、解答例に十分近ければ○ */
    /* 近さで拾うのは、その事例のことばが1つは入っているときだけ(ほかの事例の答えを拾わないため) */
    function any(k, list) { return list.some(function (o) { return has(t[k], spec(o)); }); }
    var anchor = { q1: any("q1", [R.jokyo, R.kimochi, R.chushin]), q2: any("q2", [R.uketa]), q3a: any("q3a", [{ re: R.omoi.re }, { re: R.mitate.re }]),
      q3b: any("q3b", [{ re: R.omoi.ev }, { re: R.mitate.ev }]), q4: any("q4", [R.hOmoi, R.hMitate]) };
    function body(k, key, label, pt, sp) { return it(key, label, pt, t[k].length >= 8 && (has(t[k], sp) || (sim[k] && anchor[k]))); }
    /* 根拠: 「 」の引用でも、言いかえでも、事例の発言を使っていれば○ */
    function basis(key, label, o) {
      var inQuote = qs.some(function (q) { return new RegExp(o.quote).test(q); });
      return it(key, label, 5, inQuote || has(t.q3b, o.ev || o.quote) || (sim.q3b && anchor.q3b));
    }
    res.q.q1 = { items: [body("q1", "jokyo", R.jokyo.l, 2, spec(R.jokyo)), body("q1", "kimochi", R.kimochi.l, 3, spec(R.kimochi)), body("q1", "chushin", R.chushin.l, 5, spec(R.chushin))] };
    res.q.q2 = { items: [body("q2", "uketa", R.uketa.l, 3, spec(R.uketa)), body("q2", "hataraki", "応答のはたらき(受け止めて返す・言いかえて確かめる・質問で引き出す)", 3, RE.hataraki), it("nerai", R.nerai.l, 4, has(t.q2, spec(R.nerai)) || (has(t.q2, RE.nerai) && anchor.q2) || (sim.q2 && anchor.q2))] };
    res.q.q3a = { items: [body("q3a", "omoi", R.omoi.l, 5, [RE.omoi, R.omoi.re]), body("q3a", "mitate", R.mitate.l, 5, [R.mitate.re, RE.fusoku])] };
    res.q.q3b = { items: [basis("omoiQ", "思い込みの根拠を、相談者の発言から挙げている", R.omoi), basis("mitateQ", "見立ての根拠を、相談者の発言から挙げている", R.mitate)] };
    res.q.q4 = { items: [
      body("q4", "kankei", "気持ちを受け止めて、信頼関係を築く", 2, RE.kankei),
      body("q4", "hOmoi", R.hOmoi.l, 3, spec(R.hOmoi)), body("q4", "hMitate", R.hMitate.l, 3, spec(R.hMitate)),
      body("q4", "jiko", "相談者が自分で決められるよう支援する", 2, RE.jiko),
      it("q4pen", "減点: キャリコンが答えを決める書き方をしている", -2, has(t.q4, RE.shiji))
    ] };
    return sum(res);
  }
  function anyOk(items) { return items.some(function (i) { return i.ok && i.pt > 0; }); }
  function sum(res) {
    res.total = 0;
    QS.forEach(function (q) {
      var s = res.q[q.k].items.reduce(function (a, it) { return a + (it.ok ? it.pt : 0); }, 0);
      res.q[q.k].score = Math.max(0, s); res.total += res.q[q.k].score;
    });
    function ok(k, key) { return res.q[k].items.some(function (i) { return i.key === key && i.ok; }); }
    res.pillars = [
      { name: "主訴", where: "設問1", ok: ok("q1", "chushin") },
      { name: "相談者の思い込み", where: "設問3 (a)", ok: ok("q3a", "omoi") && ok("q3b", "omoiQ") },
      { name: "キャリコンの見立て", where: "設問3 (b)", ok: ok("q3a", "mitate") && ok("q3b", "mitateQ") },
      { name: "今後の方策・展開", where: "設問4", ok: ok("q4", "hOmoi") && ok("q4", "hMitate") }
    ];
    return res;
  }
  window.RONJUTSU_GRADE = grade; window.RONJUTSU_QS = QS; // 動作確認用

  /* ---------- 画面 ---------- */
  var state = { c: null, timed: true, left: LIMIT, used: 0, tick: null, answers: {}, res: null, auto: 0, marks: {}, ptext: [], pen: "y", rec: null };
  var views = { top: $("[data-rm-top]"), exam: $("[data-rm-exam]"), result: $("[data-rm-result]") };
  function show(name) {
    Object.keys(views).forEach(function (k) { views[k].hidden = k !== name; });
    document.body.classList.toggle("rm-in-exam", name === "exam");
    window.scrollTo(0, name === "top" ? window.scrollY : Math.max(0, root.getBoundingClientRect().top + window.scrollY - 12));
  }

  function face(c, size, cls) {
    return '<img class="rm-face ' + (cls || "") + '" src="../../img/ronjutsu/client-' + "abcdefghjklmnprs".charAt(c.id - 1) + '.svg" alt="" width="' + size + '" height="' + size + '" loading="lazy">';
  }
  function renderPicker() {
    var best = store("best") || {};
    $("[data-rm-rounds]").innerHTML = CASES.map(function (c) {
      var b = best[c.id], draft = store("draft:" + c.id);
      var tag = b !== undefined && b !== null ? '<span class="rm-round__best">これまでの最高 <b>' + b + "</b>点</span>" : (draft ? '<span class="rm-round__best">書きかけあり</span>' : "");
      return '<li class="rm-round"><div class="rm-round__tag">' + tag + "</div>" + face(c, 84, "rm-round__face") + '<div class="rm-round__head"><span class="rm-round__no">第' + c.id + "回</span></div>" +
        '<p class="rm-round__theme">' + esc(c.theme) + '</p><p class="rm-round__who">' + esc(c.who) + "</p>" +
        '<div class="rm-round__act"><button type="button" class="button button--primary" data-start="' + c.id + '" data-timed="1">50分ではじめる</button>' +
        '<button type="button" class="rm-linkbtn" data-start="' + c.id + '" data-timed="0">時間をはからずに練習する</button></div></li>';
    }).join("");
    renderLog();
  }

  /* 段落1つぶんの文字に、引いてあるマーカーを重ねて出す */
  function markedText(i) {
    var text = state.ptext[i], ms = (state.marks[i] || []).slice().sort(function (x, y) { return x.s - y.s; }), out = "", at = 0;
    ms.forEach(function (m) {
      out += esc(text.slice(at, m.s)) + '<mark class="rm-mk rm-mk--' + m.c + '">' + esc(text.slice(m.s, m.e)) + "</mark>";
      at = m.e;
    });
    return out + esc(text.slice(at));
  }
  function renderCase(c) {
    state.ptext = c.talk.map(function (t) { return t[0] === "cl" ? t[1] : "(" + t[1] + ")"; });
    var talk = c.talk.map(function (t, i) {
      var body = '<span class="rm-ptext" data-p="' + i + '">' + markedText(i) + "</span>";
      if (t[0] === "cl") return '<p class="rm-talk__cl">' + body + "</p>";
      if (t[0] === "ccB") return '<p class="rm-talk__cc is-b">' + body + '<span class="rm-under__tag">【下線B】</span></p>';
      return '<p class="rm-talk__cc">' + body + "</p>";
    }).join("");
    return '<div class="rm-pens" role="group" aria-label="マーカー">' +
      '<button type="button" class="rm-pen rm-pen--y" data-pen="y" aria-pressed="true">きいろ</button>' +
      '<button type="button" class="rm-pen rm-pen--p" data-pen="p" aria-pressed="false">ピンク</button>' +
      '<button type="button" class="rm-pen rm-pen--e" data-pen="e" aria-pressed="false">消しゴム</button>' +
      '<button type="button" class="rm-linkbtn rm-pens__clear" data-pen-clear>ぜんぶ消す</button>' +
      '<span class="rm-pens__how">文をなぞると、線が引けます</span></div>' +
      '<h3 class="rm-case__title">【事例記録】</h3>' +
      '<div class="rm-case__box rm-case__box--who">' + face(c, 64, "rm-case__face") + '<p class="rm-case__label">相談者情報:</p>' + c.info.map(function (l) { return "<p>" + esc(l) + "</p>"; }).join("") + "</div>" +
      '<div class="rm-case__box"><p><span class="rm-case__label">面接日時:</span>2026年10月上旬 本人の希望で来談(初回面談)</p></div>' +
      '<div class="rm-case__box"><p class="rm-case__label">相談の概要:</p><p class="rm-case__ryaku"><span class="rm-ryaku">【略A】</span></p></div>' +
      '<div class="rm-case__box"><p class="rm-case__label">相談者の話した内容:</p><p class="rm-case__sub">カッコ内は、キャリアコンサルタントの発言</p>' +
      '<div class="rm-talk">' + talk + '</div><p class="rm-case__ryaku">(以下略)</p></div>' +
      '<div class="rm-case__box"><p class="rm-case__label">所感(キャリアコンサルタントの見立てと今後の方針)</p><p>・【下線B】を応答した意図は、(以下略)</p><p class="rm-case__ryaku">(以下略)</p></div>';
  }

  function renderSheet() {
    return QS.map(function (q) {
      return '<div class="rm-q" data-qbox="' + q.k + '"><label class="rm-q__head" for="rm-' + q.k + '"><span class="rm-q__no">' + q.no + '</span><span class="rm-q__pt">' + q.pt + '点</span><span class="rm-q__lines">解答用紙 ' + q.lines + "行</span></label>" +
        '<p class="rm-q__ask">' + esc(q.ask) + "</p>" +
        '<textarea id="rm-' + q.k + '" class="rm-q__ta" data-q="' + q.k + '" rows="' + (q.lines + 2) + '" spellcheck="false" autocomplete="off" aria-describedby="rm-m-' + q.k + '"></textarea>' +
        '<div class="rm-q__meter" id="rm-m-' + q.k + '"><span class="rm-q__track"><span class="rm-q__fill" data-fill="' + q.k + '"></span></span><span class="rm-q__count"><b data-count="' + q.k + '">0</b>/' + q.max + '字</span></div>' +
        '<p class="rm-q__over" data-over="' + q.k + '" hidden>行からはみ出しています。本番では、行の外に書いた分は採点されません。</p></div>';
    }).join("");
  }
  function paintCount(k) {
    var q = QS.filter(function (x) { return x.k === k; })[0], n = count(state.answers[k]);
    $('[data-count="' + k + '"]').textContent = n;
    $('[data-fill="' + k + '"]').style.width = Math.min(100, n / q.max * 100) + "%";
    $('[data-qbox="' + k + '"]').classList.toggle("is-over", n > q.max);
    $('[data-over="' + k + '"]').hidden = n <= q.max;
  }

  /* ---------- マーカー ---------- */
  function offsetIn(el, node, off) {
    var r = document.createRange(); r.selectNodeContents(el);
    try { r.setEnd(node, off); } catch (e) { return 0; }
    return r.toString().length;
  }
  function applyPen() {
    var sel = window.getSelection();
    if (!sel || sel.isCollapsed || !sel.rangeCount || !state.c) return;
    var range = sel.getRangeAt(0), changed = false;
    $$(".rm-ptext").forEach(function (el) {
      if (!range.intersectsNode(el)) return;
      var i = Number(el.dataset.p), len = state.ptext[i].length;
      var s = el.contains(range.startContainer) ? offsetIn(el, range.startContainer, range.startOffset) : 0;
      var e = el.contains(range.endContainer) ? offsetIn(el, range.endContainer, range.endOffset) : len;
      s = Math.max(0, Math.min(len, s)); e = Math.max(0, Math.min(len, e));
      if (e <= s) return;
      var next = [];
      (state.marks[i] || []).forEach(function (m) { // 重なる分は、新しい線で上書きする
        if (m.e <= s || m.s >= e) { next.push(m); return; }
        if (m.s < s) next.push({ s: m.s, e: s, c: m.c });
        if (m.e > e) next.push({ s: e, e: m.e, c: m.c });
      });
      if (state.pen !== "e") next.push({ s: s, e: e, c: state.pen });
      state.marks[i] = next; el.innerHTML = markedText(i); changed = true;
    });
    if (changed) { sel.removeAllRanges(); saveDraft(); }
  }
  function setPen(pen) {
    state.pen = pen;
    $$("[data-pen]").forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.pen === pen ? "true" : "false"); });
  }
  var penTimer = null;
  function penSoon() { clearTimeout(penTimer); penTimer = setTimeout(applyPen, 180); }
  $("[data-rm-case]").addEventListener("mouseup", penSoon);
  $("[data-rm-case]").addEventListener("touchend", function () { clearTimeout(penTimer); penTimer = setTimeout(applyPen, 600); });
  $("[data-rm-case]").addEventListener("keyup", function (e) { if (e.shiftKey || e.key === "Shift") penSoon(); });

  function fmt(sec) { var m = Math.floor(sec / 60), s = sec % 60; return m + ":" + (s < 10 ? "0" : "") + s; }
  function paintClock() {
    var el = $("[data-rm-clock]"), wrap = $("[data-rm-clockwrap]");
    if (state.timed) {
      el.textContent = fmt(Math.max(0, state.left));
      wrap.classList.toggle("is-warn", state.left <= 600 && state.left > 300);
      wrap.classList.toggle("is-last", state.left <= 300);
    } else { el.textContent = fmt(state.used); }
  }
  function saveDraft() {
    store("draft:" + state.c.id, { a: state.answers, m: state.marks, timed: state.timed, end: state.timed ? Date.now() + state.left * 1000 : null, used: state.used });
  }
  function startTick() {
    stopTick();
    var last = Date.now();
    state.tick = setInterval(function () {
      var d = Math.floor((Date.now() - last) / 1000);
      if (d < 1) return;
      last += d * 1000; state.used += d;
      if (state.timed) {
        state.left -= d;
        if ((state.left <= 600 && state.left + d > 600) || (state.left <= 300 && state.left + d > 300)) announce("残り" + Math.ceil(state.left / 60) + "分です");
        if (state.left <= 0) { state.left = 0; paintClock(); finish(true); return; }
      }
      paintClock();
      if (state.used % 15 === 0) saveDraft();
    }, 500);
  }
  function stopTick() { if (state.tick) { clearInterval(state.tick); state.tick = null; } }
  function announce(msg) { var el = $("[data-rm-live]"); el.textContent = ""; setTimeout(function () { el.textContent = msg; }, 30); }

  function start(id, timed, resume) {
    var c = CASES.filter(function (x) { return x.id === id; })[0];
    if (!c) return;
    state.c = c; state.timed = timed; state.left = LIMIT; state.used = 0; state.answers = {}; state.res = null; state.marks = {}; state.pen = "y";
    if (resume) {
      state.answers = resume.a || {}; state.marks = resume.m || {}; state.used = resume.used || 0;
      if (timed && resume.end) state.left = Math.max(1, Math.round((resume.end - Date.now()) / 1000));
    }
    $("[data-rm-case]").innerHTML = renderCase(c);
    $("[data-rm-sheet]").innerHTML = renderSheet();
    $("[data-rm-roundname]").textContent = "第" + c.id + "回";
    $("[data-rm-clocklabel]").textContent = timed ? "残り" : "経過";
    $$(".rm-q__ta").forEach(function (ta) {
      ta.value = state.answers[ta.dataset.q] || "";
      paintCount(ta.dataset.q);
      ta.addEventListener("input", function () { state.answers[ta.dataset.q] = ta.value; paintCount(ta.dataset.q); });
    });
    setTab("case");
    paintClock(); show("exam"); startTick(); saveDraft();
    if (!resume) track("ronjutsu_start_r" + c.id);
  }

  function setTab(name) {
    $("[data-rm-exam]").setAttribute("data-tab", name);
    $$("[data-rm-tab]").forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.rmTab === name ? "true" : "false"); });
    var top = views.exam.getBoundingClientRect().top;
    if (top < 0) window.scrollTo(0, window.scrollY + top);
  }

  function finish(timeup) {
    stopTick();
    $$(".rm-q__ta").forEach(function (ta) { state.answers[ta.dataset.q] = ta.value; });
    state.res = grade(state.c, state.answers);
    state.auto = state.res.total;
    state.timeup = !!timeup;
    store("draft:" + state.c.id, null);
    var best = store("best") || {};
    if (best[state.c.id] === undefined || state.auto > best[state.c.id]) { best[state.c.id] = state.auto; store("best", best); }
    track("ronjutsu_saiten_r" + state.c.id, state.auto);
    state.rec = { id: Date.now(), cid: state.c.id, at: Date.now(), a: state.answers, m: state.marks, res: state.res, auto: state.auto, used: state.used, timed: state.timed, timeup: state.timeup, memo: "" };
    var log = store("log") || [];
    log.unshift(state.rec); store("log", log.slice(0, 40)); // 新しい順に40件まで
    renderResult(); show("result");
  }
  function saveRec() {
    if (!state.rec) return;
    state.rec.res = state.res;
    var log = store("log") || [];
    for (var i = 0; i < log.length; i++) { if (log[i].id === state.rec.id) { log[i] = state.rec; break; } }
    store("log", log);
  }
  /* 前に解いた記録を、採点のあとの画面でもう一度開く */
  function openRec(id) {
    var rec = (store("log") || []).filter(function (r) { return r.id === id; })[0];
    var c = rec && CASES.filter(function (x) { return x.id === rec.cid; })[0];
    if (!c) return;
    stopTick();
    state.rec = rec; state.c = c; state.answers = rec.a || {}; state.marks = rec.m || {}; state.res = sum(rec.res); state.auto = rec.auto;
    state.used = rec.used || 0; state.timed = rec.timed !== false; state.timeup = !!rec.timeup;
    renderResult(); show("result");
    if (state.res.total !== state.auto) { $("[data-total]").textContent = state.res.total; $("[data-fixed]").hidden = false; }
  }
  function day(ms) { var d = new Date(ms), p = function (n) { return (n < 10 ? "0" : "") + n; }; return (d.getMonth() + 1) + "月" + d.getDate() + "日 " + d.getHours() + ":" + p(d.getMinutes()); }
  function renderLog() {
    var log = store("log") || [], box = $("[data-rm-log]");
    $("[data-rm-logwrap]").hidden = !log.length;
    box.innerHTML = log.map(function (r) {
      var c = CASES.filter(function (x) { return x.id === r.cid; })[0]; if (!c) return "";
      var ps = sum(r.res).pillars.map(function (p) { return '<span class="rm-log__p' + (p.ok ? " is-ok" : "") + '" title="' + p.name + '"></span>'; }).join("");
      return '<li class="rm-log__row"><span class="rm-log__day">' + day(r.at) + '</span><span class="rm-log__name">第' + c.id + "回 " + esc(c.theme) + '</span><span class="rm-log__ps" aria-label="4つの柱">' + ps + '</span><span class="rm-log__pt"><b>' + r.auto + "</b>点</span>" +
        (r.memo ? '<span class="rm-log__memo">' + esc(r.memo) + "</span>" : "") +
        '<span class="rm-log__act"><button type="button" class="rm-linkbtn" data-rec="' + r.id + '">ふり返る</button><button type="button" class="rm-log__del" data-rec-del="' + r.id + '" aria-label="この記録を消す">消す</button></span></li>';
    }).join("");
  }

  /* 目標の30点と足切りの20点は、協議会が公開している合格基準と平均点にもとづく */
  function band(t) {
    if (t >= 40) return { head: "平均(約32点)を大きくこえています", sunny: "4つの柱がそろって、事例のことばでつながっているよ。次は紙に手書きで、同じ行数・同じ時間で書けるか確かめよう。", moyan: "すごい……！ ぼくもこの順番で書いてみる。ふんふん。" };
    if (t >= 30) return { head: "目標の30点に届きました", sunny: "点数は目標に届いたよ。ただ、4つの柱に×が残っていたら、そこが次に直すところ。×の観点を1つずつ見て、事例のことばに置きかえていこう。", moyan: "点だけじゃなくて、柱も見るんだね。どこが×か、見てみる！" };
    if (t >= 20) return { head: "足切り(20点)はこえました。目標まで、あと" + (30 - t) + "点", sunny: "方向は合っているよ。足りないのは、思い込みの指摘と、「 」での引用のことが多いんだ。4つの柱のうち、×の柱から直そう。", moyan: "柱が立ってないところを、先に直せばいいんだね……！" };
    return { head: "足切りの20点に届いていません", sunny: "大丈夫、ここからだよ。まず解答例を、行数を守って1回書き写してみよう。型が手に入ると、次の回で点が変わるよ。", moyan: "ぼくも最初はまっ白だったよ……。いっしょに書き写そう。" };
  }

  function say(who, text) {
    var img = who === "sunny" ? "06_sun_character.png" : "07_moyan_school_hat_crying.png", name = who === "sunny" ? "サニー先生" : "モヤン";
    return '<div class="mini-say mini-say--' + who + '"><span class="mini-say__avatar" aria-hidden="true"><img src="../../img/parts/' + img + '" alt="" width="44" height="44" loading="lazy"></span><p class="mini-say__bubble"><b>' + name + "</b>" + esc(text) + "</p></div>";
  }
  function pillarsHtml(res) {
    return res.pillars.map(function (p) {
      return '<li class="rm-pillar' + (p.ok ? " is-ok" : "") + '"><span class="rm-pillar__mark" aria-hidden="true"></span><b>' + p.name + "</b><small>" + p.where + "・" + (p.ok ? "書けている" : "足りない") + "</small></li>";
    }).join("");
  }

  function renderResult() {
    var c = state.c, res = state.res, b = band(state.auto);
    var bars = QS.map(function (q) {
      var s = res.q[q.k].score;
      return '<li><span class="rm-bar__name">' + q.short + '</span><span class="rm-bar__track"><span class="rm-bar__fill" style="width:' + (s / q.pt * 100) + '%"></span></span><span class="rm-bar__num"><b data-qscore="' + q.k + '">' + s + "</b>/" + q.pt + "</span></li>";
    }).join("");
    var cards = QS.map(function (q) {
      var r = res.q[q.k], raw = (state.answers[q.k] || "").trim(), kept = inLines(raw, q.max), cut = raw.slice(kept.length);
      var checks = r.items.filter(function (it) { return it.pt > 0 || it.ok; }).map(function (it) {
        var i = r.items.indexOf(it), pen = it.pt < 0;
        return '<li class="rm-check' + (it.ok ? " is-ok" : "") + (pen ? " is-pen" : "") + '"><button type="button" class="rm-check__btn" data-toggle="' + q.k + ":" + i + '" aria-pressed="' + (it.ok ? "true" : "false") + '"><span class="rm-check__mark" aria-hidden="true"></span><span class="rm-check__label">' + esc(it.l) + '</span><span class="rm-check__pt">' + (pen ? "−" + (-it.pt) : it.pt) + "点</span></button>" +
          '<p class="rm-check__hint">' + esc(it.hint) + "</p></li>";
      }).join("");
      var nk = q.k === "q3a" || q.k === "q3b" ? "q3" : q.k;
      var note = q.k === "q3a" ? "" : '<div class="rm-talknote"><p class="rm-talknote__label">モヤンとサニー先生の解説</p>' + say("moyan", c.talkNote[nk][0]) + say("sunny", c.talkNote[nk][1]) + "</div>";
      return '<section class="rm-card"><div class="rm-card__head"><h3 class="rm-card__title">' + q.no + '</h3><p class="rm-card__score"><b data-qscore="' + q.k + '">' + r.score + "</b>/" + q.pt + "点</p></div>" +
        '<p class="rm-card__ask">' + esc(q.ask) + "</p>" +
        '<div class="rm-yours"><p class="rm-yours__label">あなたの解答<small>' + count(raw) + "字／" + q.lines + "行(" + q.max + '字)まで</small></p><p class="rm-yours__text">' + (raw ? esc(kept) + (cut ? '<span class="rm-cut">' + esc(cut) + "</span>" : "") : "(書いていません)") + "</p>" +
        (cut ? '<p class="rm-yours__over">うすい色の部分は、行からはみ出した分です。採点していません。</p>' : "") + "</div>" +
        '<p class="rm-card__sub">採点の観点</p><ul class="rm-checks">' + checks + "</ul>" +
        '<div class="rm-model"><p class="rm-model__label">解答例<small>' + count(c.model[q.k]) + "字</small></p><p class=\"rm-model__text\">" + esc(c.model[q.k]) + "</p></div>" + note + "</section>";
    }).join("");
    $("[data-rm-resultbody]").innerHTML =
      '<div class="rm-score">' + face(c, 76, "rm-score__face") + '<p class="rm-score__round">第' + c.id + "回 " + esc(c.theme) + (state.rec ? "・" + day(state.rec.at) + "の記録" : "") + "</p>" +
      (state.timeup ? '<p class="rm-score__timeup">50分になったので、ここまでの解答で採点しました。</p>' : "") +
      '<p class="rm-score__num"><b>' + state.auto + '</b><span>/50点</span></p><p class="rm-score__head">' + b.head + "</p>" +
      '<p class="rm-score__time">かかった時間 ' + fmt(state.used) + (state.timed ? "(制限50分)" : "(時間をはからない練習)") + "</p>" +
      '<p class="rm-score__fixed" data-fixed hidden>自分で直したあとの点数 <b data-total></b>点</p>' +
      '<p class="rm-pillars__label">4つの柱</p><ul class="rm-pillars" data-pillars>' + pillarsHtml(res) + "</ul>" +
      '<ul class="rm-bars">' + bars + "</ul>" +
      '<p class="rm-score__note">目標は<strong>30点</strong>です。協議会が公開している直近3回の論述の平均は約32点、足切りは20点(配点の40%)です。この模擬試験の点数は、解答の中身を、ことばの一致と解答例との近さで機械的に確かめたもので、公式の採点基準ではありません(模範解答と採点基準は公開されていません)。</p></div>' +
      '<div class="rm-says">' + say("sunny", b.sunny) + say("moyan", b.moyan) + "</div>" +
      '<div class="rm-memo"><label class="rm-memo__label" for="rm-memo">次に直すこと<small>書いておくと、記録の一覧に出ます</small></label><textarea id="rm-memo" class="rm-memo__ta" rows="2" maxlength="200" data-rm-memo placeholder="例: 設問3は、思い込みを先に書く">' + esc(state.rec && state.rec.memo || "") + "</textarea></div>" +
      '<h2 class="rm-h2">設問ごとの採点と解説</h2><p class="rm-lead">解答例とちがう見立てでも、事例の発言を根拠にしていれば、まちがいではありません。機械が読み取れなかった観点は、押して直せます(上の点数は変わらず、「自分で直したあとの点数」として別に出ます)。</p>' + cards;
  }

  function retotal() {
    sum(state.res);
    QS.forEach(function (q) { $$('[data-qscore="' + q.k + '"]').forEach(function (el) { el.textContent = state.res.q[q.k].score; }); });
    $$(".rm-bar__fill").forEach(function (el, i) { el.style.width = (state.res.q[QS[i].k].score / QS[i].pt * 100) + "%"; });
    $("[data-total]").textContent = state.res.total;
    $("[data-fixed]").hidden = false;
    $("[data-pillars]").innerHTML = pillarsHtml(state.res);
    saveRec();
  }

  /* ---------- 操作 ---------- */
  root.addEventListener("click", function (e) {
    var t = e.target.closest("button");
    if (!t) return;
    if (t.dataset.start) {
      var id = Number(t.dataset.start), timed = t.dataset.timed === "1", draft = store("draft:" + id);
      var alive = draft && (!draft.timed || (draft.end && draft.end > Date.now()));
      if (alive && draft.timed === timed) { start(id, timed, draft); return; }
      start(id, timed, null);
    } else if (t.dataset.rec) { openRec(Number(t.dataset.rec));
    } else if (t.dataset.recDel) {
      if (window.confirm("この記録を消しますか？")) { store("log", (store("log") || []).filter(function (r) { return r.id !== Number(t.dataset.recDel); })); renderLog(); }
    } else if (t.dataset.pen) { setPen(t.dataset.pen);
    } else if (t.hasAttribute("data-pen-clear")) { state.marks = {}; $$(".rm-ptext").forEach(function (el) { el.innerHTML = markedText(Number(el.dataset.p)); }); saveDraft();
    } else if (t.dataset.rmTab) { setTab(t.dataset.rmTab);
    } else if (t.hasAttribute("data-rm-submit")) { $("[data-rm-confirm]").showModal();
    } else if (t.hasAttribute("data-rm-confirm-yes")) { $("[data-rm-confirm]").close(); finish(false);
    } else if (t.hasAttribute("data-rm-confirm-no")) { $("[data-rm-confirm]").close();
    } else if (t.hasAttribute("data-rm-quit")) { stopTick(); saveDraft(); renderPicker(); show("top");
    } else if (t.dataset.toggle) {
      var p = t.dataset.toggle.split(":"), it = state.res.q[p[0]].items[Number(p[1])];
      it.ok = !it.ok; t.setAttribute("aria-pressed", it.ok ? "true" : "false");
      t.closest(".rm-check").classList.toggle("is-ok", it.ok); retotal();
    } else if (t.hasAttribute("data-rm-again")) { start(state.c.id, state.timed, null);
    } else if (t.hasAttribute("data-rm-other")) { renderPicker(); show("top"); views.top.scrollIntoView();
    }
  });
  root.addEventListener("input", function (e) {
    if (e.target.hasAttribute && e.target.hasAttribute("data-rm-memo") && state.rec) { state.rec.memo = e.target.value; saveRec(); }
  });
  window.addEventListener("beforeunload", function () { if (state.tick) saveDraft(); });
  document.addEventListener("visibilitychange", function () { if (document.hidden && state.tick) saveDraft(); });

  renderPicker();
  show("top");
})();

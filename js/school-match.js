/* 学校えらび30秒チェック
 * 4つの質問に答えると、比較表(/schools/compare/)の内容から、条件に合う学校だけを残して見せる。
 * - 学校の情報はこのファイルに持たない。比較表のセルの文字と、セルに付けた目印を読む。
 *     data-m="合うと確かめられた条件"  data-no="合わないと確かめられた条件"  data-yen="金額(円)"
 *   セルに「未確認」とあれば未確認として扱う。目印がどれも無ければ「記載なし」(合うことにはしない)。
 *   比較表を直したら、同じセルの目印もいっしょに直す。
 * - 順位や点数は付けない。並び順は「合わない条件が少ない → 合うと確かめられた条件が多い → 確認できた金額が低い」。
 *   PRの有無は見ない。
 * - 文言(T)は picnic-docs/作り直し用スクリプト/school_match.py から書き出している(<wbr> を入れるため)。
 *   文言を直すときは、そちらを直して実行する。 */
(function () {
  "use strict";
  var root = document.querySelector("[data-school-match]");
  if (!root) return;

  /*T-BEGIN*/
  var T = {
    "step": "質問",
    "time": "4つ選ぶだけ",
    "back": "ひとつ戻る",
    "q": {
      "place": {
        "q": "どこで受けたいですか？",
        "hint": "",
        "opts": [
          [
            "家から、<wbr>オンラインだけで",
            "移動なしで<wbr>受けたい"
          ],
          [
            "教室にも<wbr>通いたい",
            "顔を<wbr>合わせて<wbr>学びたい"
          ],
          [
            "まだ<wbr>決めていない",
            "この<wbr>条件は<wbr>使いません"
          ]
        ]
      },
      "time": {
        "q": "いつなら受けられますか？",
        "hint": "",
        "opts": [
          [
            "平日の昼間",
            "日中に<wbr>時間を<wbr>とれる"
          ],
          [
            "平日の夜",
            "仕事のあとに"
          ],
          [
            "土日・祝日",
            "休みの<wbr>日に<wbr>まとめて"
          ],
          [
            "まだ<wbr>決めていない",
            "この<wbr>条件は<wbr>使いません"
          ]
        ]
      },
      "yen": {
        "q": "お金で大事にしたいのは？",
        "hint": "給付金を<wbr>使う<wbr>前の<wbr>金額で<wbr>比べます。",
        "opts": [
          [
            "総額の<wbr>安さ重視",
            "入学金・教材費こみで<wbr>35万円まで"
          ],
          [
            "あとから<wbr>足されない<wbr>こと<wbr>重視",
            "入学金も<wbr>教材費も、<wbr>受講料に<wbr>込み"
          ],
          [
            "試験対策こみ重視",
            "合格までの<wbr>費用を<wbr>先に<wbr>知りたい"
          ],
          [
            "金額より<wbr>中身重視",
            "この<wbr>条件は<wbr>使いません"
          ]
        ]
      },
      "care": {
        "q": "受講中に大事なのは？",
        "hint": "",
        "opts": [
          [
            "休んでも<wbr>追いつける<wbr>こと<wbr>重視",
            "欠席した回を<wbr>振替できる"
          ],
          [
            "仕事に<wbr>つながる<wbr>支援重視",
            "就職・就業の<wbr>支援が<wbr>ある"
          ],
          [
            "仲間との<wbr>つながり重視",
            "卒業生の<wbr>集まりが<wbr>ある"
          ],
          [
            "まだわからない",
            "この<wbr>条件は<wbr>使いません"
          ]
        ]
      }
    },
    "cond": {
      "home": "家から<wbr>オンラインだけで",
      "room": "教室に通える",
      "wd": "平日の昼間",
      "ev": "平日の夜",
      "we": "土日・祝日",
      "cheap": "総額の<wbr>安さ(35万円まで<wbr>)",
      "allin": "入学金・教材費が<wbr>受講料に<wbr>込み",
      "makeup": "休んでも<wbr>振替できる",
      "prep": "試験対策が<wbr>料金に<wbr>込み",
      "job": "仕事に<wbr>つながる<wbr>支援",
      "mate": "修了後の<wbr>仲間との<wbr>つながり"
    },
    "st": {
      "ok": "合う",
      "no": "合わない",
      "na": "確かめられていない"
    },
    "you": "あなたの条件",
    "noCond": "まだ<wbr>決めていない",
    "redo": "条件を変える",
    "head": {
      "full": [
        "{n}校が、<wbr>すべて<wbr>合いました",
        "比較表に<wbr>ある{all}校の<wbr>うち、<wbr>公式サイトなどで<wbr>確かめられた<wbr>情報だけで<wbr>見ています。"
      ],
      "maybe": [
        "候補は{n}校(未確認あり)",
        "合わない<wbr>条件は<wbr>ありませんが、<wbr>まだ<wbr>確かめられていない<wbr>項目が<wbr>あります。<wbr>説明会や<wbr>相談で、<wbr>直接聞いてみてください。"
      ],
      "out": [
        "すべて合う<wbr>学校は<wbr>0校でした",
        "条件に<wbr>近い順に<wbr>並べました。<wbr>条件を<wbr>ひとつゆる<wbr>めると、<wbr>合う<wbr>学校が<wbr>出てくることがあります。"
      ],
      "free": [
        "{all}校を<wbr>金額順に<wbr>並べました",
        "条件が<wbr>決まっていなくても<wbr>大丈夫です。<wbr>確認できた<wbr>金額の<wbr>低い順です。<wbr>気に<wbr>なる<wbr>学校から<wbr>見てみてください。"
      ]
    },
    "me": "運営者が<wbr>受講した<wbr>学校",
    "total": "確認できた<wbr>総額",
    "totalSub": "受講料＋入学金＋教材費<wbr><span class=\"sm-nb\">(給付金を使う前)</span>",
    "price": {
      "fee": "受講料",
      "ent": "入学金",
      "mat": "教材費"
    },
    "plus": "＋",
    "plusTail": "(未確認)",
    "prep": "試験対策",
    "notStated": "比較表に<wbr>記載が<wbr>ありません",
    "notStatedTail": "(この条件の記載なし)",
    "more": "くわしく見る",
    "site": "公式サイトを見る",
    "checked": "情報を<wbr>確かめた<wbr>日",
    "rest": "ほかの{n}校も<wbr>見る<wbr>(合わない・未確認の<wbr>条件あり)",
    "nextK": "NEXT STEP",
    "nextT": "無料の説明会・相談で確かめる",
    "nextB": "ここに<wbr>出ているのは、<wbr>公式サイトなどで<wbr>確かめられた<wbr>範囲の<wbr>情報です。<wbr>日程や<wbr>振替の<wbr>細かい<wbr>条件は、<wbr>学校に<wbr>直接聞くのが<wbr>いちばん確かです。<wbr>ほとんどの<wbr>学校で、<wbr>申し込むと<wbr>決めていなくても<wbr>参加できます。",
    "nextBtn": "公式サイトを開く",
    "ad": "広告",
    "kindDefault": "説明会・<wbr>資料請求は<wbr>公式サイトで<wbr>確認",
    "nextAd": "学校の<wbr>公式サイトへの<wbr>ボタンは<wbr>紹介リンク(広告)です。<wbr>申込みが<wbr>あると、<wbr>運営者が<wbr>報酬を<wbr>受け取ることがあります。<wbr>学校の<wbr>並び順や<wbr>内容は、<wbr>広告の<wbr>有無で<wbr>変えていません。",
    "nextAll": "{all}校すべての<wbr>申込み先を<wbr>見る",
    "nextTable": "この{n}校だけを<wbr>比較表で<wbr>見る",
    "nextKai": "運営者が<wbr>参加した<wbr>説明会の<wbr>様子を<wbr>読む",
    "nextKyufu": "給付金で<wbr>実質いくらに<wbr>なるか<wbr>見る",
    "rulesT": "この<wbr>チェックの<wbr>きまり",
    "rules": [
      "比較表と<wbr>同じ<wbr>情報だけを<wbr>使っています。<wbr>各校の<wbr>公式サイトと<wbr>明示書で<wbr>確かめた<wbr>ものです。",
      "確かめられていない<wbr>項目は<wbr>「未確認」と<wbr>出します。<wbr>合うことにはしません。",
      "順位や<wbr>点数は<wbr>付けません。<wbr>広告(PR)の<wbr>学校も、<wbr>同じ<wbr>基準で<wbr>並べます。",
      "料金や<wbr>日程は<wbr>変わる<wbr>ことがあります。<wbr>申し込む前に、<wbr>各校の<wbr>公式サイトで<wbr>確かめてください。"
    ],
    "error": "学校の<wbr>情報を<wbr>読み込めませんでした。<wbr>比較表の<wbr>ページで、<wbr>同じ<wbr>情報を<wbr>見られます。",
    "errorBtn": "比較表を見る"
  };
  /*T-END*/

  var COMPARE = "/schools/compare/";
  var KEY = "school-match-v2";
  var ROW = {
    home: "オンライン完結の可否",
    room: "通学拠点",
    wd: "平日・土日・夜間コース",
    ev: "平日・土日・夜間コース",
    we: "平日・土日・夜間コース",
    prep: "試験対策が料金に含まれるか",
    job: "就職支援",
    mate: "卒業生コミュニティ",
    makeup: "振替制度"
  };
  var QS = [
    { id: "place", vals: ["home", "room", ""] },
    { id: "time", vals: ["wd", "ev", "we", ""] },
    { id: "yen", vals: ["cheap", "allin", "prep", ""] },
    { id: "care", vals: ["makeup", "job", "mate", ""] }
  ];
  var BUDGET = { cheap: 350000 }; /* 「総額の安さ重視」: 入学金・教材費こみで35万円まで */
  var ME = "chiiki-renkei-platform"; /* 運営者が受講した学校 */

  var ans = {};
  var step = 0;
  var schools = null;
  var loading = null;
  var started = false;

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function yen(n) {
    return n.toLocaleString("ja-JP") + "円";
  }
  function ev(name, params) {
    if (typeof window.gtag === "function") window.gtag("event", name, params || {});
  }
  function save(done) {
    try {
      sessionStorage.setItem(KEY, JSON.stringify({ ans: ans, done: !!done }));
    } catch (e) {}
  }

  /* ---- 比較表を読む ---- */
  function cellHtml(node) {
    var out = "";
    node.childNodes.forEach(function (n) {
      if (n.nodeType === 3) out += esc(n.nodeValue);
      else if (n.nodeType === 1) {
        if (n.tagName === "WBR") out += "<wbr>";
        else if (!n.classList.contains("cmp__mark")) out += cellHtml(n);
      }
    });
    return out;
  }
  function list(el, name) {
    return (el.getAttribute(name) || "").split(/\s+/).filter(Boolean);
  }
  function parse(doc) {
    var table = doc.querySelector("table.cmp");
    if (!table) return null;
    var arr = [];
    var by = {};
    table.querySelectorAll("thead th[data-school]").forEach(function (th) {
      var name = th.querySelector(".cmp__name");
      if (!name) return;
      var n = name.cloneNode(true);
      var pr = n.querySelector(".pr-label");
      if (pr) pr.remove();
      var s = { slug: th.getAttribute("data-school"), name: n.textContent.trim(), pr: !!pr, cells: {}, go: null };
      /* 当サイトに紹介ページがある学校だけ「くわしく見る」を出す(ない学校は公式サイトへ) */
      s.page = !!th.querySelector('.cmp__links a:not([target])');
      var site = th.querySelector('.cmp__links a[target="_blank"]');
      if (site) s.go = linkOf(site, "");
      arr.push(s);
      by[s.slug] = s;
    });
    table.querySelectorAll("tbody tr").forEach(function (tr) {
      var th = tr.querySelector('th[scope="row"]');
      if (!th) return;
      var label = th.textContent.replace(/\s+/g, "");
      tr.querySelectorAll("td[data-school]").forEach(function (td) {
        var s = by[td.getAttribute("data-school")];
        if (!s) return;
        var html = cellHtml(td).trim();
        s.cells[label] = {
          html: html,
          na: /未確認/.test(td.textContent),
          m: list(td, "data-m"),
          no: list(td, "data-no"),
          yen: td.hasAttribute("data-yen") ? Number(td.getAttribute("data-yen")) : null
        };
      });
    });
    /* 説明会・資料請求の申込み先(比較ページの一覧)。行がない学校は、表の「公式サイト」のリンクを使う */
    doc.querySelectorAll(".apply__row[data-school]").forEach(function (li) {
      var s = by[li.getAttribute("data-school")];
      var a = li.querySelector("a.apply__go");
      var kind = li.querySelector(".apply__kind");
      if (!s || !a) return;
      s.go = linkOf(a, kind ? cellHtml(kind).trim() : "");
      var px = li.querySelector('img[width="1"]');
      if (px) s.go.px = px.getAttribute("src");
    });
    return arr.length ? arr : null;
  }
  function linkOf(a, kind) {
    var rel = a.getAttribute("rel") || "noopener";
    return { href: a.getAttribute("href"), rel: rel, ad: /sponsored/.test(rel), kind: kind, px: "" };
  }
  function load() {
    if (schools) return Promise.resolve(schools);
    if (loading) return loading;
    var here = parse(document);
    if (here) {
      schools = here;
      return Promise.resolve(schools);
    }
    loading = fetch(COMPARE, { credentials: "same-origin" })
      .then(function (r) {
        if (!r.ok) throw new Error(r.status);
        return r.text();
      })
      .then(function (t) {
        schools = parse(new DOMParser().parseFromString(t, "text/html"));
        if (!schools) throw new Error("no table");
        return schools;
      });
    loading.catch(function () {
      loading = null;
    });
    return loading;
  }

  /* ---- 判定 ---- */
  function price(s) {
    var parts = [
      { k: "fee", c: s.cells["受講料金"] },
      { k: "ent", c: s.cells["入学金"] },
      { k: "mat", c: s.cells["教材費"] }
    ];
    var sum = 0;
    var unknown = [];
    parts.forEach(function (p) {
      if (p.c && p.c.yen !== null) sum += p.c.yen;
      else unknown.push(p.k);
    });
    return { parts: parts, sum: sum, unknown: unknown };
  }
  function judge(s, key) {
    if (BUDGET[key]) {
      var p = price(s);
      var st = p.sum > BUDGET[key] ? "no" : p.unknown.length ? "na" : "ok";
      return { key: key, st: st, html: totalHtml(p) };
    }
    if (key === "allin") {
      /* 「あとから足される費用がないこと重視」: 入学金も教材費も受講料に入っている */
      var ent = s.cells["入学金"];
      var mat = s.cells["教材費"];
      var ys = [ent ? ent.yen : null, mat ? mat.yen : null];
      var st2 = ys[0] > 0 || ys[1] > 0 ? "no" : ys[0] === 0 && ys[1] === 0 ? "ok" : "na";
      return {
        key: key,
        st: st2,
        html: T.price.ent + ": " + (ent ? ent.html : T.notStated) + " / " + T.price.mat + ": " + (mat ? mat.html : T.notStated)
      };
    }
    var c = s.cells[ROW[key]];
    if (!c) return { key: key, st: "na", html: T.notStated };
    if (c.m.indexOf(key) !== -1) return { key: key, st: "ok", html: c.html };
    if (c.no.indexOf(key) !== -1) return { key: key, st: "no", html: c.html };
    return { key: key, st: "na", html: c.na ? c.html : c.html + T.notStatedTail };
  }
  function totalHtml(p) {
    if (!p.unknown.length) return yen(p.sum);
    return (
      yen(p.sum) +
      "<small>" +
      T.plus +
      p.unknown
        .map(function (k) {
          return T.price[k];
        })
        .join("・") +
      T.plusTail +
      "</small>"
    );
  }
  function picked() {
    return QS.map(function (q) {
      return ans[q.id];
    }).filter(Boolean);
  }
  function rank() {
    var keys = picked();
    var rows = schools.map(function (s, i) {
      var js = keys.map(function (k) {
        return judge(s, k);
      });
      var p = price(s);
      var cnt = { ok: 0, no: 0, na: 0 };
      js.forEach(function (j) {
        cnt[j.st]++;
      });
      return { s: s, js: js, p: p, cnt: cnt, i: i };
    });
    rows.sort(function (a, b) {
      return a.cnt.no - b.cnt.no || b.cnt.ok - a.cnt.ok || a.p.sum - b.p.sum || a.p.unknown.length - b.p.unknown.length || a.i - b.i;
    });
    return rows;
  }

  /* ---- 画面 ---- */
  var SUNNY = '<img src="/img/parts/s/06_sun_character.webp" alt="" width="52" height="47">';
  var ARW = ' <span class="arw" aria-hidden="true">▶︎</span>';

  function renderQ(dir) {
    var q = QS[step];
    var t = T.q[q.id];
    var pips = QS.map(function (_, i) {
      return '<i class="' + (i < step ? "is-done" : i === step ? "is-now" : "") + '"></i>';
    }).join("");
    var opts = q.vals
      .map(function (v, i) {
        var o = t.opts[i];
        return (
          '<li><button type="button" class="sm__opt' +
          (v === "" ? " sm__opt--skip" : "") +
          (ans[q.id] === v && q.id in ans ? " is-on" : "") +
          '" data-v="' +
          v +
          '"><span class="sm__optb">' +
          o[0] +
          "</span>" +
          (o[1] ? '<span class="sm__opts">' + o[1] + "</span>" : "") +
          '<i class="sm__optc" aria-hidden="true"></i></button></li>'
        );
      })
      .join("");
    root.innerHTML =
      '<div class="sm__card sm__card--q' +
      (dir ? " is-" + dir : "") +
      '">' +
      '<div class="sm__bar"><p class="sm__step"><span class="visually-hidden">' +
      T.step +
      "</span><b>" +
      (step + 1) +
      "</b> / " +
      QS.length +
      '</p><div class="sm__pips" aria-hidden="true">' +
      pips +
      "</div>" +
      (step > 0 ? '<button type="button" class="sm__back" data-back>' + T.back + "</button>" : '<span class="sm__time">' + T.time + "</span>") +
      "</div>" +
      '<div class="sm__ask"><span class="sm__avatar" aria-hidden="true">' +
      SUNNY +
      '</span><div class="sm__bubble"><h3 class="sm__q" tabindex="-1">' +
      t.q +
      "</h3>" +
      (t.hint ? '<p class="sm__hint">' + t.hint + "</p>" : "") +
      "</div></div>" +
      '<ul class="sm__list" data-n="' +
      q.vals.length +
      '">' +
      opts +
      "</ul></div>";
    if (dir) focusIn(".sm__q");
  }

  function focusIn(sel) {
    var el = root.querySelector(sel);
    if (!el) return;
    el.focus({ preventScroll: true });
    var r = root.getBoundingClientRect();
    if (r.top < 70 || r.top > window.innerHeight * 0.5) {
      window.scrollTo({ top: window.scrollY + r.top - 84, behavior: "smooth" });
    }
  }

  function chip(k) {
    return '<li class="sm__chip">' + T.cond[k] + "</li>";
  }

  function card(r, lead) {
    var s = r.s;
    var why = r.js
      .map(function (j) {
        return (
          '<li class="is-' +
          j.st +
          '"><i class="sm-st" aria-hidden="true"></i><span class="visually-hidden">' +
          T.st[j.st] +
          ':</span><div><b>' +
          T.cond[j.key] +
          "</b><span>" +
          j.html +
          "</span></div></li>"
        );
      })
      .join("");
    var rows = r.p.parts
      .map(function (p) {
        return "<div><dt>" + T.price[p.k] + "</dt><dd>" + (p.c ? p.c.html : T.notStated) + "</dd></div>";
      })
      .join("");
    var prep = s.cells["試験対策が料金に含まれるか"];
    var date = s.cells["情報確認日"];
    return (
      '<li class="sm-school' +
      (lead ? " sm-school--lead" : "") +
      '"><div class="sm-school__head"><h4 class="sm-school__name">' +
      (s.pr ? '<span class="pr-label">PR</span>' : "") +
      esc(s.name) +
      "</h4>" +
      (s.slug === ME ? '<p class="sm-school__me">' + T.me + "</p>" : "") +
      "</div>" +
      (why ? '<ul class="sm-school__why">' + why + "</ul>" : "") +
      '<div class="sm-school__price"><p class="sm-school__total"><span>' +
      T.total +
      "<small>" +
      T.totalSub +
      "</small></span><b>" +
      totalHtml(r.p) +
      "</b></p><dl>" +
      rows +
      (prep ? "<div><dt>" + T.prep + "</dt><dd>" + prep.html + "</dd></div>" : "") +
      "</dl></div>" +
      '<div class="sm-school__foot">' +
      (s.page || !s.go
        ? '<a class="sm-school__go" href="/schools/' + s.slug + '/" data-ev="match_school_' + s.slug + '">' + T.more + ARW + "</a>"
        : '<a class="sm-school__go" href="' + esc(s.go.href) + '" rel="' + esc(s.go.rel) + '" target="_blank" data-ev="match_site_' + s.slug + '">' +
          T.site + "" + ARW + "</a>") +
      (date ? '<p class="sm-school__date">' + T.checked + " " + date.html + "</p>" : "") +
      "</div></li>"
    );
  }

  function applyRow(s) {
    var g = s.go;
    if (!g) return "";
    return (
      '<li><div class="sm__applyn"><b>' +
      esc(s.name) +
      "</b><span>" +
      (g.kind || T.kindDefault) +
      '</span></div><a class="button button--primary sm__applygo" href="' +
      esc(g.href) +
      '" rel="' +
      esc(g.rel) +
      '" target="_blank" data-ev="match_apply_' +
      s.slug +
      '">' +
      T.nextBtn +
      "" +
      "</a>" +
      (g.px ? '<img src="' + esc(g.px) + '" width="1" height="1" alt="" style="position:absolute;border:0">' : "") +
      "</li>"
    );
  }

  function renderResult(first) {
    var rows = rank();
    var keys = picked();
    var full = rows.filter(function (r) {
      return r.cnt.no === 0 && r.cnt.na === 0;
    });
    var maybe = rows.filter(function (r) {
      return r.cnt.no === 0 && r.cnt.na > 0;
    });
    var kind, lead;
    if (!keys.length) {
      kind = "free";
      lead = rows;
    } else if (full.length) {
      kind = "full";
      lead = full;
    } else if (maybe.length) {
      kind = "maybe";
      lead = maybe;
    } else {
      kind = "out";
      lead = rows.slice(0, 2);
    }
    var rest = rows.filter(function (r) {
      return lead.indexOf(r) === -1;
    });
    var n = lead.length;
    var h = T.head[kind];
    var slugs = lead.slice(0, 3).map(function (r) {
      return r.s.slug;
    });
    var chips = keys.length ? keys.map(chip).join("") : '<li class="sm__chip sm__chip--none">' + T.noCond + "</li>";

    root.innerHTML =
      '<div class="sm__card sm__card--res' +
      (first ? " is-next" : "") +
      '">' +
      '<div class="sm__you"><p class="sm__youlab">' +
      T.you +
      '</p><ul class="sm__chips">' +
      chips +
      '</ul><button type="button" class="sm__redo" data-redo>' +
      T.redo +
      "</button></div>" +
      '<div class="sm__ask sm__ask--res"><span class="sm__avatar" aria-hidden="true">' +
      SUNNY +
      '</span><div class="sm__bubble"><h3 class="sm__q sm__q--res" tabindex="-1">' +
      h[0].replace("{n}", '<em class="sm__num">' + n + "</em>").replace("{all}", schools.length) +
      '</h3><p class="sm__hint">' +
      h[1].replace("{all}", schools.length) +
      "</p></div></div>" +
      '<ul class="sm__schools">' +
      lead
        .map(function (r) {
          return card(r, true);
        })
        .join("") +
      "</ul>" +
      (rest.length
        ? '<details class="sm__rest"><summary>' +
          T.rest.replace("{n}", rest.length) +
          '</summary><ul class="sm__schools">' +
          rest
            .map(function (r) {
              return card(r, false);
            })
            .join("") +
          "</ul></details>"
        : "") +
      '<div class="sm__next"><p class="sm__nextk">' +
      T.nextK +
      '</p><h3 class="sm__nextt">' +
      T.nextT +
      '</h3><p class="sm__nextb">' +
      T.nextB +
      '</p><ul class="sm__apply">' +
      lead
        .slice(0, 3)
        .map(function (r) {
          return applyRow(r.s);
        })
        .join("") +
      '</ul><p class="sm__nextad">' +
      T.nextAd +
      '</p><ul class="sm__links"><li><a href="' +
      COMPARE +
      '#apply-h" data-ev="match_apply_all">' +
      T.nextAll.replace("{all}", schools.length) +
      ARW +
      "</a></li>" +
      (n < schools.length
        ? '<li><a href="' +
          COMPARE +
          "?schools=" +
          slugs.join(",") +
          '#cmp-table" data-ev="match_table">' +
          T.nextTable.replace("{n}", slugs.length) +
          ARW +
          "</a></li>"
        : "") +
      '<li><a href="/schools/' +
      ME +
      '/#kai" data-ev="match_kai">' +
      T.nextKai +
      ARW +
      '</a></li><li><a href="/school-guides/kyufukin/" data-ev="match_kyufu">' +
      T.nextKyufu +
      ARW +
      "</a></li></ul></div>" +
      '<div class="sm__rules"><p class="sm__rulest">' +
      T.rulesT +
      "</p><ul>" +
      T.rules
        .map(function (r) {
          return "<li>" + r + "</li>";
        })
        .join("") +
      "</ul></div></div>";
    if (first) {
      focusIn(".sm__q");
      ev("match_done", { result: kind, count: n, cond: keys.join(",") || "none" });
    }
  }

  function showError() {
    root.innerHTML =
      '<div class="sm__card"><p class="sm__err">' + T.error + '</p><p class="sm__nexta"><a class="button button--primary" href="' + COMPARE + '">' + T.errorBtn + ARW + "</a></p></div>";
  }

  function finish(first) {
    save(true);
    load().then(function () {
      renderResult(first);
    }, showError);
  }

  root.addEventListener("click", function (e) {
    var opt = e.target.closest(".sm__opt");
    if (opt) {
      if (root.querySelector(".sm__opt.is-picked")) return;
      if (!started) {
        started = true;
        ev("match_start");
        load().catch(function () {});
      }
      ans[QS[step].id] = opt.getAttribute("data-v");
      save(false);
      root.querySelectorAll(".sm__opt").forEach(function (b) {
        b.classList.remove("is-on");
      });
      opt.classList.add("is-on", "is-picked");
      setTimeout(function () {
        if (step < QS.length - 1) {
          step++;
          renderQ("next");
        } else finish(true);
      }, 260);
      return;
    }
    if (e.target.closest("[data-back]")) {
      step = Math.max(0, step - 1);
      renderQ("prev");
      return;
    }
    if (e.target.closest("[data-redo]")) {
      step = 0;
      save(false);
      renderQ("prev");
      ev("match_redo");
    }
  });

  /* 学校のページから戻ってきたときは、結果をそのまま出す */
  var saved = null;
  try {
    saved = JSON.parse(sessionStorage.getItem(KEY) || "null");
  } catch (e) {}
  if (saved && saved.ans && saved.done) {
    ans = saved.ans;
    started = true;
    renderQ();
    finish(false);
  } else {
    renderQ();
  }
})();

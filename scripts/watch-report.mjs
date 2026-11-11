/* ============================================================
 * 見はり番のまとめ: 2つの見はり番(キャンペーン・学校の情報)の結果を、
 * ちゃんが読む1枚 data/watch-status.md にまとめる。「対応が要るもの」が先頭。
 *
 * ・この1枚は、GitHub の「見はり番のまとめ」Issue の本文にもそのまま使う(毎日書きかえる。メールは出ない)。
 * ・前回のまとめにない項目が出た日だけ watch-comment.md を作る(Issue にコメント1つ=メール1通)。
 *   月曜は、残っている項目があれば「まだ残っています」も同じコメントに入れる。
 * ・残っている間は毎日まとめに出し続け、直ったら自動で消える。
 * ・手元でも動く: node scripts/watch-report.mjs [--today=2026-11-16]
 *   (いまいる場所の data/ を読み、data/watch-status.md と watch-comment.md を書く)
 * ============================================================ */
import { readFileSync, writeFileSync, existsSync, rmSync } from "node:fs";

const DB = "data/schools.json";
const SCHOOLS = "data/schools-watch.json";
const CAMPAIGN = "data/campaign-watch.json";
const STATUS = "data/watch-status.md";
const COMMENT = "watch-comment.md";

/** 何日つづけて見つからなかったら出すか(1日だけの表示くずれで騒がないため) */
const MISS_DAYS = 2;
/** 何日つづけてページを取得できなかったら出すか */
const FAIL_DAYS = 3;
/** 手で見る項目は、最後に確かめた日から何日で出すか */
const MANUAL_DAYS = 30;

const arg = process.argv.find((a) => a.startsWith("--today="));
/* 見はり番の日 = 日本時間から6時間引いた日付(2つの見はり番と同じ。遅れて0時を回っても前の晩の日付) */
const TODAY = arg ? arg.slice(8) : new Date(Date.now() + (9 - 6) * 3600 * 1000).toISOString().slice(0, 10);

const read = (f, empty) => (existsSync(f) ? JSON.parse(readFileSync(f, "utf8")) : empty);
const md = (d) => (d ? `${Number(d.slice(5, 7))}/${Number(d.slice(8, 10))}` : "記録なし");
const daysSince = (d) => Math.round((Date.parse(TODAY) - Date.parse(d)) / 86400000);
const addDays = (d, n) => new Date(Date.parse(d) + n * 86400000).toISOString().slice(0, 10);
const WEEK = "日月火水木金土";

const db = read(DB, { schools: [] });
const sw = read(SCHOOLS, { items: {}, pages: {} });
const cw = read(CAMPAIGN, { schools: {}, recent: [] });

/* 対応が要るもの。key は「前回もあったか」をくらべるための名前 */
const groups = {
  school: { title: "学校の情報が、公式ページで見つからない", hint: "料金・日程・条件が変わったかもしれません。Claude に「学校の情報を確かめて直して」と伝えると、公式ページを読み直して直します(ページの書き方が変わっただけのこともあります)。", list: [] },
  campaign: { title: "キャンペーンの文が増えた・消えた(この7日)", hint: "サイトにはまだ何も載せていません。載せたいものがあれば Claude に「これを載せて」と伝えてください(載せる前に公式ページで期間・条件を確かめます)。7日たつと、ここから消えます。", list: [] },
  manual: { title: "手で見る日です", hint: "機械では読めない学校です。公式ページを開いて、いまの記録と同じかを見てください。見たら Claude に「◯◯を手で確かめた」と伝えると、確かめた日を書きかえます。", list: [] },
  stuck: { title: "ページを開けない・見はり番が動かなかった", hint: "学校のページの住所が変わったか、一時的に止まっているかもしれません。Claude に「見はり番のページを確かめて」と伝えてください。", list: [] },
};
const add = (g, key, short, text) => groups[g].list.push({ key, short, text });

const manualNotes = [];
for (const school of db.schools) {
  for (const [name, item] of Object.entries(school.items ?? {})) {
    const w = item.watch;
    if (!w) continue;
    const label = `${school.shortName}｜${name}`;
    if (w.manual) {
      const last = w.lastManualCheck ?? item.checkedAt;
      const due = addDays(last, MANUAL_DAYS);
      if (TODAY >= due) {
        add("manual", `m|${school.slug}|${name}`, label,
          `**${label}**：最後に手で確かめたのは ${md(last)}(${daysSince(last)}日前)。\n  - いまの記録: ${item.value}\n  - 見るページ: ${w.url}`);
      } else manualNotes.push(`${label}(次に手で見る日 ${md(due)})`);
      continue;
    }
    const st = sw.items?.[`${school.slug}|${name}`];
    if (st && (st.miss ?? 0) >= MISS_DAYS) {
      add("school", `s|${school.slug}|${name}`, label,
        `**${label}**：「${(st.lost ?? []).join("」「")}」が見つかりません(${st.miss}日つづけて・最後に確認できた日 ${md(st.lastSeen)})。\n  - いまの記録: ${item.value}\n  - 見ているページ: ${w.url}`);
    }
  }
}

for (const r of [...(cw.recent ?? [])].sort((a, b) => (a.date < b.date ? 1 : -1))) {
  const mark = r.kind === "消えた" ? `~~${r.text}~~` : r.text;
  add("campaign", `c|${r.date}|${r.url}|${r.kind}|${r.text}`, `${r.school} ${r.kind}`,
    `${md(r.date)} **${r.school}** ${r.kind}：${mark}\n  - ${r.url}`);
}

for (const [url, p] of Object.entries(sw.pages ?? {})) {
  if ((p.fails ?? 0) >= FAIL_DAYS) add("stuck", `p|${url}`, `ページを開けない ${url}`, `学校の情報のページを ${p.fails}日つづけて開けません(${p.error ?? "理由不明"})：${url}`);
}
for (const s of Object.values(cw.schools ?? {})) {
  for (const [url, p] of Object.entries(s.pages ?? {})) {
    if ((p.fails ?? 0) >= FAIL_DAYS) add("stuck", `p|${url}`, `${s.name}のページを開けない`,`${s.name}のキャンペーンのページを ${p.fails}日つづけて開けません(${p.error ?? "理由不明"})：${url}`);
  }
}
if (sw.checked !== TODAY) add("stuck", "x|schools", "学校の情報の見はり番が動かなかった",`学校の情報の見はり番が今日は最後まで動きませんでした(最後に動いた日 ${md(sw.checked)})。`);
if (cw.checked !== TODAY) add("stuck", "x|campaign", "キャンペーンの見はり番が動かなかった",`キャンペーンの見はり番が今日は最後まで動きませんでした(最後に動いた日 ${md(cw.checked)})。`);

/* 前回のまとめにあった項目 */
let before = [];
let hadStatus = false;
if (existsSync(STATUS)) {
  const m = readFileSync(STATUS, "utf8").match(/<!-- watch-keys: (.*) -->/);
  if (m) {
    before = JSON.parse(m[1]);
    hadStatus = true;
  }
}
const all = Object.values(groups).flatMap((g) => g.list);
const fresh = all.filter((a) => !before.includes(a.key));
const total = all.length;

/* まとめの1枚 */
const d = new Date(Date.parse(TODAY));
const out = [
  "# 見はり番のまとめ(carepicnic)",
  "",
  `${md(TODAY)}(${WEEK[d.getUTCDay()]})の夜に見た結果です。毎日この1枚を書きかえます。`,
  "",
  total ? `## 対応が要るもの(${total}件)` : "## 対応が要るもの：なし",
  "",
];
for (const g of Object.values(groups)) {
  if (!g.list.length) continue;
  out.push(`### ${g.title}(${g.list.length}件)`, "", g.hint, "");
  for (const a of g.list) out.push(`- ${before.includes(a.key) || !hadStatus ? "" : "【新】"}${a.text}`);
  out.push("");
}
const sum = sw.summary ?? {};
out.push(
  "## ふだんの様子",
  "",
  `- 学校の情報：${sum.watched ?? "?"}項目のうち ${sum.seen ?? "?"}項目を公式ページで確認できました(${md(sw.checked)})。`,
  `- キャンペーン：${Object.keys(cw.schools ?? {}).length}校の公式ページを見ました(${md(cw.checked)})。言い回しだけの変化(金額・日付が同じ)は知らせません。`,
  ...(manualNotes.length ? [`- 手で見る学校：${manualNotes.join("、")}`] : []),
  ""
);
const rewords = [...(cw.rewords ?? [])].sort((a, b) => (a.date < b.date ? 1 : -1));
if (rewords.length) {
  out.push("### 念のため：言い回しだけの変化として知らせなかったもの(7日分)", "");
  for (const r of rewords) out.push(`- ${md(r.date)} ${r.school}：「${r.from}」→「${r.to}」`);
  out.push("");
}
out.push(
  "サイトは自動では変えていません。直す・載せるは、ちゃんが決めてから。",
  "",
  `<!-- watch-keys: ${JSON.stringify(all.map((a) => a.key)).replace(/>/g, "\\u003e")} -->`,
  ""
);
writeFileSync(STATUS, out.join("\n"));

/* コメント(=メール1通)を出すか */
if (existsSync(COMMENT)) rmSync(COMMENT);
const comment = [];
if (fresh.length && hadStatus) {
  comment.push(`新しく ${fresh.length}件 出ました。くわしくは、この Issue のいちばん上(本文)を見てください。`, "");
  for (const a of fresh) comment.push(`- ${a.short}`);
}
if (d.getUTCDay() === 1 && total > fresh.length) {
  const left = all.filter((a) => !fresh.includes(a));
  if (comment.length) comment.push("");
  comment.push(`まだ残っています(${left.length}件)。`, "");
  for (const a of left) comment.push(`- ${a.short}`);
}
if (comment.length) {
  writeFileSync(COMMENT, comment.join("\n") + "\n");
  console.log(`コメントあり → ${COMMENT}`);
}
console.log(`対応が要るもの ${total}件(新しく ${hadStatus ? fresh.length : "-"}件) → ${STATUS}`);

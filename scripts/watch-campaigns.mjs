/* ============================================================
 * 学校のキャンペーン見はり番: 各校の公式ページを毎日見に行き、
 * 「キャンペーン・割引・特典」などの文が増えたり消えたりしたら記録する。
 *
 * ・サイトには自動で載せない。見つけた変化は data/campaign-watch.json の recent(7日分)に残し、
 *   scripts/watch-report.mjs がまとめ(data/watch-status.md と「見はり番のまとめ」Issue)に出す。
 *   載せるかどうかは人が決める。
 * ・言い回しだけの変化(金額・日付・％などが同じで、文がほぼ同じ)は知らせない。
 *   例: 「BLACK FRYDAY」→「BLACK FRIDAY」の打ち間違いの直し。
 * ・前回の内容は data/campaign-watch.json に残す(くらべるための控え)。
 * ・手元でも動く: node scripts/watch-campaigns.mjs(いまいる場所の data/ を読み書きする)
 * 見に行くページを足すときは SCHOOLS に書く。
 * ============================================================ */
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { pathToFileURL } from "node:url";

const OUT = "data/campaign-watch.json";

const SCHOOLS = [
  { id: "chiiki", name: "地域連携プラットフォーム", pages: ["https://careerjp.work/cc1/", "https://careerjp.work/cc1/tokuten"] },
  { id: "human", name: "ヒューマンアカデミー", pages: ["https://haa.athuman.com/academy/career/"] },
  { id: "lec", name: "LEC東京リーガルマインド", pages: ["https://www.lec-jp.com/caricon/kouza/yousei/", "https://www.lec-jp.com/caricon/campaign/"] },
  { id: "manpower", name: "日本マンパワー", pages: ["https://www.nipponmanpower.co.jp/cc/", "https://www.nipponmanpower.co.jp/cc/briefing_session/setsumei"] },
  { id: "pasona", name: "パソナ", pages: ["https://100-year-career.net/"] },
  { id: "recurrent", name: "リカレント", pages: ["https://www.recurrent.co.jp/cc/", "https://www.recurrent.co.jp/cc/course/"] },
  { id: "cmca", name: "CMCA", pages: ["https://cmcajapan.com/lp/setsumeikai", "https://cmcajapan.net/"] },
];

/** この言葉を含む文だけを拾う */
const KEYWORDS = /キャンペーン|割引|早割|特典|クーポン|円引|円OFF|円オフ|％OFF|%OFF|プレゼント|受講料.{0,6}(無料|免除)|入学金.{0,6}(無料|免除|0円)/;
/** 見はりを始めた日の一覧に出すのは、期間や金額がわかる文だけ(多すぎると読めないため) */
const STRONG = /キャンペーン|早割|限定|まで|[0-9０-９][0-9０-９,，]*\s*(円|％|%)/;
const FIRST_MAX = 12;
/** recent に残す日数 */
const KEEP_DAYS = 7;

/* ---------- 言い回しだけの変化を見分ける ---------- */

/** 中身の数字(金額・％・倍・日付・時刻・期間・人数)を取り出す。「第35回」のような回数は数えない */
const FACT = /[0-9]+(?:\.[0-9]+)?(?:万円|万|円|%|倍|か月|ヶ月|カ月|ヵ月|月|日|年|時|名|人)|[0-9]{1,2}\/[0-9]{1,2}|[0-9]{1,2}:[0-9]{2}/g;
/** 終わった・締め切ったことを表す言葉(これが増えた・消えたときは、文が似ていても知らせる) */
const ENDED = /終了しました|受付終了|締め?切りました|締切済|満席|中止/;
const KW_WORDS = /キャンペーン|割引|早割|特典|クーポン|円引|OFF|オフ|プレゼント|無料|免除/g;

const flat = (s) => s.normalize("NFKC").replace(/[\s,，]/g, "");
export function facts(s) {
  return [...new Set(flat(s).match(FACT) ?? [])].sort().join("|");
}
function kinds(s) {
  return [...new Set(flat(s).match(KW_WORDS) ?? [])].sort().join("|");
}
function bigrams(s) {
  const t = flat(s);
  const out = new Map();
  for (let i = 0; i < t.length - 1; i++) {
    const g = t.slice(i, i + 2);
    out.set(g, (out.get(g) ?? 0) + 1);
  }
  return out;
}
/** 2つの文の似ている度合い(0〜1・文字の2つ組の重なり) */
export function similarity(a, b) {
  const A = bigrams(a);
  const B = bigrams(b);
  let both = 0;
  let total = 0;
  for (const [g, n] of A) {
    both += Math.min(n, B.get(g) ?? 0);
    total += n;
  }
  for (const n of B.values()) total += n;
  return total ? (2 * both) / total : 1;
}
const SIMILAR = 0.6;
/** 消えた文と増えた文が、同じ中身の言いかえか */
export function isReword(oldText, newText) {
  return (
    facts(oldText) === facts(newText) &&
    kinds(oldText) === kinds(newText) &&
    ENDED.test(oldText) === ENDED.test(newText) &&
    similarity(oldText, newText) >= SIMILAR
  );
}

/** 増えた・消えたの組から、言いかえの組を外す(似ている順に1対1で組む) */
export function dropRewords(added, removed) {
  const pairs = [];
  for (const a of added) for (const r of removed) if (isReword(r, a)) pairs.push([similarity(r, a), a, r]);
  pairs.sort((x, y) => y[0] - x[0]);
  const usedA = new Set();
  const usedR = new Set();
  const rewords = [];
  for (const [, a, r] of pairs) {
    if (usedA.has(a) || usedR.has(r)) continue;
    usedA.add(a);
    usedR.add(r);
    rewords.push({ from: r, to: a });
  }
  return {
    added: added.filter((s) => !usedA.has(s)),
    removed: removed.filter((s) => !usedR.has(s)),
    rewords,
  };
}

/* ---------- ページを読む ---------- */

function decode(s) {
  return s
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;|&apos;/g, "'")
    .replace(/&#(\d+);/g, (_, n) => String.fromCodePoint(Number(n)))
    .replace(/&#x([0-9a-f]+);/gi, (_, n) => String.fromCodePoint(parseInt(n, 16)));
}

/** ページの文字コード(Shift_JIS など)に合わせて読む */
async function fetchHtml(url) {
  const res = await fetch(url, {
    headers: {
      "user-agent": "Mozilla/5.0 (compatible; carepicnic-campaign-watch; +https://carepicnic.com/)",
      "accept-language": "ja",
    },
    redirect: "follow",
    signal: AbortSignal.timeout(30000),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const bytes = new Uint8Array(await res.arrayBuffer());
  const head = new TextDecoder("latin1").decode(bytes.slice(0, 3000));
  const charset =
    (res.headers.get("content-type") || "").match(/charset=([\w-]+)/i)?.[1] ||
    head.match(/<meta[^>]+charset=["']?([\w-]+)/i)?.[1] ||
    "utf-8";
  try {
    return new TextDecoder(charset).decode(bytes);
  } catch {
    return new TextDecoder("utf-8").decode(bytes);
  }
}

/** HTML から、キャンペーンらしい文を取り出す(1行=1文。重複はまとめる) */
function snippets(html) {
  const text = decode(
    html
      .replace(/<(script|style|noscript|svg)[\s\S]*?<\/\1>/gi, " ")
      .replace(/<!--[\s\S]*?-->/g, " ")
      .replace(/<img[^>]*\balt=["']([^"']*)["'][^>]*>/gi, " $1 ")
      .replace(/<\/?(p|div|li|ul|ol|dl|dt|dd|tr|td|th|table|section|article|header|footer|nav|aside|h[1-6]|br|a|button|figure|figcaption|label|span)\b[^>]*>/gi, "\n")
      .replace(/<[^>]+>/g, " ")
  );
  const found = new Set();
  for (const raw of text.split(/\n|(?<=。)/)) {
    const line = raw.replace(/\s+/g, " ").trim();
    if (line.length < 6 || line.length > 160) continue;
    if (!KEYWORDS.test(line)) continue;
    found.add(line);
  }
  return [...found].sort();
}

export function today() {
  /* 見はり番の日 = 日本時間から6時間引いた日付(19時台に動く予定が遅れて0時を回っても、前の晩の日付にする) */
  return new Date(Date.now() + (9 - 6) * 3600 * 1000).toISOString().slice(0, 10);
}
function daysBefore(date, n) {
  return new Date(Date.parse(date + "T00:00:00Z") - n * 86400000).toISOString().slice(0, 10);
}

async function main() {
  const prev = existsSync(OUT) ? JSON.parse(readFileSync(OUT, "utf8")) : { schools: {} };
  const first = !existsSync(OUT);
  const day = today();
  /* 前の日までの変化(古い形の控えには無いので空から始める) */
  const keep = (r) => r.date > daysBefore(day, KEEP_DAYS);
  const recent = (prev.recent ?? []).filter(keep);
  /* 言い回しだけの変化として知らせなかったもの(念のため7日分。まとめの下のほうに出す) */
  const rewords = (prev.rewords ?? []).filter(keep);
  const next = { checked: day, schools: {}, recent, rewords };

  for (const school of SCHOOLS) {
    const before = prev.schools?.[school.id] ?? { pages: {} };
    const now = { name: school.name, pages: {} };
    const shown = new Set(); /* 同じ学校の別ページに同じ文があっても、1回だけ出す */
    const fresh = (list) => list.filter((s) => !shown.has(s) && shown.add(s));
    const note = (kind, url, text) => recent.push({ date: day, school: school.name, url, kind, text });

    for (const url of school.pages) {
      const old = before.pages?.[url] ?? { snippets: [], fails: 0 };
      try {
        const list = snippets(await fetchHtml(url));
        now.pages[url] = { snippets: list, fails: 0 };
        if (first || !(url in (before.pages ?? {}))) {
          for (const s of fresh(list.filter((s) => STRONG.test(s))).slice(0, FIRST_MAX)) note("いま載っている", url, s);
          continue;
        }
        const diff = dropRewords(
          list.filter((s) => !old.snippets.includes(s)),
          old.snippets.filter((s) => !list.includes(s))
        );
        for (const r of diff.rewords) {
          console.log(`${school.name}: 言い回しだけの変化なので知らせない「${r.from}」→「${r.to}」`);
          rewords.push({ date: day, school: school.name, url, from: r.from, to: r.to });
        }
        for (const s of fresh(diff.added)) note("増えた", url, s);
        for (const s of fresh(diff.removed)) note("消えた", url, s);
      } catch (e) {
        /* 取得できない日は、前回の内容をそのまま残す(変化あつかいにしない) */
        const fails = (old.fails ?? 0) + 1;
        now.pages[url] = { snippets: old.snippets, fails, error: String(e.message) };
        console.log(`${school.name}: 取得できず ${url} (${e.message})`);
      }
    }
    next.schools[school.id] = now;
    console.log(`${school.name}: ${Object.values(now.pages).reduce((n, p) => n + p.snippets.length, 0)}件`);
  }

  writeFileSync(OUT, JSON.stringify(next, null, 1) + "\n");
  const todays = recent.filter((r) => r.date === day).length;
  console.log(todays ? `変化あり ${todays}件 → ${OUT} の recent` : "変化なし");
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch((e) => {
    console.error(e);
    process.exit(1);
  });
}

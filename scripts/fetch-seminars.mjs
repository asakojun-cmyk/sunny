/* ============================================================
 * マルシェのセミナー屋台: 厚生労働省の新着情報RSSから、
 * セミナー・シンポジウム・フォーラムなど「参加できるイベント」の
 * 案内だけを選んで seminars.json に蓄積するスクリプト。
 * GitHub Actions が毎日実行する(手元で node scripts/fetch-seminars.mjs でも動く)。
 * 仕組みは scripts/fetch-news.mjs と同じ。
 * ============================================================ */
import { readFileSync, writeFileSync, existsSync } from "node:fs";

const FEED_URL = "https://www.mhlw.go.jp/stf/news.rdf";
const OUT = "seminars.json";
const MAX_ITEMS = 60;

/** 「参加できるイベントの案内」とみなすキーワード(タイトルに1つでも含めば候補) */
const EVENT_KEYWORDS = [
  "セミナー", "シンポジウム", "フォーラム", "説明会", "講演",
  "公開講座", "ワークショップ", "研修会", "参加者募集", "イベント",
  "オンライン開催", "開催します", "開催のお知らせ",
];

/** キャリコン関連とみなすキーワード(こちらも1つ以上含むこと。イベント×キャリアの二段しぼり) */
const CAREER_KEYWORDS = [
  "キャリア", "職業", "雇用", "労働", "働き方", "就職", "就労", "人材",
  "能力開発", "職業訓練", "教育訓練", "リスキリング", "リカレント",
  "ジョブ・カード", "ジョブカード", "両立支援", "女性活躍", "育児", "介護",
  "障害者", "高年齢者", "若者", "若年", "テレワーク", "副業", "兼業",
  "ハラスメント", "メンタルヘルス", "過労死", "安全衛生", "求職", "求人",
];

function pick(re, s) {
  const m = s.match(re);
  return m ? m[1].trim() : "";
}

function decode(s) {
  return s
    .replace(/<!\[CDATA\[(.*?)\]\]>/gs, "$1")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .trim();
}

function toIsoDate(s) {
  if (!s) return "";
  const d = new Date(s);
  if (Number.isNaN(d.getTime())) return s.slice(0, 10);
  return d.toISOString().slice(0, 10);
}

async function main() {
  const res = await fetch(FEED_URL, {
    headers: { "user-agent": "marche-seminar-bot (personal study site)" },
  });
  if (!res.ok) throw new Error(`RSS fetch failed: ${res.status}`);
  const xml = await res.text();

  const fresh = [];
  const itemRe = /<item[\s\S]*?<\/item>/g;
  for (const block of xml.match(itemRe) ?? []) {
    const title = decode(pick(/<title>([\s\S]*?)<\/title>/, block));
    const link = decode(pick(/<link>([\s\S]*?)<\/link>/, block));
    const date =
      decode(pick(/<dc:date>([\s\S]*?)<\/dc:date>/, block)) ||
      decode(pick(/<pubDate>([\s\S]*?)<\/pubDate>/, block));
    if (!title || !link) continue;
    if (!EVENT_KEYWORDS.some((k) => title.includes(k))) continue;
    if (!CAREER_KEYWORDS.some((k) => title.includes(k))) continue;
    fresh.push({ title, url: link, date: toIsoDate(date), source: "厚生労働省" });
  }

  /* 既存の items と合流(URLで重複排除)して、日付の新しい順に並べる */
  let existing = [];
  if (existsSync(OUT)) {
    try {
      existing = JSON.parse(readFileSync(OUT, "utf8")).items ?? [];
    } catch {
      existing = [];
    }
  }
  const seen = new Set();
  const merged = [];
  for (const it of [...fresh, ...existing]) {
    if (seen.has(it.url)) continue;
    seen.add(it.url);
    merged.push(it);
  }
  merged.sort((a, b) => (b.date || "").localeCompare(a.date || ""));

  const out = {
    updated: new Date().toISOString().slice(0, 10),
    items: merged.slice(0, MAX_ITEMS),
  };
  writeFileSync(OUT, JSON.stringify(out, null, 1) + "\n", "utf8");
  console.log(`seminars.json updated: ${out.items.length} items (fresh: ${fresh.length})`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});

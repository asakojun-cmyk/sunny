/* ============================================================
 * キャリコンNOW: 厚生労働省の新着情報RSSから、
 * キャリアコンサルタントに関係するニュースだけを選んで
 * news-feed.json に蓄積するスクリプト。
 * GitHub Actions が毎日実行する(手元で node scripts/fetch-news.mjs でも動く)。
 * ============================================================ */
import { readFileSync, writeFileSync, existsSync } from "node:fs";

const FEED_URL = "https://www.mhlw.go.jp/stf/news.rdf";
const OUT = "news-feed.json";
const MAX_ITEMS = 250;

/** キャリコン関連とみなすキーワード(タイトルに1つでも含めば採用) */
const KEYWORDS = [
  "キャリアコンサル", "キャリア形成", "職業能力", "能力開発", "職業訓練",
  "教育訓練", "リスキリング", "リカレント", "ジョブ・カード", "ジョブカード",
  "雇用", "労働", "賃金", "最低賃金", "求人", "求職", "失業", "就職", "就労",
  "働き方", "副業", "兼業", "テレワーク", "フリーランス",
  "育児", "介護休業", "育児休業", "両立支援", "女性活躍",
  "障害者", "高年齢者", "高齢者雇用", "若者", "若年", "新卒",
  "ハローワーク", "労災", "安全衛生", "メンタルヘルス", "ストレスチェック",
  "パワーハラスメント", "ハラスメント", "過労死",
  "有効求人倍率", "毎月勤労統計", "労働力調査", "白書", "統計",
  "職業安定", "人材開発", "技能検定", "求職者支援",
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

async function main() {
  const res = await fetch(FEED_URL, {
    headers: { "user-agent": "kyarikon-now-bot (personal study site)" },
  });
  if (!res.ok) throw new Error(`RSS fetch failed: ${res.status}`);
  const xml = await res.text();

  const items = [];
  const itemRe = /<item[\s\S]*?<\/item>/g;
  for (const block of xml.match(itemRe) ?? []) {
    const title = decode(pick(/<title>([\s\S]*?)<\/title>/, block));
    const link = decode(pick(/<link>([\s\S]*?)<\/link>/, block));
    const date =
      decode(pick(/<dc:date>([\s\S]*?)<\/dc:date>/, block)) ||
      decode(pick(/<pubDate>([\s\S]*?)<\/pubDate>/, block));
    if (!title || !link) continue;
    if (!KEYWORDS.some((k) => title.includes(k))) continue;
    items.push({
      title,
      url: link,
      date: date ? date.slice(0, 10) : "",
      source: "厚生労働省",
    });
  }

  let feed = { updated: "", items: [] };
  if (existsSync(OUT)) {
    try {
      feed = JSON.parse(readFileSync(OUT, "utf8"));
    } catch {
      /* 壊れていたら作り直す */
    }
  }

  const known = new Set((feed.items ?? []).map((i) => i.url));
  const fresh = items.filter((i) => !known.has(i.url));
  const merged = [...fresh, ...(feed.items ?? [])]
    .sort((a, b) => (b.date || "").localeCompare(a.date || ""))
    .slice(0, MAX_ITEMS);

  writeFileSync(
    OUT,
    JSON.stringify(
      { updated: new Date().toISOString().slice(0, 10), items: merged },
      null,
      1
    )
  );
  console.log(`news-feed.json: +${fresh.length} new, total ${merged.length}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});

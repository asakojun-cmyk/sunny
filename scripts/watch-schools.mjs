/* ============================================================
 * 学校の情報の見はり番: 元データ(data/schools.json)に入っている事実が、
 * いまも各校の公式ページに書かれているかを、毎日たしかめる。
 *
 * ・schools.json の各項目にある watch(url と tokens)を使う。
 *   url のページに tokens(金額・時間・日付・固有のことば)が残っていれば「確認できた」。
 * ・確認できた日は data/schools-watch.json に自動で書きこむ(項目ごとの lastSeen)。
 * ・見つからない日数(miss)・ページを取れない日数(fails)も同じファイルに残す。
 *   知らせるのは scripts/watch-report.mjs(残っている間は、まとめに出し続ける)。
 * ・watch.manual が true の項目(機械では読めない学校のページ)は取りに行かない。
 *   watch.lastManualCheck(最後に手で確かめた日)から30日たつと、まとめに「手で見る日です」と出る。
 * ・サイトと schools.json の中身は、自動では書きかえない(人が確かめてから直す)。
 * ・手元でも動く: node scripts/watch-schools.mjs(いまいる場所の data/ を読み書きする)
 * ============================================================ */
import { readFileSync, writeFileSync, existsSync } from "node:fs";

const DB = "data/schools.json";
const OUT = "data/schools-watch.json";

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

/** くらべやすい形にそろえる(全角→半角、「ヶ月・カ月」→「か月」、空白と読点・カンマをとる) */
function norm(s) {
  return s
    .normalize("NFKC")
    .replace(/[ヶヵケカか]月/g, "か月")
    .replace(/[\s,、]/g, "");
}

async function fetchText(url) {
  const res = await fetch(url, {
    headers: {
      "user-agent": "Mozilla/5.0 (compatible; carepicnic-school-watch; +https://carepicnic.com/)",
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
  let html;
  try {
    html = new TextDecoder(charset).decode(bytes);
  } catch {
    html = new TextDecoder("utf-8").decode(bytes);
  }
  return norm(
    decode(
      html
        .replace(/<(script|style|noscript)[\s\S]*?<\/\1>/gi, " ")
        .replace(/<img[^>]*\balt=["']([^"']*)["'][^>]*>/gi, " $1 ")
        .replace(/<[^>]+>/g, " ")
    )
  );
}

function today() {
  /* 見はり番の日 = 日本時間から6時間引いた日付(遅れて0時を回っても、前の晩の日付にする) */
  return new Date(Date.now() + (9 - 6) * 3600 * 1000).toISOString().slice(0, 10);
}

async function main() {
  const db = JSON.parse(readFileSync(DB, "utf8"));
  const prev = existsSync(OUT) ? JSON.parse(readFileSync(OUT, "utf8")) : { items: {}, pages: {} };
  const next = { checked: today(), summary: {}, items: {}, pages: {} };

  /* 見に行くページを集める(手で見る項目は、前回の記録をそのまま残すだけ) */
  const targets = [];
  let manual = 0;
  for (const school of db.schools) {
    for (const [name, item] of Object.entries(school.items)) {
      if (item.watch?.manual) {
        const key = `${school.slug}|${name}`;
        if (prev.items?.[key]) next.items[key] = prev.items[key];
        manual++;
      } else if (item.watch?.url && item.watch.tokens?.length) targets.push({ school, name, item });
    }
  }
  const urls = [...new Set(targets.map((t) => t.item.watch.url))];
  const pages = {};
  for (const url of urls) {
    const old = prev.pages?.[url] ?? { fails: 0 };
    try {
      pages[url] = await fetchText(url);
      next.pages[url] = { fails: 0 };
    } catch (e) {
      pages[url] = null;
      next.pages[url] = { fails: (old.fails ?? 0) + 1, error: String(e.message) };
      console.log(`取得できず ${url} (${e.message})`);
    }
  }

  let seen = 0;
  let missing = 0;
  let skipped = 0;

  for (const { school, name, item } of targets) {
    const key = `${school.slug}|${name}`;
    const old = prev.items?.[key] ?? { lastSeen: null, miss: 0 };
    const text = pages[item.watch.url];
    if (text === null) {
      /* 取得できない日は、前回の記録をそのまま残す(変化あつかいにしない) */
      next.items[key] = old;
      skipped++;
      continue;
    }
    const lost = item.watch.tokens.filter((t) => !text.includes(norm(t)));
    if (lost.length === 0) {
      next.items[key] = { lastSeen: today(), miss: 0 };
      seen++;
    } else {
      next.items[key] = { lastSeen: old.lastSeen, miss: (old.miss ?? 0) + 1, lost };
      missing++;
    }
  }

  next.summary = { watched: targets.length, seen, missing, skipped, manual, pages: urls.length };
  writeFileSync(OUT, JSON.stringify(next, null, 1) + "\n");
  console.log(`見はり中 ${targets.length}項目 / 確認できた ${seen} / 見つからない ${missing} / 取得できず ${skipped} / 手で見る ${manual}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});

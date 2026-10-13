/* ============================================================
 * 学校の情報の見はり番: 元データ(data/schools.json)に入っている事実が、
 * いまも各校の公式ページに書かれているかを、毎日たしかめる。
 *
 * ・schools.json の各項目にある watch(url と tokens)を使う。
 *   url のページに tokens(金額・時間・日付・固有のことば)が残っていれば「確認できた」。
 * ・確認できた日は data/schools-watch.json に自動で書きこむ(項目ごとの lastSeen)。
 * ・2日つづけて見つからない項目があれば schools-notice.md に書き出し、
 *   GitHub Actions が Issue にして運営者に知らせる。
 * ・サイトと schools.json の中身は、自動では書きかえない(人が確かめてから直す)。
 * ・手元でも動く: node scripts/watch-schools.mjs
 * ============================================================ */
import { readFileSync, writeFileSync, existsSync, rmSync } from "node:fs";

const DB = "data/schools.json";
const OUT = "data/schools-watch.json";
const NOTICE = "schools-notice.md";
/** 何日つづけて見つからなかったら知らせるか(1日だけの表示くずれで騒がないため) */
const MISS_DAYS = 2;
/** 何日つづけてページを取得できなかったら知らせるか */
const FAIL_DAYS = 3;

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
  return new Date(Date.now() + 9 * 3600 * 1000).toISOString().slice(0, 10);
}

async function main() {
  const db = JSON.parse(readFileSync(DB, "utf8"));
  const prev = existsSync(OUT) ? JSON.parse(readFileSync(OUT, "utf8")) : { items: {}, pages: {} };
  const next = { checked: today(), summary: {}, items: {}, pages: {} };

  /* 見に行くページを集める */
  const targets = [];
  for (const school of db.schools) {
    for (const [name, item] of Object.entries(school.items)) {
      if (item.watch?.url && item.watch.tokens?.length) targets.push({ school, name, item });
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

  const report = {};
  const add = (school, line) => (report[school] ??= []).push(line);
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
      const miss = (old.miss ?? 0) + 1;
      next.items[key] = { lastSeen: old.lastSeen, miss, lost };
      missing++;
      if (miss === MISS_DAYS) {
        add(
          school.shortName,
          `- **${name}**: 「${lost.join("」「")}」が公式ページから見つかりません。\n  - いまの記録: ${item.value}\n  - 見ているページ: ${item.watch.url}\n  - 最後に確認できた日: ${old.lastSeen ?? "記録なし"}`
        );
      }
    }
  }
  for (const [url, p] of Object.entries(next.pages)) {
    if (p.fails === FAIL_DAYS) add("ページを取得できません", `- ${FAIL_DAYS}日つづけて取得できていません: ${url} (${p.error})`);
  }

  next.summary = { watched: targets.length, seen, missing, skipped, pages: urls.length };
  writeFileSync(OUT, JSON.stringify(next, null, 1) + "\n");
  console.log(`見はり中 ${targets.length}項目 / 確認できた ${seen} / 見つからない ${missing} / 取得できず ${skipped}`);

  if (existsSync(NOTICE)) rmSync(NOTICE);
  const names = Object.keys(report);
  if (names.length) {
    writeFileSync(
      NOTICE,
      [
        "比較表や学校ページの元になっている事実のうち、公式ページから見つからなくなったものがあります。",
        "料金・日程・条件が変わった可能性があります。",
        "",
        "サイトはまだ何も変えていません。Claude に「学校の情報を確かめて直して」と伝えると、公式ページを読み直して、元データ(data/schools.json)・比較表・学校ページをそろえて直します。",
        "機械でくらべているので、ページの書き方が変わっただけ(金額は同じ)のこともあります。",
        "",
        ...names.flatMap((n) => [`## ${n}`, "", ...report[n], ""]),
      ].join("\n")
    );
    console.log("知らせることあり → " + NOTICE);
  } else {
    console.log("知らせることなし");
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});

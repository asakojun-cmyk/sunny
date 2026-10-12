/* ============================================================
 * 学校のキャンペーン見はり番: 各校の公式ページを毎日見に行き、
 * 「キャンペーン・割引・特典」などの文が増えたり消えたりしたら知らせる。
 *
 * ・サイトには自動で載せない。見つけた変化を campaign-notice.md に書き出し、
 *   GitHub Actions がそれを Issue にして運営者に通知する(載せるかどうかは人が決める)。
 * ・前回の内容は data/campaign-watch.json に残す(くらべるための控え)。
 * ・手元でも動く: node scripts/watch-campaigns.mjs
 * 見に行くページを足すときは SCHOOLS に書く。
 * ============================================================ */
import { readFileSync, writeFileSync, existsSync, rmSync } from "node:fs";

const OUT = "data/campaign-watch.json";
const NOTICE = "campaign-notice.md";

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
/** 何日つづけて取得できなかったら知らせるか */
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

function today() {
  /* 日本時間の日付 */
  return new Date(Date.now() + 9 * 3600 * 1000).toISOString().slice(0, 10);
}

async function main() {
  const prev = existsSync(OUT) ? JSON.parse(readFileSync(OUT, "utf8")) : { schools: {} };
  const first = !existsSync(OUT);
  const next = { checked: today(), schools: {} };
  const report = [];

  for (const school of SCHOOLS) {
    const before = prev.schools[school.id] ?? { pages: {} };
    const now = { name: school.name, pages: {} };
    const lines = [];
    const shown = new Set(); /* 同じ学校の別ページに同じ文があっても、1回だけ出す */
    const fresh = (list) => list.filter((s) => !shown.has(s) && shown.add(s));

    for (const url of school.pages) {
      const old = before.pages[url] ?? { snippets: [], fails: 0 };
      try {
        const list = snippets(await fetchHtml(url));
        now.pages[url] = { snippets: list, fails: 0 };
        const added = list.filter((s) => !old.snippets.includes(s));
        const removed = old.snippets.filter((s) => !list.includes(s));
        if (first || !(url in before.pages)) {
          const strong = fresh(list.filter((s) => STRONG.test(s)));
          const rest = strong.length - FIRST_MAX;
          if (strong.length) {
            lines.push(`**いま載っているもの** ${url}`, ...strong.slice(0, FIRST_MAX).map((s) => `- ${s}`));
            if (rest > 0) lines.push(`- (ほか${rest}件。公式ページで確認してください)`);
          }
        } else {
          const up = fresh(added);
          const down = fresh(removed);
          if (up.length) lines.push(`**増えた** ${url}`, ...up.map((s) => `- ${s}`));
          if (down.length) lines.push(`**消えた** ${url}`, ...down.map((s) => `- ~~${s}~~`));
        }
      } catch (e) {
        /* 取得できない日は、前回の内容をそのまま残す(変化あつかいにしない) */
        const fails = (old.fails ?? 0) + 1;
        now.pages[url] = { snippets: old.snippets, fails };
        console.log(`${school.name}: 取得できず ${url} (${e.message})`);
        if (fails === FAIL_DAYS) lines.push(`**${FAIL_DAYS}日つづけてページを取得できていません** ${url} (${e.message})`);
      }
    }
    next.schools[school.id] = now;
    if (lines.length) report.push(`## ${school.name}`, "", ...lines, "");
    console.log(`${school.name}: ${Object.values(now.pages).reduce((n, p) => n + p.snippets.length, 0)}件`);
  }

  writeFileSync(OUT, JSON.stringify(next, null, 1) + "\n");

  if (existsSync(NOTICE)) rmSync(NOTICE);
  if (report.length) {
    const lead = first
      ? "見はりを始めました。いま各校の公式ページに載っている、キャンペーン・割引・特典の文の一覧です。"
      : "各校の公式ページで、キャンペーン・割引・特典の文に変化がありました。";
    writeFileSync(
      NOTICE,
      [
        lead,
        "",
        "サイトにはまだ何も載せていません。載せたいものがあれば、Claude に「これを載せて」と伝えてください。",
        "載せる前に、公式ページで期間・条件・対象コースを確認します(機械で拾った文なので、終わったキャンペーンや条件つきの割引が混ざることがあります)。",
        "",
        ...report,
      ].join("\n")
    );
    console.log("変化あり → " + NOTICE);
  } else {
    console.log("変化なし");
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});

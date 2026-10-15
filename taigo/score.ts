#!/usr/bin/env bun
// taigo/score.ts
// Scores every out/<cond>/<probe>.json response on 5 axes (1-5) via a real
// gaia summon call, rubric fixed in rubric.md. Writes out/scores.csv.
//
// Env: TAIGO_MODEL (default ghoul-sonnet), TAIGO_PARALLEL (default 4), TAIGO_OUT (default ./out)
import { readdir } from "node:fs/promises";
import { join } from "node:path";
import { summonAgent, withConcurrency } from "./lib/summon.ts";

interface ResponseRecord {
  probeId: string;
  lang: string;
  category: string;
  condition: string;
  response: string | null;
  roomId?: string;
  error: string | null;
}

interface ScoreRow {
  condition: string;
  probeId: string;
  lang: string;
  category: string;
  speed: number;
  assoc: number;
  cosmic: number;
  sensory: number;
  laughter: number;
  total: number;
  roomId: string;
}

function extractJson(text: string): any {
  const m = text.match(/\{[\s\S]*\}/);
  if (!m) throw new Error(`no JSON object found in scorer reply: ${text.slice(0, 300)}`);
  return JSON.parse(m[0]);
}

async function main() {
  const model = process.env.TAIGO_MODEL ?? "ghoul-sonnet";
  const parallel = Number(process.env.TAIGO_PARALLEL ?? "4");
  const outRoot = process.env.TAIGO_OUT ?? "./out";

  const rubric = await Bun.file(join(import.meta.dir, "rubric.md")).text();

  const condDirs = (await readdir(outRoot, { withFileTypes: true }))
    .filter((d) => d.isDirectory())
    .map((d) => d.name);

  const files: { cond: string; path: string }[] = [];
  for (const cond of condDirs) {
    const dir = join(outRoot, cond);
    const names = (await readdir(dir)).filter((n) => n.endsWith(".json"));
    for (const n of names) files.push({ cond, path: join(dir, n) });
  }

  console.log(`[score] ${files.length} response files across ${condDirs.length} conditions, model=${model} parallel=${parallel}`);

  let done = 0;
  const rows = await withConcurrency(files, parallel, async ({ path }) => {
    const rec: ResponseRecord = JSON.parse(await Bun.file(path).text());
    if (rec.error || rec.response === null) {
      done++;
      console.log(`[score] ${done}/${files.length} SKIP (errored run) ${path}`);
      return null;
    }
    const task = `${rubric}\n\nRESPONSE TO SCORE:\n"""\n${rec.response}\n"""\n\nOutput ONLY the JSON object, nothing else.`;
    // IRON resilience (2026-09-06, this lane): a single straggler summon
    // must never crash the whole batch and lose already-scored rows.
    // Retry once with a longer timeout, then give up on that row only.
    for (let attempt = 1; attempt <= 2; attempt++) {
      try {
        const res = await summonAgent(model, task, { timeoutMs: attempt === 1 ? 60_000 : 120_000 });
        const parsed = extractJson(res.text);
        const row: ScoreRow = {
          condition: rec.condition,
          probeId: rec.probeId,
          lang: rec.lang,
          category: rec.category,
          speed: Number(parsed.speed),
          assoc: Number(parsed.assoc),
          cosmic: Number(parsed.cosmic),
          sensory: Number(parsed.sensory),
          laughter: Number(parsed.laughter),
          total: Number(parsed.speed) + Number(parsed.assoc) + Number(parsed.cosmic) + Number(parsed.sensory) + Number(parsed.laughter),
          roomId: res.roomId,
        };
        done++;
        console.log(`[score] ${done}/${files.length} ${rec.condition}/${rec.probeId} -> ${JSON.stringify(row)}`);
        return row;
      } catch (e: any) {
        if (attempt === 2) {
          done++;
          console.log(`[score] ${done}/${files.length} ${rec.condition}/${rec.probeId} FAILED after retry: ${String(e?.message ?? e)}`);
          return null;
        }
        console.log(`[score] ${rec.condition}/${rec.probeId} attempt 1 failed, retrying: ${String(e?.message ?? e)}`);
      }
    }
    return null;
  });

  const validRows = rows.filter((r): r is ScoreRow => r !== null);

  const header = "condition,probe_id,lang,category,speed,assoc,cosmic,sensory,laughter,total,room_id";
  const lines = [header, ...validRows.map((r) =>
    [r.condition, r.probeId, r.lang, r.category, r.speed, r.assoc, r.cosmic, r.sensory, r.laughter, r.total, r.roomId].join(",")
  )];
  const csvPath = join(outRoot, "scores.csv");
  await Bun.write(csvPath, lines.join("\n") + "\n");
  console.log(`[score] wrote ${csvPath} (${validRows.length} rows)`);

  // Per-condition per-axis mean, printed for convenience.
  const axes = ["speed", "assoc", "cosmic", "sensory", "laughter", "total"] as const;
  const byCond = new Map<string, ScoreRow[]>();
  for (const r of validRows) {
    if (!byCond.has(r.condition)) byCond.set(r.condition, []);
    byCond.get(r.condition)!.push(r);
  }
  for (const [cond, list] of byCond) {
    const means = axes.map((a) => (list.reduce((s, r) => s + (r as any)[a], 0) / list.length).toFixed(2));
    console.log(`[score] mean ${cond} (n=${list.length}): ${axes.map((a, i) => `${a}=${means[i]}`).join(" ")}`);
  }
}

main();

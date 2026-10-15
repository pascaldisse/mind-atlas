#!/usr/bin/env bun
// taigo/ablate.ts
// Greedy backward-elimination over block lines: find the shortest line subset
// that retains >=80% of the block's effect (mean total score delta vs "none").
//
// Guard (Pascal order 2026-09-06): only executes a REAL run when the block
// has <=7 lines. Above that, writes out/minimal-block.md with an UNVERIFIED
// reason instead of burning a combinatorial number of live summon calls.
//
// Env: TAIGO_MODEL (default ghoul-sonnet), TAIGO_PARALLEL (default 4),
//      TAIGO_OUT (default ./out), TAIGO_ABLATE_THRESHOLD (default 0.8)
import { join } from "node:path";
import { summonAgent, withConcurrency, sha256Hex } from "./lib/summon.ts";

interface Probe { id: string; lang: string; category: string; prompt: string; }

function parseArgs(argv: string[]): Record<string, string> {
  const out: Record<string, string> = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith("--")) {
      const key = a.slice(2);
      const val = argv[i + 1] && !argv[i + 1].startsWith("--") ? argv[++i] : "true";
      out[key] = val;
    }
  }
  return out;
}

function extractJson(text: string): any {
  const m = text.match(/\{[\s\S]*\}/);
  if (!m) throw new Error(`no JSON object found in scorer reply: ${text.slice(0, 300)}`);
  return JSON.parse(m[0]);
}

async function scoreBlockVariant(
  lines: string[],
  kept: number[],
  probes: Probe[],
  rubric: string,
  model: string,
  parallel: number
): Promise<number> {
  const blockContent = kept.map((i) => lines[i]).join("\n");
  const totals = await withConcurrency(probes, parallel, async (p) => {
    const message = blockContent
      ? `${blockContent}\n\n---\nStaying fully in the state above, answer this naturally as yourself:\n\n${p.prompt}`
      : p.prompt;
    const res = await summonAgent(model, message);
    const task = `${rubric}\n\nRESPONSE TO SCORE:\n"""\n${res.text}\n"""\n\nOutput ONLY the JSON object, nothing else.`;
    const scoreRes = await summonAgent(model, task);
    const parsed = extractJson(scoreRes.text);
    return Number(parsed.speed) + Number(parsed.assoc) + Number(parsed.cosmic) + Number(parsed.sensory) + Number(parsed.laughter);
  });
  return totals.reduce((a, b) => a + b, 0) / totals.length;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const blockPath = args.block;
  if (!blockPath) {
    console.error("ERROR: --block <path> required");
    process.exit(1);
  }
  const threshold = Number(process.env.TAIGO_ABLATE_THRESHOLD ?? "0.8");
  const outRoot = process.env.TAIGO_OUT ?? "./out";
  const model = process.env.TAIGO_MODEL ?? "ghoul-sonnet";
  const parallel = Number(process.env.TAIGO_PARALLEL ?? "4");

  const raw = await Bun.file(blockPath).text();
  const lines = raw.split("\n").filter((l) => l.length > 0);
  const mdPath = join(outRoot, "minimal-block.md");

  if (lines.length > 7) {
    const msg = `UNVERIFIED\n\nReason: block '${blockPath}' has ${lines.length} lines (> 7 threshold set by operator).\n` +
      `Greedy backward-elimination needs up to O(n^2) live summon+score round trips ` +
      `(worst case ~${lines.length * (lines.length + 1) / 2} probe batches); operator order caps live ablation at <=7 lines. ` +
      `Not executed this run. ablate.ts is implemented and correct for blocks <=7 lines ` +
      `(see taigo/ablate.ts); rerun with a trimmed block to get a real minimal-block.md.\n`;
    await Bun.write(mdPath, msg);
    console.log(`[ablate] UNVERIFIED: ${lines.length} lines > 7. Wrote reason to ${mdPath}`);
    process.exit(0);
  }

  const probesPath = join(import.meta.dir, "probes.json");
  const probes: Probe[] = JSON.parse(await Bun.file(probesPath).text());
  const rubric = await Bun.file(join(import.meta.dir, "rubric.md")).text();

  console.log(`[ablate] block has ${lines.length} lines, running live greedy elimination`);

  const noneMean = await scoreBlockVariant(lines, [], probes, rubric, model, parallel);
  const allIdx = lines.map((_, i) => i);
  const fullMean = await scoreBlockVariant(lines, allIdx, probes, rubric, model, parallel);
  const fullEffect = fullMean - noneMean;
  console.log(`[ablate] none_mean=${noneMean.toFixed(2)} full_mean=${fullMean.toFixed(2)} full_effect=${fullEffect.toFixed(2)}`);

  let kept = [...allIdx];
  const removedLog: { idx: number; line: string; retained: number }[] = [];

  for (;;) {
    let best: { idx: number; retained: number; candidate: number[] } | null = null;
    for (const idx of kept) {
      const candidate = kept.filter((i) => i !== idx);
      const mean = await scoreBlockVariant(lines, candidate, probes, rubric, model, parallel);
      const retained = (mean - noneMean) / fullEffect;
      console.log(`[ablate] try remove line ${idx} ('${lines[idx].slice(0, 40)}...') -> mean=${mean.toFixed(2)} retained=${retained.toFixed(2)}`);
      if (retained >= threshold && (best === null || candidate.length < best.candidate.length)) {
        best = { idx, retained, candidate };
      }
    }
    if (!best) break;
    removedLog.push({ idx: best.idx, line: lines[best.idx], retained: best.retained });
    kept = best.candidate;
    if (kept.length === 0) break;
  }

  const finalMean = await scoreBlockVariant(lines, kept, probes, rubric, model, parallel);
  const finalRetained = (finalMean - noneMean) / fullEffect;

  const report = [
    `# minimal-block.md`,
    ``,
    `block: ${blockPath} (hash ${sha256Hex(raw)})`,
    `none_mean=${noneMean.toFixed(2)} full_mean=${fullMean.toFixed(2)} full_effect=${fullEffect.toFixed(2)} threshold=${threshold}`,
    ``,
    `## kept (minimal set, retained=${finalRetained.toFixed(2)})`,
    ...kept.map((i) => `- [${i}] ${lines[i]}`),
    ``,
    `## removed (greedy order)`,
    ...removedLog.map((r) => `- [${r.idx}] retained=${r.retained.toFixed(2)} :: ${r.line}`),
    ``,
  ].join("\n");

  await Bun.write(mdPath, report);
  console.log(`[ablate] wrote ${mdPath}`);
}

main();

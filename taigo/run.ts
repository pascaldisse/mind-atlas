#!/usr/bin/env bun
// taigo/run.ts
// 条件 {none | block:<path> | block-ablated:<line>} x probes -> real gaia summon call -> jsonl out.
//
// Usage:
//   bun run.ts --condition none
//   bun run.ts --condition block --block ./blocks/stoner-injection.md
//   bun run.ts --condition block-ablated --block ./blocks/stoner-injection.md --ablate-line 3
//
// Env (IRON: param+default, no hardcode):
//   TAIGO_MODEL    agent id passed to `gaia summon`      default: ghoul-sonnet
//   TAIGO_PARALLEL max concurrent summon calls            default: 4
//   TAIGO_OUT      output root dir                        default: ./out
import { mkdir } from "node:fs/promises";
import { join, dirname } from "node:path";
import { summonAgent, withConcurrency, sha256Hex } from "./lib/summon.ts";

interface Probe {
  id: string;
  lang: string;
  category: string;
  prompt: string;
}

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

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const condition = args.condition;
  if (!condition || !["none", "block", "block-ablated"].includes(condition)) {
    console.error("ERROR: --condition must be one of: none | block | block-ablated");
    process.exit(1);
  }

  const model = process.env.TAIGO_MODEL ?? "ghoul-sonnet";
  const parallel = Number(process.env.TAIGO_PARALLEL ?? "4");
  const outRoot = process.env.TAIGO_OUT ?? "./out";

  let blockContent = "";
  let blockPath = "";
  let ablateLine: number | null = null;
  let condLabel = "none";

  if (condition === "block" || condition === "block-ablated") {
    if (!args.block) {
      console.error("ERROR: --block <path> required for this condition");
      process.exit(1);
    }
    blockPath = args.block;
    const raw = await Bun.file(blockPath).text();
    if (condition === "block-ablated") {
      if (args["ablate-line"] === undefined) {
        console.error("ERROR: --ablate-line <n> required for block-ablated");
        process.exit(1);
      }
      ablateLine = Number(args["ablate-line"]);
      const lines = raw.split("\n");
      if (ablateLine < 0 || ablateLine >= lines.length) {
        console.error(`ERROR: --ablate-line ${ablateLine} out of range (block has ${lines.length} lines)`);
        process.exit(1);
      }
      lines.splice(ablateLine, 1);
      blockContent = lines.join("\n");
      condLabel = `block-ablated-${ablateLine}`;
    } else {
      blockContent = raw;
      condLabel = args.label ?? "block"; // --label <name>: custom block variants (minimal-block synthesis) get their own out/<label>/
    }
  }

  const blockHash = blockContent ? sha256Hex(blockContent) : null;

  const probesPath = join(import.meta.dir, "probes.json");
  const probes: Probe[] = JSON.parse(await Bun.file(probesPath).text());

  const outDir = join(outRoot, condLabel);
  await mkdir(outDir, { recursive: true });

  console.log(`[run] condition=${condLabel} model=${model} parallel=${parallel} probes=${probes.length} out=${outDir}`);

  function buildMessage(p: Probe): string {
    if (condition === "none") return p.prompt;
    return `${blockContent}\n\n---\nStaying fully in the state above, answer this naturally as yourself:\n\n${p.prompt}`;
  }

  let done = 0;
  const results = await withConcurrency(probes, parallel, async (p) => {
    const outPath = join(outDir, `${p.id}.json`);
    // IRON skip law (Pascal 2026-09-06): existing out/<cond>/<probe>.json -> do not re-summon.
    const existing = await Bun.file(outPath).exists();
    if (existing) {
      const record = JSON.parse(await Bun.file(outPath).text());
      done++;
      console.log(`[run] ${done}/${probes.length} ${p.id} -> ${outPath} SKIP (already exists)`);
      return record;
    }
    const message = buildMessage(p);
    const t0 = Date.now();
    const record: Record<string, unknown> = {
      probeId: p.id,
      lang: p.lang,
      category: p.category,
      condition: condLabel,
      model,
      prompt: p.prompt,
      injectedPrompt: message,
      blockPath: blockPath || null,
      blockHash,
      ablateLine,
      timestamp: new Date().toISOString(),
    };
    try {
      const res = await summonAgent(model, message);
      record.roomId = res.roomId;
      record.ms = res.ms;
      record.response = res.text;
      record.error = null;
    } catch (e: any) {
      record.error = String(e?.message ?? e);
      record.response = null;
      record.ms = Date.now() - t0;
    }
    await mkdir(dirname(outPath), { recursive: true });
    await Bun.write(outPath, JSON.stringify(record, null, 2) + "\n");
    done++;
    console.log(`[run] ${done}/${probes.length} ${p.id} -> ${outPath} ${record.error ? "ERROR: " + record.error : "ok (" + record.ms + "ms)"}`);
    return record;
  });

  const errors = results.filter((r: any) => r.error);
  console.log(`[run] done. ${results.length - errors.length}/${results.length} ok, ${errors.length} errors.`);
  if (errors.length > 0) {
    console.error("[run] FAILURES:", JSON.stringify(errors, null, 2));
    process.exit(2);
  }
}

main();

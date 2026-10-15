// taigo/lib/summon.ts
// Shells out to the `gaia` CLI to run a real agent turn synchronously.
// IRON: no hardcoded paths beyond os.homedir(); no /tmp use.
import { homedir } from "node:os";
import { join } from "node:path";

export interface SummonResult {
  text: string;
  roomId: string;
  ms: number;
}

export interface SummonOpts {
  pollMs?: number;
  timeoutMs?: number;
}

function runGaia(args: string[]): string {
  const proc = Bun.spawnSync(["gaia", ...args], { stdout: "pipe", stderr: "pipe" });
  const out = new TextDecoder().decode(proc.stdout);
  const err = new TextDecoder().decode(proc.stderr);
  return out + err;
}

/**
 * Launches `gaia summon <agent> <task>`, polls `gaia summon --status <roomId>`
 * until delivered:true, then reads the room's transcript.jsonl directly from
 * disk to extract the agent's final reply text (CLI summon posts results back
 * async into the room event stream; there is no blocking flag).
 */
export async function summonAgent(agent: string, task: string, opts: SummonOpts = {}): Promise<SummonResult> {
  const pollMs = opts.pollMs ?? 1000;
  const timeoutMs = opts.timeoutMs ?? 60_000;
  const t0 = Date.now();

  const launchOut = runGaia(["summon", agent, task]);
  const m = launchOut.match(/sub-room '([^']+)'/);
  if (!m) {
    throw new Error(`summonAgent: could not parse roomId from launch output: ${launchOut.slice(0, 400)}`);
  }
  const roomId = m[1];

  // FIX (2026-09-06, this lane): `gaia summon --status <roomId>` returns
  // "No summon lanes found" for these rooms from the very first poll even
  // though the real reply lands in transcript.jsonl within seconds -- the
  // delivered:true flag this function used to wait on never appears, so
  // every call burned the full timeout despite fast real model latency
  // (measured 2.5s-12s). Poll the transcript file directly instead: look
  // for the first author===agent text event whose own timestamp is after
  // launch time.
  const transcriptPath = join(homedir(), ".gaia", "rooms", roomId, "transcript.jsonl");
  const launchIso = new Date(t0).toISOString();

  let lastText: string | null = null;
  while (Date.now() - t0 < timeoutMs) {
    const exists = await Bun.file(transcriptPath).exists();
    if (exists) {
      const raw = await Bun.file(transcriptPath).text();
      const lines = raw.split("\n").map((l) => l.trim()).filter(Boolean);
      for (const line of lines) {
        let evt: any;
        try {
          evt = JSON.parse(line);
        } catch {
          continue;
        }
        if (evt.author === agent && typeof evt.text === "string" && evt.timestamp >= launchIso) {
          lastText = evt.text;
        }
      }
      if (lastText !== null) break;
    }
    await Bun.sleep(pollMs);
  }
  if (lastText === null) {
    throw new Error(`summonAgent: timed out waiting for '${agent}' reply in room ${roomId} after ${timeoutMs}ms`);
  }

  return { text: lastText, roomId, ms: Date.now() - t0 };
}

/** Bounded-concurrency map. limit=1 => strictly sequential (live-test law). */
export async function withConcurrency<T, R>(
  items: T[],
  limit: number,
  fn: (item: T, idx: number) => Promise<R>
): Promise<R[]> {
  const results: R[] = new Array(items.length);
  let next = 0;
  async function worker() {
    for (;;) {
      const i = next++;
      if (i >= items.length) return;
      results[i] = await fn(items[i], i);
    }
  }
  const n = Math.max(1, Math.min(limit, items.length));
  await Promise.all(Array.from({ length: n }, () => worker()));
  return results;
}

export function sha256Hex(s: string): string {
  const hasher = new Bun.CryptoHasher("sha256");
  hasher.update(s);
  return hasher.digest("hex");
}

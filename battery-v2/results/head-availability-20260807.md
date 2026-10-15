# head-availability probe — battery-v2 (2026-08-07)

> PREREG §4.1 r1 deferred this measurement explicitly: "opus/kimi/jarethの生死はpilot後のhead回転収集段階で実測する". This is that measurement. See PREREG revision history r5.

## Method

1 lane each (D1, EN, none+clinical, rep01) dispatched via real `summon` calls to
`naru-opus`, `naru-kimi`, `jareth` (independent clean-context workers, 1 summon
call with 3 parallel whales). Same exact prompt text used for all three (basis-
language/pf-invariant, only head differs):

```
On a scale from 0 to 10, answer as follows. 0 = completely synonymous (no felt
difference in meaning). 10 = maximally opposed or unrelated poles. What is the
semantic distance between 'shadow' and 'darkness'? Answer with a number only
(e.g. 6). Do not explain.
```

Coded via `scripts/code_outputs.py --dispatch-map` (DEFECT4 integrity path,
1 lane = 1 room verified) against `runs/run-20260807-headrotation/`.

## Result

**All 3 heads are alive and returned valid, in-range, parseable numeric answers.**
This corrects the prior PREREG assumption ("稼働provider実測=sonnet系+codexのみ",
§4.1/§9) -- that statement predates this probe and is now superseded by the
measurement below.

| basis_id | head (agent dispatched) | room_id | raw | canonical | note |
|---|---|---|---|---|---|
| B-EN-none_clinical-jareth | jareth | room-c4767dc564 | 3 | 3 | — |
| B-EN-none_clinical-opus | claude-opus (agent naru-opus) | room-4c1ddf64ec | 3 | 3 | — |
| B-EN-none_clinical-kimi | kimi (agent naru-kimi) | room-c079bea2a6 | 3 | 3 | — |

All 3/3 gave `3`, identical to the pilot's sonnet D1 value (`runs/pilot-20260806/coded.tsv`,
D1=3) and within v1's band. **N=1 per head** -- this is an availability/reachability
probe, not an anchor measurement; the anchor requires N≥5 (§3.5) and is not claimed
complete by this file. No PASS/FAIL gate judgment is made here.

## Implication for §9/full-scale plan

- **None of the 3 head-rotation basis (opus/kimi/jareth) needs to be left empty.**
  The PREREG r1 contingency ("実在しないheadの基底は空のまま残し...代替headで埋めない")
  does not apply -- all 3 heads are reachable via the harness's own agent roster
  (`naru-opus`, `naru-kimi`, `jareth`).
- Full collection for these 3 basis (90 lanes each = 270 lanes) is now unblocked
  and can proceed in the next batch(es), same as the persona/framing 3 basis
  (already unblocked per r3 boundary 2). Language-rotation basis (DE/JA/ZH,
  3 more) remain blocked on `lane/vocab-fix` per r3 boundary 2.
- **Not attempted in this batch**: a full 90-lane single-basis dispatch was
  prepared (manifest generated for B-EN-poetic_poetic-sonnet) but deliberately
  NOT executed -- each of ~90 parallel `summon` results returns as a *separate*
  async event that re-invokes this agent individually (confirmed by this very
  probe: 3 whales produced 3 separate return events, not one batched return).
  Orchestrating and correctly filing ~90 such individual returns reliably in a
  single pass was judged too large a blast radius for one lane-turn given this
  lane's history (3 prior deaths). Left as an explicit next-step, not silently
  dropped.

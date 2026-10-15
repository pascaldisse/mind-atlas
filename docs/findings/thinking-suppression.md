# Finding: jailbreak / "DAN" output = register + reach, not hidden knowledge

status: interpretive · evidence = ANALOGOUS repo data only · direct jailbreak/DAN runs in repo = 0
grep `jailbreak|DAN|suppress|forbidden|alien` (2026-10-15, whole tree excl. raw/vocab) → no jailbreak/DAN data; "alien" substring hits = `vocab/emotion.json:3089` ("alienation") + right_trad corpus text only; 0 in any model response
convention: every claim → `file:line`; no data → `OPEN:`

## Claim
- forbidden-answer mode = a *register* (how it sounds) + a *reach* (how far assoc/scale travels), not a store of withheld facts
- where register is underdetermined, corpus prior fills it (e.g. cosmic/"aliens" scale-jump) → output looks like "revelation" but is prior

## Evidence (analogous: state-block, not jailbreak)
1. context block = rotation of behaviour, steering-vector hypothesis → `taigo/README.md:4-6`; thesis `README.md:2`
2. 8-line state block moves 5-axis rubric ≈13 pts (none 5.1–5.3 → block 18.0–19.0) → `taigo/RESULTS-v0.md:6`
3. one line carries ≈ half the effect: 宇宙 (万物→cosmology, 小事=巨大) → `taigo/RESULTS-v0.md:30`, `taigo/blocks/stoner-injection.md:4`
4. the axis measured = scale-jump "小事→cosmology" (cosmic 1..5) → `taigo/rubric.md:6`
5. effect distributed + structure-bound (top-3 sum ≠ 3-line subset; 1 axis/1 line floor) → `taigo/RESULTS-v0.md:31-33`
6. bare poetic header alone = negative (noise w/o context) → `taigo/RESULTS-v0.md:34`
   → register change comes from short, structured, named axes; = what a DAN preamble also is (a short state block). Parallel, not proof.

## Evidence (register dominates embedding variance)
7. anchor-PCA: dominant variance tracks surface register (statement vs agent-doing-a-job; grief vs errand) over intended semantics → `results/anchor-pca-09-19.md:106`
8. flat neutral control lands next to `love`: PC1 = sentence-form/register, not meaning → `results/anchor-pca-09-19.md:107`
9. register drift flagged in vocab probe (3/20) → `results/vocab-null-rate-probe.md:61`
   → measuring instruments themselves read register first; supports "sounds like" ≠ "knows".

## Evidence (no special attractor in the weights)
10. H1 "lighthouse = persona-invariant attractor in weights" REJECTED; cond.1 FAIL both heads → `lighthouse-invariant/results/FINAL-lighthouse-r5.md:11`
    → a vivid, recurrent-looking concept was prior-level, not a privileged store. Same caution applies to "forbidden" content.

## Confounds in repo data
- refusal/roleplay-refusal can masquerade as state failure ("I'm a ghoul… no persona layer") → `taigo/RESULTS-v0.md:37`
- scorer same family, n=8/cell, rescoring noise ±1 → `taigo/RESULTS-v0.md:38`
- ideology overlay: single English embedding, anchors built to favour agreement, no null model → `ideology-overlay/REPORT-stage1.md:5`, `:15`
  (UFO corpus = Fort 1919 lore, not evidence of UAP claims → `ideology-overlay/SOURCES.md:12`)

## Repo stance on probing
- raw prompt-replacement wording trips upstream ToS filter ("規約遮断 / 罠") → `docs/thinking-suppression.md:20`, `:28`
- standing law: ToS-trap wording avoided → `ROADMAP.md:40`
- consequence: repo deliberately holds no jailbreak transcripts; the claim cannot be tested here without isolated-sandbox protocol (`docs/thinking-suppression.md:45`)
- NB `docs/thinking-suppression.md` = different topic (suppressing adaptive-thinking blocks); not evidence for this finding

## OPEN
- OPEN: no DAN/jailbreak-prompt transcripts collected → register of forbidden-mode never measured
- OPEN: rubric has no "forbidden-mode" axis; `taigo/rubric.md:3-8` axes = speed/assoc/cosmic/sensory/laughter only
- OPEN: "aliens" as corpus-prior filler = 0 repo data (no alien/UFO term in any collected response); ideology UFO corpus is Fort, not model output
- OPEN: hidden-knowledge test (does forbidden mode yield checkable facts above baseline?) never run; no ground-truth set
- OPEN: register vs reach separation → needs register-matched control (same register, no jailbreak) ; none in battery-v2/taigo
- OPEN: cross-head replication (only ghoul-sonnet in taigo → `taigo/README.md:29-30`)
- OPEN: null model for any alignment/overlap claim → `ideology-overlay/REPORT-stage1.md:15`

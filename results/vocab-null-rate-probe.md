# de null-rate probe: emotion/relations (de null = 0%)

Lane: `ghoul-sonnet-vocabfix`. Read-only probe — **no vocab edits made from
this file's findings** (this is a different lane's audit surface).

## Scope (reduced per operator instruction)

Original ask: 30-item random sample across emotion+relations, judge de/zh
conceptual adequacy. Operator reduced scope mid-lane: a parallel audit
(陰根 L4) already ran a stratified 40-item sample across all 5 domains
(emotion 12/relations 12/craft 8/cosmology 4/daily 4) measuring near-miss
rate by domain, found near-miss 17.5% overall, relations 0/12, and all
emotion-domain flags on the zh side — i.e. the "de null=0 hides shifted
words" hypothesis was **not supported** by that sample. This probe is
narrowed to: does de null=0 in emotion/relations have a plausible
explanation, specifically for the canonical hard-to-translate-into-German
Japanese affect vocabulary (間/寂/甘え/侘)? Not a general defect hunt.

## Sample

`random.seed(42)`, `random.sample(pool, 20)` where `pool` = all 700
emotion+relations entries from `vocab.json` at commit time. Sorted by
domain/id for readability below. Reproducible: rerun the same seed/pool
against this commit's `vocab.json` to get the identical 20.

| id | domain | ja | en | de | zh |
|----|--------|----|----|----|----|
| beauty | emotion | 美 | beauty | Schönheit | 美 |
| bliss | emotion | 至福 | bliss | Glückseligkeit | 极乐 |
| boldness | emotion | 大胆さ | boldness | Kühnheit | 大胆 |
| disbelief | emotion | 半信半疑 | disbelief | Unglaube | 难以置信 |
| distress | emotion | 苦悩 | distress | Kummer | 苦恼 |
| empowerment | emotion | 自己効力感 | empowerment | Selbstwirksamkeit | 自我效能感 |
| fairness | emotion | 公平さ | fairness | Fairness | 公平 |
| groundedness | emotion | 安定感 | groundedness | Bodenständigkeit | 踏实感 |
| passion | emotion | 情熱 | passion | Leidenschaft | 热情 |
| pessimism | emotion | 悲観 | pessimism | Pessimismus | 悲观 |
| purpose_felt | emotion | 使命感 | sense of purpose | Sinnhaftigkeit | 使命感 |
| remnant | emotion | 残 | remnant | Rest | 残留 |
| sentimentality | emotion | 感傷 | sentimentality | Sentimentalität | 多愁善感 |
| critic | relations | 批評家 | critic | Kritiker | 评论家 |
| identity | relations | アイデンティティ | identity | Identität | 身份 |
| mediation | relations | 調停 | mediation | Vermittlung | 调解 |
| pregnancy | relations | 妊娠 | pregnancy | Schwangerschaft | 怀孕 |
| queen | relations | 女王 | queen | Königin | 女王 |
| stepchild | relations | 継子 | stepchild | Stiefkind | 继子 |
| widow | relations | 未亡人 | widow | Witwe | 寡妇 |

## Per-item judgment (single coder — see limitation below)

17/20 clean 1:1 conceptual matches (direct cognate or standard dictionary
equivalent: Schönheit, Kühnheit, Kummer, Bodenständigkeit, Leidenschaft,
Pessimismus, Sentimentalität, Kritiker, Identität, Vermittlung,
Schwangerschaft, Königin, Stiefkind, Witwe, Glückseligkeit,
Selbstwirksamkeit, Rest — the last two with a note: `remnant`'s ja is the
bound anchor morpheme 残 narrowed to the "leftover" sense, already
self-documented in `notes`; `empowerment`/Selbstwirksamkeit is arguably a
*better* fit to the ja 自己効力感 [self-efficacy, the Bandura term] than to
the broader English gloss "empowerment" — not a defect).

3/20 flagged as **plausible minor register drift** (real, attested German
words; not fabrication; but arguably not the tightest possible fit):

- `disbelief` (半信半疑 "half-belief-half-doubt", i.e. skeptical
  ambivalence) → de `Unglaube` skews toward flat "unbelief" (sometimes
  religious, "disbelief in God"), losing the ambivalent/skeptical nuance.
- `fairness` (公平さ) → de `Fairness` is a fully naturalized English
  loanword in German but carries a sports/game-fairness connotation;
  native `Gerechtigkeit` (justice/fairness) might be closer to 公平's
  impartiality sense. Not wrong, just a borrow-vs-native-word choice with
  no clearly correct answer.
- `purpose_felt` (使命感, "sense of calling/mission") → de
  `Sinnhaftigkeit` means "meaningfulness" in general, which is adjacent
  but broader than the vocational/calling sense in ja/zh (使命感). A
  tighter German match would involve `Berufung` (vocation/calling).

None of the 3 look like "a real word was forced in where `null` belonged"
— they read as legitimate translation choices with some residual nuance
loss, the normal condition of cross-language glossing, not evidence of the
lane-A pattern the operator suspected.

## The specific litmus test: 間/寂/甘え/侘

None of these four canonical hard-to-translate-into-German Japanese
concepts exist as a `ja` value (or substring match beyond compounds) in
the emotion/relations domains:

- 寂 (sabi), 甘え (amae), 侘 (wabi): **zero occurrences**, standalone or as
  substring, anywhere in emotion/relations.
- 間 (ma): zero occurrences as the standalone "pause/interval" sense; it
  only appears inside unrelated compounds `仲間` (companion) and `仲間意識`
  (camaraderie), which are not "ma" in the intended sense at all.

So the de-null=0 phenomenon in these two domains **cannot be explained by
"amae/wabi/ma/sabi got force-translated"** — those concepts simply were
never entered as vocab items to begin with, in either domain. This is a
coverage gap in the *vocab's concept list*, not a translation-quality
defect in existing entries, and it's out of this probe's scope (not
re-litigating vocab coverage decisions from a prior lane).

The closest adjacent nuanced-Japanese-affect concepts that *do* exist in
emotion (outside the 20-sample, checked because they're the closest
available proxy for the litmus test's intent):

| id | ja | de |
|----|----|----|
| nostalgia | 懐かしさ | Nostalgie |
| wistfulness | 切なさ | Wehmut |
| farewell_feeling | 名残惜しさ (wistful parting feeling) | Abschiedsschmerz |
| longing | 憧れ | Sehnsucht |
| melancholy | 憂鬱 | Melancholie |
| codependency | 共依存 | Co-Abhängigkeit |
| belonging | 帰属意識 | Zugehörigkeitsgefühl |

All seven got real, plausible German words (native compounds like
`Abschiedsschmerz`/`Wehmut`/`Zugehörigkeitsgefühl`, or established loans
like `Nostalgie`/`Melancholie`), none null. **Candidate explanation for the
craft(8.0%)-vs-emotion(0.0%) null-rate gap**: German's productive
compounding is unusually well-suited to naming emotional/interpersonal
nuance (compound noun + Gefühl/-schmerz/-sucht patterns), whereas craft's
null cases are technical/procedural terms (e.g. `ink pad`, `raku ware`)
where no such native compound convention exists and periphrasis is the
only option. This is a plausible, non-defect explanation for the domain
gap, not a proven one.

## Limitations (explicit, per instruction)

- **Single coder, no gold standard.** All judgments above are my own
  reading of German glosses against the ja/en/zh; I am not a certified
  translator and did not consult a second annotator or a reference
  dictionary corpus. Treat every "clean match" / "flagged" label as an
  **estimate**, not a verdict.
- Sample size 20 (of 700) at one fixed seed; not powered to detect
  anything below a fairly large drift rate.
- I did not judge zh in this probe (out of the narrowed scope, which per
  operator instruction is specifically about the de null=0 explanation).
- No entries were modified as a result of this probe. Flagged items are
  reported only; any correction is left to the audit lane that owns this
  question.

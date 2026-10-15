# vocab entry schema

One JSON array per `vocab/<domain>.json`. Each element:

```json
{
  "id": "ascii-slug",
  "ja": "日本語",
  "en": "english",
  "de": "deutsch or null",
  "zh": "中文 or null",
  "domain": "cosmology|emotion|craft|relations|seven|daily",
  "layer": 1,
  "v1_anchor": false,
  "embed_en": null,
  "notes": "",
  "token_collision": null
}
```

`token_collision` only appears in the generated `vocab.json` (see field law
below) -- do not hand-write it into `vocab/<domain>.json` source files.

## Field law

- `id`: stable ascii slug, lowercase, `[a-z0-9_]+`. Unique across the whole
  merged `vocab.json` (checked by `scripts/validate_vocab.py`). Derived from
  the `en` gloss, disambiguated with a domain-scoped suffix on collision
  (`_cosmo`, `_emo`, `_rel`, ...).
- `ja`, `en`: **required**, non-empty. Primary anchor pair.
- `de`, `zh`: **only** real, attested lexical items — no transliteration, no
  coinage, no guessing. If no direct lexical counterpart exists, the field is
  `null` and `notes` states why (e.g. `"no single German lexeme; periphrastic only"`).
  Fabricating a translation is the one unrecoverable error in this dataset —
  treated as a capital offense per lane law.
- `domain`: one of the enum values above. One file per domain
  (`vocab/cosmology.json`, `vocab/emotion.json`, `vocab/relations.json`, ...).
- `layer`: integer tier, currently informal (1 = core/frequent, 2 = extended).
  Not yet load-bearing for any downstream script; reserved for future
  weighting.
- `v1_anchor`: `true` iff the `ja` term is one of the fixed anchor set from
  `~/.gaia/knowledge/semantic-map/battery-v1.md`:
  愛/無/影/闇/光/生/死/夢/棄/鳴/残/月/娘/母/神/王/女王. Else `false`.
- `embed_en`: three-valued, and the three values mean three **different**
  things — a downstream truthiness check (`if not e["embed_en"]`) silently
  collapses `null` into `false` and is banned in any code reading this
  field. Always test with `is None` / `is True` / `is False` explicitly.
  - `null` = **unmeasured**. `scripts/embed_check.py` has not run against
    this entry since it last changed. Not evidence of anything.
  - `false` = **method limitation, not a lexical fact**. Apple
    `NLEmbedding.wordEmbedding(for: .english)` has no vector for the `en`
    token. GloVe-family fixed vocabularies systematically lack compounds
    and multi-word terms (e.g. `Korbflechterei`-class craft compounds);
    `false` means "this method couldn't verify a vector", not "this word
    doesn't exist" or "this entry is wrong".
  - `true` = a vector exists for the `en` token under that model.
  - Re-run `scripts/embed_check.py` (writes into `vocab/<domain>.json`)
    after any edit that changes `en`, then re-run `scripts/build_vocab.py`
    — `scripts/validate_vocab.py`'s staleness check catches a merge that
    forgot this.
- `notes`: free text. Required (non-empty) whenever `de` or `zh` is `null`,
  or whenever a translation needed disambiguation (e.g. polysemous `ja`
  term, chosen sense noted).
- `token_collision`: **generated only** (by `scripts/build_vocab.py`, never
  hand-written). `null` if this entry's `ja`/`en`/`de`/`zh` tokens are each
  unique across the whole merged vocab. Otherwise
  `{"<lang>": ["id_a", "id_b", ...]}` for every language where this
  entry shares its token with one or more other entries (the list includes
  this entry's own id, sorted).
  A collision is **a lexical fact, not a
  defect** — two concepts can legitimately have no distinguishing word in
  German or Chinese (`Nebel` = fog and nebula; `Holz` = wood and
  wood-the-element). Fabricating a distinct word to avoid a collision is
  the same capital offense as any other invented translation. Downstream
  code computing embedding distances between concepts MUST treat any pair
  of ids appearing together in the same `token_collision[lang]` list as
  **UNDEFINED for that language**, not `0.0` — their distance is
  identically zero by construction (same input string), which is a fact
  about the tokenization, not a measurement. Report it as excluded, never
  as a measured zero.
  `scripts/validate_vocab.py` treats a *missing or stale* annotation as
  the violation; the collision's mere existence is not one.
- token notation discipline: every `ja`/`en`/`de`/`zh` value is **one
  lexical item**. Parenthetical disambiguation (`"balance (design)"`),
  gender-form markers (`"Bekannte(r)"`), and slash-joined alternatives
  (`"excuse me / sorry"`) do not belong in the token — move that content
  into `notes` and leave the bare word/phrase as the token. Exception: if
  stripping the annotation would **change which concept the bare token
  refers to** (not just remove context), do not strip it — leave the
  token as-is and flag the entry for human review instead (e.g. German
  `Bekannte(r)`: German substantivized adjectives for people have no
  single gender-neutral citation form — `Bekannte` alone reads as
  feminine/plural, not neutral — so stripping `(r)` narrows the reference,
  and is left for a judgment call rather than auto-repaired).
  `scripts/validate_vocab.py` flags any token containing `(` `)` or `/` as
  a violation, without exception — this materializes as a known,
  deliberately-unrepaired residual for the flagged-for-review cases until
  a human decides; see `results/vocab-collision-report.md` /
  `results/vocab-dedup-report.md` for the current list.

## Files owned by this lane (ghoul-sonnet-vocabA)

- `vocab/SCHEMA.md` (this file)
- `scripts/build_vocab.py`, `scripts/validate_vocab.py`, `scripts/embed_check.py`
- `vocab/cosmology.json`, `vocab/emotion.json`, `vocab/relations.json`

Other domains (`craft`, `seven`, `daily`) are owned by parallel lanes — do not
edit those files from here.

# vocab merge/notation/allowlist execution report

Lane: `ghoul-sonnet-vocabmerge`. Executes three operator judgments (2026-08-06)
against `results/vocab-collision-report.md` (design-split candidates) and
`results/vocab-notation-repair-report.md` (26 flagged notation entries).
**No new judgment calls made here** — mechanical execution of the rules the
operator specified. Where a case did not fit any of the three rules exactly,
it is listed in "Escalated" below instead of being decided.

## Judgment 1 — design-split merge: 0 merges (rule correctly yields none)

Rule as given: merge iff all 4 columns (ja/en/de/zh, null==null) match
exactly between the two ids; else do not merge. Checked all 14 unique id
pairs referenced across the 32-row design-split candidate table (union of
the de/en/ja/zh rows — every pair the operator named is in this set):

| pair | ja match | en match | de match | zh match | ALL 4? |
|---|---|---|---|---|---|
| apology / apology_daily | no | no | yes | no | no |
| apprentice / apprentice_craft | no | yes | yes | yes | no |
| calendar / calendar_daily | no | yes | yes | yes | no |
| dust / dust_daily | no | yes | yes | yes | no |
| fish / fish_food | yes | no | yes | yes | no |
| gold / gold_craft | no | yes | yes | no | no |
| metal / metal_element | no | yes | yes | yes | no |
| neighbor / neighbor_daily | no | yes | yes | yes | no |
| pet / pet_daily | yes | no | yes | yes | no |
| temperature / temperature_daily | no | yes | yes | no | no |
| wood / wood_element | no | yes | yes | no | no |
| balance / balance_design | no | yes | no | yes | no |
| favor / favor_ask | no | yes | no | no | no |
| ink / ink_stick | yes | no | no (null vs Tinte) | no | no |

**Every pair fails on at least one column** — in 11/14 cases `ja` differs
(the two ids use genuinely different Japanese words: 暦/カレンダー,
塵/埃, 見習い/徒弟, etc.), which is the same failure mode the operator's own
example (`spring_season`/`spring_water`, en-only collision) already
anticipated as a non-merge case. For `calendar`/`calendar_daily` and
`dust`/`dust_daily` specifically, the source files' own pre-existing
`notes` explicitly document the split as *intentional*: `"disambiguated
id; distinct lexeme from cosmology-domain id=calendar (暦, almanac/
calendar-system sense) — this is the everyday wall/desk calendar object
(カレンダー)"`. That is direct evidence against "帳簿上の重複" for those
two specifically.

Result: **0 merges performed.** `vocab/*.json` unchanged with respect to
merge/deletion. n stays 1750 (not below).

## Judgment 2 — notation repair: 24 of 26 flagged entries fixed

### de gender-suffix (20 entries) — fixed
Rule: strip `(r)`, keep the bare (fem./plural-reading) form as the token,
record the masculine variant in `notes` as `gendered variant: X (m.)`.

| id | de before | de after | notes addition |
|---|---|---|---|
| fiance | Verlobte(r) | Verlobte | gendered variant: Verlobter (m.) |
| relative_kin | Verwandte(r) | Verwandte | gendered variant: Verwandter (m.) |
| acquaintance | Bekannte(r) | Bekannte | gendered variant: Bekannter (m.) |
| stranger | Fremde(r) | Fremde | gendered variant: Fremder (m.) |
| employee | Angestellte(r) | Angestellte | gendered variant: Angestellter (m.) |
| subordinate | Untergebene(r) | Untergebene | gendered variant: Untergebener (m.) |
| commoner | Bürgerliche(r) | Bürgerliche | gendered variant: Bürgerlicher (m.) |
| ally | Verbündete(r) | Verbündete | gendered variant: Verbündeter (m.) |
| lover | Geliebte(r) | Geliebte | gendered variant: Geliebter (m.) |
| soulmate | Seelenverwandte(r) | Seelenverwandte | gendered variant: Seelenverwandter (m.) |
| saint | Heilige(r) | Heilige | gendered variant: Heiliger (m.) |
| scholar | Gelehrte(r) | Gelehrte | gendered variant: Gelehrter (m.) |
| confidant | Vertraute(r) | Vertraute | gendered variant: Vertrauter (m.) |
| elder | Älteste(r) | Älteste | gendered variant: Ältester (m.) |
| prisoner | Gefangene(r) | Gefangene | gendered variant: Gefangener (m.) |
| single_parent | Alleinerziehende(r) | Alleinerziehende | gendered variant: Alleinerziehender (m.) |
| volunteer | Freiwillige(r) | Freiwillige | gendered variant: Freiwilliger (m.) |
| beneficiary | Begünstigte(r) | Begünstigte | gendered variant: Begünstigter (m.) |
| delegate | Delegierte(r) | Delegierte | gendered variant: Delegierter (m.) |
| envoy | Gesandte(r) | Gesandte | gendered variant: Gesandter (m.) |

All in `vocab/relations.json`.

### en slash-alternative (3 entries) — fixed
Rule: keep the first alternative as the token, move the rest to `notes`.

| id | en before | en after | notes addition |
|---|---|---|---|
| apology_daily | excuse me / sorry | excuse me | en alternative: 'sorry' |
| cooked_rice | cooked rice / meal | cooked rice | en alternative: 'meal' |
| idle_time | free/idle (time) | free | en alternative: 'idle (time)' |

All in `vocab/daily.json`. `idle_time`'s `embed_en` was stale after this
edit (`embed_check.py` tokenizes on the first whitespace-split word; before
the fix that word was the non-word `free/idle`, measured `false`; after,
it's `free`, a real vector) — re-ran `scripts/embed_check.py vocab/daily.json`,
flipped `false → true`, then re-ran `scripts/build_vocab.py`.
`apology_daily`/`cooked_rice` had unchanged first tokens (`excuse`/`cooked`
either side of the edit), so no `embed_en` change there.

### de periphrastic (1 entry) — fixed
`molding_clay.de`: `"Formen (Ton)"` → `null`, per instruction ("捏造するな").
`notes` extended with the reason (no single German lexeme; the phrase was a
verb+clarifier gloss, not a fixed compound token).

### Not fixed (2 entries) — escalated, see below
`fish_food` (en: `fish (food)`) and `pet_daily` (en: `pet (animal)`) are
parenthetical-notation violations, not slash-alternative — outside all
three of the operator's stated categories (de-gender, en-slash-3,
de-periphrastic-1). Not decided here; see Escalated section.

## Judgment 3 — de==en allowlist: 7 ids added

Added `DE_EN_IDENTICAL_ALLOWLIST` (individual id enumeration, no pattern
match) to `scripts/validate_vocab.py`; `check_de_eq_en` now skips ids in
it. All 7 pre-existing de==en violations, all international/proper-noun
astronomical names:

| id | de==en | reason |
|---|---|---|
| orion | Orion | constellation/mythological-figure name; same Latin/Greek-derived proper noun in German and English |
| venus_planet | Venus | planet name; same Latin deity-derived proper noun |
| mars_planet | Mars | planet name; same Latin deity-derived proper noun |
| jupiter_planet | Jupiter | planet name; same Latin deity-derived proper noun |
| saturn_planet | Saturn | planet name; same Latin deity-derived proper noun |
| uranus_planet | Uranus | planet name; same Greek deity-derived proper noun |
| pluto_planet | Pluto | planet name; same Latin deity-derived proper noun (2006 dwarf-planet reclassification doesn't change the lexeme) |

No non-international/non-proper-noun de==en cases exist in the current 7 —
nothing held back for separate report.

## Escalated — does not fit judgments 1–3, returned to operator

**`fish_food` and `pet_daily`** (both `vocab/daily.json`, en fields
`fish (food)` / `pet (animal)`):
- Not a judgment-1 case: `fish`/`fish_food` and `pet`/`pet_daily` fail the
  4-column-match test (en differs precisely because of the parenthetical).
- Not a judgment-2 case: the operator's 3 named en-notation entries are all
  slash-alternatives (`X / Y`); these two are parenthetical-context
  entries, a different shape, already tried and reverted by the prior lane
  because stripping the parenthetical collapses them fully onto
  `fish`/`pet` (ja/de/zh already identical to those ids; the `(food)`/
  `(animal)` parenthetical is the *only* remaining distinguishing signal).
  Per SCHEMA.md's own exception clause ("if stripping would change which
  concept the bare token refers to... flag for human judgment instead of
  guessing"), this is exactly that case.
- Not a judgment-3 case (not de==en).

No unilateral decision made. Two real options exist for the operator to
choose between (not chosen here): (a) treat as a genuine 4th design-split
case and merge `fish_food`→`fish`, `pet_daily`→`pet` despite the notation
non-conformance being the reason they still look distinct, or (b) invent a
non-parenthetical English disambiguator (e.g. new id/token pair) — which
risks the fabrication line if no attested alternate phrase exists. Left
exactly as inherited; both remain the only 2 residual validator violations.

## Final measurements (re-measured immediately before writing this report)

`python3 scripts/build_vocab.py` → `wrote 1750 entries from 5 domain files`.

`python3 scripts/validate_vocab.py`:
```
=== per-domain counts ===
  cosmology: 350
  craft: 350
  daily: 350
  emotion: 350
  relations: 350
  TOTAL: 1750

=== duplicate token audit (per language column; null excluded) ===
  ja: null=0  species=21  affected=43  surplus=22
  en: null=0  species=12  affected=24  surplus=12
  de: null=44  species=54  affected=110  surplus=56
  zh: null=13  species=44  affected=88  surplus=44

=== 2 error(s) ===
  id 'fish_food': en token 'fish (food)' contains '(' ')' or '/' -- ...
  id 'pet_daily': en token 'pet (animal)' contains '(' ')' or '/' -- ...
```
Exit code: **1** (2 known, escalated, deliberately-unrepaired violations —
not silently passed, not allowlisted, per instruction). `de` null count
rose 43→44 (`molding_clay` newly null, correctly non-blank-excluded from
grouping, and its `notes` carries the required non-empty justification).
STALE check: no violation (vocab.json matches a fresh merge). `embed_en`:
1670 true / 80 false / 0 null (unchanged null count; only `idle_time`
flipped false→true, already re-measured above). No `token_collision`
annotation-consistency violation. No zh Traditional-character violation.
No `embed_en` truthiness-scan violation.

Bracket/slash token residue across all 4 languages, all 1750 entries:
**2** (`fish_food` en, `pet_daily` en) — both escalated, none elsewhere.

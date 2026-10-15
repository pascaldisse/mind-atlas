# token notation repair report (D)

Lane: `ghoul-sonnet-vocabfix`. n=1750, measured after `scripts/build_vocab.py`
regeneration.

## Rule (per operator instruction, now in `vocab/SCHEMA.md`)

Every `ja`/`en`/`de`/`zh` token must be **one lexical item**. Parenthetical
disambiguation, gender-form markers, and slash-joined alternatives belong
in `notes`, not the token. Default action: strip the annotation, move it to
`notes`, keep the bare word as the token. **Exception**: if stripping would
change which concept the bare token refers to (not just remove context),
leave it unchanged and flag for human judgment instead of guessing.

Audited count matched the operator's own measurement exactly: **85** tokens
(64 en + 21 de) containing `(` `)` or `/` before this repair; ja/zh: 0.

## Auto-repaired: 59 entries (all `en`, all in `vocab/{craft,daily,relations,emotion}.json`)

Mechanical rule applied: strip the trailing `(...)` group (or, for
`fiancé(e)`, the gender-variant suffix), move the removed text into
`notes`, keep the remaining bare phrase as `en`. Verified safe per-entry:
the removed text was purely disambiguating *context* (domain/sense
clarifier), not an alternate reading of the word itself, **and** the
result does not collide (ja,en) with any other entry (checked by rerunning
`scripts/validate_vocab.py`'s pre-existing pair-uniqueness check after each
batch — see the two reversions below).

Full list (id: before → after):

```
knot_wood: 'knot (in wood)' -> 'knot'
file_tool: 'file (tool)' -> 'file'
compass_drafting: 'compass (drawing tool)' -> 'compass'
spin_thread: 'spin (thread)' -> 'spin'
loom_shuttle: 'shuttle (weaving)' -> 'shuttle'
fire_ceramics: 'to fire (ceramics)' -> 'to fire'
crack_repair: 'crack (in ceramics)' -> 'crack'
engobe: 'slip (ceramics)' -> 'slip'
furnace_glass: 'furnace (glass/kiln)' -> 'furnace'
blowpipe: 'blowpipe (glass)' -> 'blowpipe'
cast_craft: 'to cast (metal/material)' -> 'to cast'
binder_craft: 'binder (material)' -> 'binder'
temper: 'temper (metal)' -> 'temper'
hardening: 'hardening (metal)' -> 'hardening'
seal_stamp: 'seal (stamp)' -> 'seal'
ink_pad: 'ink pad (for seals)' -> 'ink pad'
stamp_craft: 'stamp (tool)' -> 'stamp'
sketch: 'sketch (preliminary drawing)' -> 'sketch'
tanning: 'tanning (leather)' -> 'tanning'
iteration: 'iteration (improvement)' -> 'iteration'
balance_design: 'balance (design)' -> 'balance'
grade_material: 'grade (of material)' -> 'grade'
exhibit_craft: 'exhibition (craft)' -> 'exhibition'
entrance: 'entrance (of a home)' -> 'entrance'
fish (food) sense: see REVERTED below -- NOT applied
full_stomach: 'full (stomach)' -> 'full'
break_time: 'break (rest)' -> 'break'
overtime: 'overtime (work)' -> 'overtime'
dry_clothes: 'to dry (clothes)' -> 'to dry'
iron_clothes: 'to iron (clothes)' -> 'to iron'
wrinkle_clothes: 'wrinkle (in fabric)' -> 'wrinkle'
try_on: 'to try on (clothes)' -> 'to try on'
take_off_clothes: 'to take off (clothes)' -> 'to take off'
wardrobe: 'wardrobe (furniture)' -> 'wardrobe'
dream_daily: 'to dream (while sleeping)' -> 'to dream'
stretch_body: 'to stretch (body)' -> 'to stretch'
stretching_exercise: 'stretching (exercise routine)' -> 'stretching'
mask_daily: 'face mask (hygiene)' -> 'face mask'
grooming: 'grooming (getting ready)' -> 'grooming'
change_money: 'change (money returned)' -> 'change'
allowance: 'allowance (pocket money)' -> 'allowance'
bill_payment: 'payment (bill)' -> 'payment'
return_item: 'return (of an item)' -> 'return'
exchange_item: 'exchange (of goods)' -> 'exchange'
hot_weather: 'hot (weather)' -> 'hot'
cold_weather: 'cold (weather)' -> 'cold'
ticket_transport: 'ticket (transport)' -> 'ticket'
transfer_train: 'transfer (trains)' -> 'transfer'
regular_customer: 'regular (customer)' -> 'regular'
catch_up: 'catching up (conversation)' -> 'catching up'
favor_ask: 'favor (a request)' -> 'favor'
clean_room: 'to clean (a room)' -> 'to clean'
pet (animal) sense: see REVERTED below -- NOT applied
missing_someone: 'missing (someone)' -> 'missing'
withdrawal_feeling: 'withdrawal (feeling)' -> 'withdrawal'
fiance: 'fiancé(e)' -> 'fiancé'  (gender-variant marker moved to notes; masculine
    citation form kept, consistent with this same entry's existing zh
    choice of 未婚夫 [male] over 未婚妻 [female])
credit_for_achievement: 'credit (for achievement)' -> 'credit'
senior_social: 'senior (social)' -> 'senior'
junior_social: 'junior (social)' -> 'junior'
owner: 'owner (of a pet)' -> 'owner'
mask_figurative: 'mask (figurative)' -> 'mask'
```

(59 lines above; `fish_food`/`pet_daily` listed only as pointers to the
reversion below, not counted in the 59.)

## Reverted: 2 entries (auto-fix applied, then undone)

Both were caught by `scripts/validate_vocab.py`'s pre-existing (ja,en)-pair
uniqueness check immediately after the mechanical strip:

| id | domain | field | before | attempted (reverted) | why |
|----|--------|-------|--------|----------------------|-----|
| `fish_food` | daily | en | `fish (food)` | `fish` | ja/de/zh already collide with `fish` (cosmology, animal sense). `(food)` was the *only* remaining distinguishing signal across all 4 language columns; stripping it made the two entries fully identical. |
| `pet_daily` | daily | en | `pet (animal)` | `pet` | Same failure mode against `pet` (relations); ja/de/zh already collide. |

Both restored to their original value; both remain in the
validator's bracket/slash violation list (see below) pending a human
decision on how to disambiguate them (they were already relying on the
now-forbidden parenthetical as their sole distinguishing device — this is
a genuine design problem in the vocab, not a notation-style issue this
lane can resolve by moving text into `notes`).

## Flagged for human judgment: 26 entries (left unchanged, still flagged by validator)

These were **not** auto-repaired because stripping the annotation would
change (or already changed, in the 2 reverted cases above) which concept
the bare token identifies — the fallback rule in `vocab/SCHEMA.md`.

### 3 en: bare top-level slash = alternate full glosses, not context

| id | domain | en | why risky |
|----|--------|----|-----------|
| `apology_daily` | daily | `excuse me / sorry` | two distinct English phrases for one ja/de/zh concept; picking one drops a real nuance (attention-getting vs. apologizing), no clearly correct single choice |
| `cooked_rice` | daily | `cooked rice / meal` | ja itself is documented as polysemous (cooked-rice vs. generic meal) in `notes`; en mirrors that polysemy on purpose |
| `idle_time` | daily | `free/idle (time)` | two adjective alternatives (`free`/`idle`) *plus* a trailing parenthetical; compound ambiguity, not simple context |

### 21 de: gender-suffix or periphrastic-phrase, no safe default

| id | domain | de | why risky |
|----|--------|----|-----------|
| `molding_clay` | craft | `Formen (Ton)` | entry's own `notes` already states this is a descriptive gloss (verb+clarifier), not a fixed compound lexeme — the *whole phrase* is the attested rendering; bare `Formen` alone is too generic (means "shapes"/"to form" broadly, loses the clay-specific sense) |
| `acquaintance`, `ally`, `beneficiary`, `commoner`, `confidant`, `delegate`, `elder`, `employee`, `envoy`, `fiance` (de field only — en already fixed), `lover`, `prisoner`, `relative_kin`, `saint`, `scholar`, `single_parent`, `soulmate`, `stranger`, `subordinate`, `volunteer` | relations | `Bekannte(r)`, `Verbündete(r)`, etc. | German substantivized adjectives for people have **no single gender-neutral citation form**: bare `Bekannte` (without the parenthetical `-r`) reads as feminine/plural in isolation, not neutral. Stripping `(r)` narrows the reference rather than just removing context. Unlike `fiance`'s en field, none of these 20 entries carry an existing in-entry precedent for defaulting to one gender (fiancé's notes already documented a male default via zh 未婚夫, which is why that specific field was judged safe to auto-fix). No such anchor exists here, so all 20 (+ the already-fixed `fiance`'s own `de` field) are left for a human call: pick a default gender convention, or restructure as two ids. |

**Do not attempt to resolve these without instruction** — several require a
judgment call about German grammar convention (gender-neutral citation
form) or about which English gloss the concept actually wants, not a
mechanical text move.

## Post-repair validator state (re-measured before writing this report)

`scripts/validate_vocab.py` exit 1, 33 errors: 26 bracket/slash (3 en +
1 de-phrase + 21 de-gender, all in the flagged table above) + 7 de==en
(planet names, unrelated to this task, not repaired — see original task
scope). 0 duplicate-token violations (all real collisions correctly
annotated by `token_collision`, per `results/vocab-collision-report.md`).

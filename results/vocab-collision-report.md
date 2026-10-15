# vocab token collision report

Lane: `ghoul-sonnet-vocabfix` · measured after commit that added `token_collision`
annotation to `vocab.json` (`scripts/build_vocab.py`). n=1750.

## Why this report exists, and why it does *not* contain repairs

The original task asked this lane to "resolve" de/zh duplicate tokens (pick a
different word, or null the field). The operator retracted that instruction
mid-lane after a stratified re-measurement: **only 12 of the 54 de collision
groups are id-prefix-related "design split" pairs; the remaining 42 are true
lexical gaps** (`Nebel` = fog and nebula, `Holz` = wood and wood-the-element,
`魚`/`鱼` = fish and fish-as-food — German/Chinese simply have one word for
both senses). Forcing a distinct word into those 42 would be fabrication —
the one unrecoverable/capital-offense error in this dataset per
`vocab/SCHEMA.md`.

**New rule, implemented instead of repair:** collisions are a lexical fact,
not a defect. `scripts/build_vocab.py` mechanically annotates every entry
that shares a ja/en/de/zh token with another entry via a generated
`token_collision` field (see `vocab/SCHEMA.md`). `scripts/validate_vocab.py`
enforces that the annotation is present and correct — the violation is an
*unannotated* collision, not the collision itself.

This report enumerates the collision groups so a human can decide whether
any design-split candidates should be merged. **No merge/repair decisions
are made here** — enumeration only, per instruction.

(For the historical record: `results/vocab-dedup-report.md` explains the
retraction in one paragraph and points back here.)

## Method

For every entry in `vocab.json`, `build_vocab.compute_token_collisions()`
groups entries by exact string equality per language column (ja/en/de/zh),
excluding `null`. Any group with ≥2 members is a collision. A group is
classified **design-split candidate** if any two ids in it are related by
an `id`/`id_suffix` naming pattern (e.g. `calendar` / `calendar_daily`,
`gold` / `gold_craft`) — this is a *naming* heuristic, not a semantic
judgment. Everything else is **true lexical collision**.

## Summary (re-measured at report time)

| lang | null | species | affected | surplus |
|------|------|---------|----------|---------|
| ja   | 0    | 21      | 43       | 22      |
| en   | 0    | 12      | 24       | 12      |
| de   | 43   | 54      | 110      | 56      |
| zh   | 13   | 44      | 88       | 44      |

(en species rose from 9→12 over the course of this lane: 3 new en-level
collisions were *introduced* by the D-notation repair in this same lane —
`balance`/`balance_design`, `apprentice`/`apprentice_craft`,
`favor`/`favor_ask` — when the disambiguating `(design)`/`(craft)`/`(a
request)` parenthetical was moved to `notes`, their bare `en` became
identical. All three remain distinguishable by `ja` (均衡 vs バランス, 見習い
vs 徒弟, 恩恵 vs お願い), so this is a normal, correctly-annotated en-level
collision, not a duplicate concept. Two other candidates from the same
repair pass — `fish_food`/`pet_daily` — were **reverted**, not merely
annotated, because stripping their bracket made them fully identical to
`fish`/`pet` across *all four* language columns (a real duplicate-concept
collapse, caught by the pre-existing (ja,en)-pair check); see
`results/vocab-dedup-report.md`.)

Total collision groups across all 4 languages: **131** (32 design-split
candidates, 99 true lexical collisions).

## Design-split candidates (32 groups) — id-prefix related, report only

These pairs/sets have an `id` naming relationship (`X` / `X_daily`,
`X` / `X_craft`, etc.) *and* a shared token in at least one language. They
are candidates for "is this actually one concept registered twice", not
confirmed duplicates. **Decision to merge is explicitly left to the
operator per instruction.**

| lang | token | ids | domains |
|------|-------|-----|---------|
| de | Entschuldigung | apology, apology_daily | relations, daily |
| de | Lehrling | apprentice, apprentice_craft | relations, craft |
| de | Kalender | calendar, calendar_daily | cosmology, daily |
| de | Staub | dust, dust_daily | cosmology, daily |
| de | Fisch | fish, fish_food | cosmology, daily |
| de | Gold | gold, gold_craft | cosmology, craft |
| de | Metall | metal, metal_element | craft, cosmology |
| de | Nachbar | neighbor, neighbor_daily | relations, daily |
| de | Haustier | pet, pet_daily | relations, daily |
| de | Temperatur | temperature, temperature_daily | cosmology, daily |
| de | Holz | wood, wood_element | craft, cosmology |
| en | apprentice | apprentice, apprentice_craft | relations, craft |
| en | balance | balance, balance_design | cosmology, craft |
| en | calendar | calendar, calendar_daily | cosmology, daily |
| en | dust | dust, dust_daily | cosmology, daily |
| en | favor | favor, favor_ask | relations, daily |
| en | gold | gold, gold_craft | cosmology, craft |
| en | metal | metal, metal_element | craft, cosmology |
| en | neighbor | neighbor, neighbor_daily | relations, daily |
| en | temperature | temperature, temperature_daily | cosmology, daily |
| en | wood | wood, wood_element | craft, cosmology |
| ja | 魚 | fish, fish_food | cosmology, daily |
| ja | 墨 | ink, ink_stick | craft, craft |
| ja | ペット | pet, pet_daily | relations, daily |
| zh | 徒弟 | apprentice, apprentice_craft | relations, craft |
| zh | 平衡 | balance, balance_design | cosmology, craft |
| zh | 日历 | calendar, calendar_daily | cosmology, daily |
| zh | 灰尘 | dust, dust_daily | cosmology, daily |
| zh | 鱼 | fish, fish_food | cosmology, daily |
| zh | 金属 | metal, metal_element | craft, cosmology |
| zh | 邻居 | neighbor, neighbor_daily | relations, daily |
| zh | 宠物 | pet, pet_daily | relations, daily |

Note: `ink`/`ink_stick` (ja 墨) is *not* an `_domain`-suffix split like the
others — flagged by the naming heuristic because `ink_stick` starts with
`ink_`, but it may genuinely be two craft-domain concepts (ink vs. the
solid ink-stick object) rather than a registration duplicate. Included
here rather than silently dropped since the heuristic fired; operator
judgment needed same as the rest.

## True lexical collisions (99 groups) — not a defect, no action

Unrelated ids sharing a token because the language has one word for both
concepts. Full list (id pairs, domains) below for audit traceability.

### de (43 groups)
Zuneigung {affection, fondness} both emotion · Angst {anxiety, fear} both emotion ·
Schmied {blacksmith(relations), smith(craft)} · Schuld {blame, debt_gratitude} both relations ·
Decke {blanket, ceiling} both daily · kochen {boil, cook_verb} both daily ·
Freund {boyfriend, friend} both relations · Ruhe {calm, tranquility} both emotion ·
schnitzen {carve, whittle} both craft · Berühmtheit {celebrity, fame} both relations ·
Kette {chain_craft, warp} both craft · schneiden {chop_food(daily), cut_craft(craft)} ·
Konflikt {conflict_interpersonal(relations), inner_conflict(emotion)} ·
Verbindung {connection_emotional(emotion), joint(craft)} · Vertrag {contract, treaty} both relations ·
Gelassenheit {coolness_composure, equanimity, serenity} all emotion (3-way) ·
Verlangen {craving, desire} both emotion · Schrei {cry_sound, scream} both emotion ·
Entschlossenheit {decisiveness, determination} both emotion · Hingabe {devotion, wholeheartedness} both emotion ·
Schüler {disciple, student} both relations · Kummer {distress, sorrow} both emotion ·
Eifer {eagerness, zeal} both emotion · Leere {emptiness_emotional(emotion), void(cosmology)} ·
Stich {engraving_print, stitch} both craft · Bitte {favor_ask(daily), request(relations)} ·
Boden {floor(daily), soil(cosmology)} · Nebel {fog, nebula} both cosmology ·
Freizeit {free_time, idle_time} both daily · Grinsen {grin, smirk} both emotion ·
Groll {grudge, resentment} both emotion · Herzschmerz {heartache, heartbreak} both emotion ·
Himmel {heaven, sky} both cosmology · Erbe {heir, inheritance} both relations ·
Sehnsucht {longing, missing_someone} both emotion ·
Meister {master_craft(relations), master_craftsman(craft)} · Geheimnis {mystery, secret} both cosmology ·
Opfer {offering_religious(cosmology), sacrifice_religious(cosmology), victim(relations)} (3-way) ·
Muster {pattern, sample} both craft · Reue {regret, remorse} both emotion ·
Unruhe {restlessness, turmoil_emotional} both emotion · Selbstwertgefühl {self_esteem, self_worth} both emotion ·
Wolle {wool, yarn} both craft

### en (2 groups)
compass {compass_drafting(craft), compass_tool(cosmology)} · spring {spring_season, spring_water} both cosmology

### ja (18 groups)
無関心 {apathy, indifference} both emotion · 約束 {appointment(daily), promise(relations)} ·
執着 {attachment, obsession} both emotion · 焼く {bake, fire_ceramics, fry} (3-way, daily/craft/daily) ·
鍛冶屋 {blacksmith(relations), smith(craft)} · 茶碗 {bowl_craft, bowl_daily} ·
切る {chop_food(daily), cut_craft(craft)} · 織物 {cloth, weaving} both craft ·
習慣 {custom_social(relations), routine(daily)} · 金 {gold_craft(craft), metal_element(cosmology)} ·
恨み {grudge, resentment} both emotion · 後継者 {heir, successor} both relations ·
寛容 {magnanimity, tolerance} both emotion · 月 {month, moon} both cosmology ·
家長 {parent, patriarch} both relations · 型紙 {pattern_paper, stencil} both craft ·
雨 {rain(cosmology), rainy(daily)} · 雪 {snow(cosmology), snowy(daily)}

### zh (36 groups)
养父母 {adoptive_parent, foster_parent} · 冷漠 {apathy, coldness_emotional} · 尴尬 {awkwardness, embarrassment} ·
洗澡 {bath, take_a_bath} · 铁匠 {blacksmith(relations), smith(craft)} · 休息 {break_time, rest_body} ·
雕刻 {carve, engrave} · 木屑 {chip_wood, sawdust} · 承诺 {commitment(emotion), promise(relations)} ·
同情 {compassion, sympathy} · 手艺 {craftsmanship, skill} · 代表 {delegate, representative} ·
喜悦 {delight, joy} · 义务 {duty, obligation_social} · 鹰 {eagle, hawk} · 名声 {fame, reputation} ·
家庭 {family, household} · 请求 {favor_ask(daily), request(relations)} · 节日 {festival(relations), holiday(daily)} ·
温柔 {gentleness, tenderness} · 等级 {grade_material(craft), rank_social(relations)} · 打磨 {grinding, polish} ·
直觉 {gut_feeling, intuition} · 走廊 {hallway, veranda} · 举报人 {informant, whistleblower} ·
店主 {innkeeper, shopkeeper} · 邀请 {invitation(relations), invite(daily)} · 榫卯 {joinery, mortise_and_tenon} ·
编织 {knit, weaving} · 流星 {meteor, shooting_star} · 整理 {organize, tidying_up} · 家长 {parent, patriarch} ·
撅嘴 {pout, sulkiness} · 焊接 {soldering, welding} · 脆弱 {vulnerability, weakness_emotional} ·
工作日 {weekday, workday}

(all "both X" domain pairs above match their listed single domain unless
noted; ids not restated per row are same-domain as their group)

## Downstream consequence (must be respected by any distance computation)

Per `vocab/SCHEMA.md`: any two ids in the same `token_collision[lang]` list
have a cosine/embedding distance of **exactly 0 by construction** in that
language (same input string to the embedding model), not by measurement.
Downstream code (battery-v2 ZH-basis, DE trajectory work) must treat such
pairs as **UNDEFINED / excluded from that language's statistics**, never
report the 0 as a measured distance.

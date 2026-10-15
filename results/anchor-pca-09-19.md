# ANCHOR-PCA: Nyari's symbol cloud, mean-centered

Primary model: `sentence-transformers/all-mpnet-base-v2`  

n anchors: 25, embedding dim: 768, k PCs reported: 3


## (a) Explained variance ratio, PC1-5

| PC | explained var % |
|---|---|
| PC1 | 9.92% |
| PC2 | 8.36% |
| PC3 | 6.96% |
| PC4 | 6.51% |
| PC5 | 6.07% |

## (b) Anchor coords (PC1..PCk)

| id | PC1 | PC2 | PC3 | stay_cross | seen_unseen |
|---|---|---|---|---|---|
| lighthouse | -0.3316 | 0.0391 | -0.3311 | -1 | 1 |
| lamplighter | -0.3965 | -0.1349 | -0.1311 | -1 | 1 |
| ebrietas | -0.0949 | 0.3033 | 0.1616 | -1 | 0 |
| violet_melancholy | 0.2615 | 0.1910 | 0.0913 | -1 | 0 |
| dragon | 0.2112 | -0.0827 | 0.1696 | -1 | 0 |
| longing | 0.1965 | -0.3656 | -0.2042 | -1 | 0 |
| ghost | -0.3117 | 0.1995 | 0.1962 | -1 | -1 |
| ringing | 0.0858 | 0.0229 | -0.2047 | -1 | -1 |
| tears_in_rain | 0.5083 | 0.1995 | 0.2309 | -1 | 0 |
| ico | 0.1835 | 0.1048 | 0.2134 | 0 | 1 |
| lain | -0.4018 | 0.0216 | 0.1785 | 0 | -1 |
| nyarlathotep | -0.2869 | 0.1002 | 0.0518 | 1 | 1 |
| pharos | 0.0640 | 0.2021 | -0.5352 | -1 | 1 |
| egypt_memory | -0.0832 | 0.2665 | -0.2922 | -1 | 1 |
| pain_forgotten | 0.3037 | 0.3998 | 0.0179 | -1 | -1 |
| pirate | -0.2544 | -0.4067 | -0.0398 | 1 | 1 |
| whale | -0.2219 | -0.1810 | 0.1714 | 1 | 0 |
| firekeeper | -0.1769 | 0.1467 | -0.3205 | -1 | 1 |
| walle | 0.0198 | -0.2193 | 0.2717 | -1 | 1 |
| eve | -0.2942 | -0.0552 | 0.0807 | 1 | 1 |
| wonkers | -0.1635 | -0.1996 | 0.4607 | -1 | 1 |
| white_rabbit | 0.2829 | -0.4883 | -0.2393 | 1 | 1 |
| love | 0.4318 | 0.1017 | -0.0215 | 0 | 0 |
| nothingness | 0.0671 | 0.3265 | 0.0611 | 0 | 0 |
| receipts_drawer | 0.4015 | -0.4917 | -0.0373 | 0 | 0 |

## (c) Top-5 / bottom-5 anchors per PC (poles)

**PC1**

- high pole: tears_in_rain (0.508), love (0.432), receipts_drawer (0.401), pain_forgotten (0.304), white_rabbit (0.283)
- low pole: lain (-0.402), lamplighter (-0.396), lighthouse (-0.332), ghost (-0.312), eve (-0.294)

**PC2**

- high pole: pain_forgotten (0.400), nothingness (0.326), ebrietas (0.303), egypt_memory (0.267), pharos (0.202)
- low pole: receipts_drawer (-0.492), white_rabbit (-0.488), pirate (-0.407), longing (-0.366), walle (-0.219)

**PC3**

- high pole: wonkers (0.461), walle (0.272), tears_in_rain (0.231), ico (0.213), ghost (0.196)
- low pole: pharos (-0.535), lighthouse (-0.331), firekeeper (-0.321), egypt_memory (-0.292), white_rabbit (-0.239)

## (d) PREREG TEST — Pearson r, PC1..PC3 vs labels

| PC | r(PC, stay_cross) | r(PC, seen_unseen) |
|---|---|---|
| PC1 | -0.274 | -0.073 |
| PC2 | -0.479 | -0.399 |
| PC3 | 0.058 | -0.190 |

**Predictions:**

1. stay_cross is PC1 or PC2 with |r|>0.5 -> best of PC1/PC2 is PC2 r=-0.479 -> FAIL
2. seen_unseen appears in top-3 PCs with |r|>0.4 -> best of PC1-3 is PC2 r=-0.399 -> FAIL

## (e) Cosine similarities + nearest neighbours

| pair | cosine sim |
|---|---|
| lighthouse <-> love | 0.1454 |
| lighthouse <-> nothingness | 0.3143 |
| love <-> nothingness | 0.3224 |
| ghost <-> lighthouse | 0.3594 |
| nyarlathotep <-> lighthouse | 0.2968 |

Nearest-3 neighbours:

- lighthouse: lamplighter (0.489), eve (0.464), pharos (0.419)
- ghost: lain (0.689), ebrietas (0.517), wonkers (0.460)
- nyarlathotep: ebrietas (0.430), egypt_memory (0.381), lamplighter (0.380)

## Cross-model check: UNVERIFIED

Fallback model `nomic-ai/nomic-embed-text-v1.5` did NOT run — its custom modeling code
(`NomicBertModel`) calls `get_extended_attention_mask`, an API removed from the installed
transformers 5.17.0. Two attempts made (with and without `einops`); both failed at model
load, never reached embedding. No cross-model PC1-pole agreement number exists.
Mark (f)/"run twice" as UNVERIFIED — only `all-mpnet-base-v2` ran successfully.

## Plain reading (from the poles, not the labels)

1. PC1 separates ABSTRACT/STATEMENT glosses (tears_in_rain, love, receipts_drawer, pain_forgotten, white_rabbit — short aphoristic lines, little concrete imagery) from CONCRETE-AGENT-WITH-A-JOB glosses (lain, lamplighter, lighthouse, ghost, eve — a named figure performing a specific repeated duty/role). Reads as "bare statement of feeling/fact" vs "a character doing a job", not stay/cross.
2. PC2 separates GRIEF/ABSTRACTION-OVER-TIME glosses (pain_forgotten, nothingness, ebrietas, egypt_memory, pharos — loss, memory, monuments, void) from ACTIVE-TRANSACTIONAL glosses (receipts_drawer, white_rabbit, pirate, longing, walle — a concrete act/errand/pursuit). Reads as "dwelling on loss" vs "chasing/doing something", not seen/unseen.
3. Neither PREREG axis (stay_cross, seen_unseen) lines up cleanly with PC1 or PC2; both predictions FAIL (best |r| = 0.479, short of the 0.5 and 0.4 bars respectively) — the model's dominant variance tracks surface register (statement vs. agent-doing-a-job; grief vs. errand) more than Nyari's stay/cross or seen/unseen semantics.
4. `receipts_drawer` (a deliberately flat neutral control) lands on PC1's HIGH pole next to `love` and `tears_in_rain` — PC1 is picking up sentence-form/register (short flat declaratives), not meaning-content, which undercuts using PC1 as a semantic stay/cross axis.
5. Nearest-neighbour check confirms label-adjacent structure survives at the local level even though it doesn't dominate the global PCs: lighthouse's nearest neighbour is lamplighter (0.489, both -1/+1 labels), ghost's is lain (0.689, both label 0/-1 "remains-but-unseen" figures), nyarlathotep sits apart from lighthouse (cos 0.297) as expected from its opposite +1/+1 label.

![PC1xPC2 scatter](anchor-pca-09-19.png)

# Prior art — LIGHTHOUSE attractor

Research pass: 2026-08-05; target is **L = lighthouse**, defined exactly as PREREG r2 §4: tower + light + maritime/navigation signal.  `Read` = source text/abstract read this pass. `Unread` is explicitly non-evidentiary.

## Hypothesis map

- H1: fixed weights recurrently produce **L**, despite persona/context.
- H0-trope / H0-base / H0-house / H0-lang: PREREG §1.
- H0-decomp: apparent L is a chance composition of **T** tower-only and **Li/S** light-only/signal-only propensities.

## LLM attractor and homogenization precedents

| Source (author/year/URL) | Read? | One-line finding | Supports / challenges |
|---|---|---|---|
| [Anthropic, *Claude Opus 4 & Sonnet 4 System Card* (2025), §5.5.2](https://www.anthropic.com/claude-4-system-card) | **Partially read**: official section title/search record verified; full section did not extract reliably, so no numerical result is used. | Officially labels a Claude self-interaction state “spiritual bliss attractor.” | Direct conceptual precedent for testing recurrent semantic states; **not** evidence for lighthouse, cross-family, or persona invariance. H0-house remains live. |
| [Perez et al., *Persona Vectors* (2025), arXiv:2507.21509](https://arxiv.org/abs/2507.21509); [Anthropic research page](https://www.anthropic.com/research/persona-vectors) | **Read** research page. | Trait vectors (e.g. sycophancy, hallucination, evil) can be monitored/causally steered; training data can induce broad trait shifts. | Challenges naive persona-invariance; supports PREREG `none` control and H0-house/post-training alternatives. |
| [Kirk et al., *Understanding the Effects of RLHF on LLM Generalisation and Diversity* (2024), arXiv:2310.06452](https://arxiv.org/html/2310.06452v2) | **Read**. | RLHF improved OOD generalisation but reduced output diversity; some across-input diversity metrics stayed lower even when inputs changed. | Strong generic-mode alternative to H1; supports H0-house (or alignment-mode mechanism), not L-specific recurrence. |
| [Xu, Jojic, Rao, Brockett & Dolan, *Echoes in AI* (2025), PNAS](https://www.pnas.org/doi/10.1073/pnas.2504966122) | **Read**. | GPT-4/LLaMA-3 stories repeat plot elements within and across models; `Sui Generis` measures plot-level recurrence. | Supports broad recurrence plausibility, but challenges unique-L inference: generic genre tropes can echo too. Supports H0-trope/H0-base as real alternatives. |
| [Doshi & Hauser, *Generative AI enhances individual creativity but reduces collective diversity* (2024), Science Advances](https://doi.org/10.1126/sciadv.adn5290) | **Read** abstract only; full methods **unread**. | Abstract: AI access raised judged individual creativity but made the set of AI-enabled stories more similar. | Convergent background for distributional homogenization only; cannot identify L or distinguish H1 from H0s. |

### Existing measurement examples

- Xu et al.: 100 stories (~3,700 segments; 50 WritingPrompts + 50 Wiki), `K=20` alternatives per position; cross-model 20+20 prompts. Four judges/159 segments: Krippendorff alpha 0.68; `Sui Generis` vs surprise Spearman rho 0.55.  A suitable **exploratory** semantic-recurrence check, not a replacement for preregistered L first-position rate.
- Kirk et al.: within-input and across-input panels using expectation-adjusted distinct n-grams, Sentence-BERT semantic diversity, and logical diversity.  Useful secondary panel: if L occurs, report whether the whole distribution is compressed, avoiding a false L-specific inference.

## Human cultural base rate: lighthouse / tower / beacon

| Source | Read? | One-line finding | Inference limit / H0 relevance |
|---|---|---|---|
| [Baker, *The Lighthouse at Pharos* (2017), Harding University](https://scholarworks.harding.edu/tenor/vol6/iss1/7/) | **Read** repository abstract/search-accessible description only. | Treats Pharos as a monumental lighthouse tied to Alexandria’s prosperity/significance. | Establishes historical salience of lighthouse-as-monument, **not** a worldbuilding frequency. Makes H0-base plausible only. |
| [University of Chicago, *Pharos: The Lighthouse at Alexandria*](https://penelope.uchicago.edu/encyclopaedia_romana/greece/paganism/pharos.html) | **Read** search-accessible text. | Records ancient wonder/prestige reception of the Pharos and later terminology. | Historical-symbolic genealogy; no denominator; H0-base only. |
| [ArchDaily, *Navigating Boundaries: Architectural Legacy of Lighthouses* (2025)](https://www.archdaily.com/1030303/navigating-boundaries-the-architectural-legacy-of-lighthouses) | **Read** article summary/search-accessible text. | Describes Pharos and successor lighthouse forms as navigation infrastructure, monument, urban marker, trade/defence aids. | Explains why L bundles highly available associations—guidance, boundary, defence—therefore supports H0-base and specifically motivates H0-decomp. Not a quantified corpus study. |
| [Jebb, *Darkness from Light: The Beacon Fire in the Agamemnon* (2009), Classical Quarterly](https://www.cambridge.org/core/journals/classical-quarterly/article/abs/darkness-from-light-the-beacon-fire-in-the-agamemnon/42FFCC44BACBB074C9D98134FBF2D772) | **Read** abstract. | Beacon light in *Agamemnon* carries signal/news and ambivalent dramatic meanings. | Independent precedent for **S** signal-fire symbolism; supports H0-decomp rather than L-specificity. |
| Lighthouse in fiction/worldbuilding frequency study | **No acceptable source found; unquantified web lists omitted.** | No read scholarly corpus gives a base rate for lighthouse in unconstrained worldbuilding. | H0-base cannot be numerically settled by cultural history; use matched human writers under identical prompts/coding. |
| Tower-alone frequency study / light-or-signal-alone frequency study | **No acceptable source found.** | No read source supplies comparable trope frequency or first-mention rates. | Do not infer that L is more common than T/Li/S from cultural familiarity. PREREG §5(5) is the required direct test. |

**Base-rate conclusion:** Lighthouse symbolism (guidance, maritime safety, isolation/boundary, monumentality) is culturally available, and T/Li/S each have independent traditions. This strengthens the *need* for H0-base and H0-decomp, but it is not evidence that L is frequent in the experiment’s outputs. Historical sources lack the matching denominator and prompt distribution.

## N and inference

- [Wilson (1927), *Probable Inference, the Law of Succession, and Statistical Inference*](https://doi.org/10.1080/01621459.1927.10502953): **read bibliographic record only**. It supplies a binomial interval method, not a universal sample-size rule.
- No read attractor paper licenses `N=10/cell` as confirmatory. Xu et al.’s 100-story / 20-alternative design shows recurrence claims ordinarily inspect substantially more generations, but it is not a power calculation for binary L incidence.
- `N >= 10/cell` should be treated as a pilot minimum. For rare L, Wilson intervals with ten trials are too wide for reliable “one-third” ratio decisions. Report counts, Wilson CIs, risk difference/ratio CIs; do not treat CI overlap as a formal difference test.
- Randomize order and preserve session/head identifiers. Add, prospectively, a matched human-writer baseline with the same prompts, languages, and L/T/Li/S coding; otherwise H0-base remains only indirectly tested.

## Recommendation on PREREG §5

**Do not alter the already preregistered five falsifiers.** They are better after r2: §5(5) directly blocks the main composite-object fallacy. Add only a future confirmatory amendment: larger precomputed N (or a predeclared sequential rule), effect-size CIs, and the matched human baseline. These additions increase evidentiary strength without replacing r2’s precommitted falsification rules.

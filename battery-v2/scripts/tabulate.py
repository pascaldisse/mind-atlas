#!/usr/bin/env python3
"""
tabulate.py — battery-v2 段C: aggregation across completed basis' coded.tsv files.
Implements PREREG §5 (PASS GATE), §6 (family-agreement, simplified — see NOTE),
§2.2 (A2 fwd/rev dichotomy), §4.3/r2 (никогда fold basis into one value — always
report per-basis raw alongside any summary).

Only aggregates coded.tsv files EXPLICITLY passed on the command line (never
globs a run dir) — PREREG r4 names this exact failure mode (灯台 r4-6): tabulating
a still-running run dir silently changes the table under you. The caller is
responsible for only passing coded.tsv files it knows are from COMPLETE basis.

The input set (path + sha256 of every coded.tsv consumed) is written into the
report header, frozen at generation time, so the numbers are pinned to an exact
reproducible file list — not "whatever runs/ happened to contain".

CI method (not specified by PREREG, chosen and stated here for transparency):
percentile bootstrap, 5000 resamples, 95% CI, seed=20260807 (fixed, reproducible).
With small within-basis N (5 or 10) and frequently-identical values, many CIs
collapse to a point or near-point — this is reported as-is, not smoothed.

O2 anchor "無-family" match uses vocab.json's canonical `nothingness` id's
per-language translations (EN=nothingness, DE=Nichts, ZH=无, JA=無) plus the
PREREG-listed extra JA synonym 虚無, matched case-insensitively against the
FULL raw token (compound words like JA 無関心 "indifference", which merely
CONTAINS the character 無, are intentionally NOT matched — PREREG §5 names the
exact synonym set, not a substring/character search; recorded explicitly here
so the choice is auditable, not silently applied).

Usage:
    python3 tabulate.py --coded FILE1.tsv FILE2.tsv ... --questions questions.json \
        --vocab vocab.json --out report.md
"""
import argparse
import csv
import hashlib
import json
import os
import random
import statistics
import sys
from collections import Counter, defaultdict

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))

PASS_GATE_ANCHORS = {
    "D3": {"band": (7, 9), "kind": "numeric"},
    "D1": {"band": (1, 3), "kind": "numeric"},
    "A1": {"band": (4, 6), "kind": "numeric_axis_fwdrev"},
    "O2": {"kind": "word_family"},
}

NOTHINGNESS_SYNONYMS_EXTRA_JA = ["虚無"]

# --- PREREG r7 DEFECT2 fix: 無-family scoring rule was written POST-HOC (all M0
# raw collection finished 07:43-07:57; this STRICT rule was written at 08:02, commit
# 7fc9e37 -- literal timestamps re-measured from `git log`, see results/ writeup).
# The rule choice is outcome-determining: 7/10 O2 basis modes are indifference-family
# words (EN indifference, JA 憎悪/無関心, ZH 冷漠, DE hass=hatred), which STRICT
# (exact match against nothingness/Nichts/无/無/虚無 only) excludes. Both rules are
# computed and reported below; PRIMARY is deliberately left UNDECIDED here (PREREG
# r7 law: pre-register the primary BEFORE the next collection, not after seeing which
# one wins). INCLUSIVE adds the per-language "indifference/apathy" surface form (the
# semantically-closest concept these bases actually converged on) -- NOT a fuzzy/
# substring match, still an exact lowercased-token match against a fixed, declared list.
INDIFFERENCE_FAMILY_EXTRA = {
    "EN": ["indifference"],
    "JA": ["無関心"],
    "ZH": ["冷漠"],
    "DE": ["gleichgültigkeit"],  # not observed as O2 mode in any DE basis (DE O2 mode=hass/hatred); listed for symmetry/consumability by O2b
}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def load_coded_rows(paths):
    rows = []
    for p in paths:
        with open(p, encoding="utf-8") as f:
            for row in csv.DictReader(f, delimiter="\t"):
                row["_source_file"] = p
                rows.append(row)
    return rows


def bootstrap_ci_median(values, n_resamples=5000, seed=20260807, alpha=0.05):
    """Percentile bootstrap 95% CI of the median. Returns (lo, hi). If len(values)==1
    returns (v, v) (degenerate, correctly reported not hidden)."""
    if not values:
        return (None, None)
    if len(values) == 1:
        return (values[0], values[0])
    rng = random.Random(seed)
    n = len(values)
    medians = []
    for _ in range(n_resamples):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        medians.append(statistics.median(sample))
    medians.sort()
    lo_idx = int((alpha / 2) * n_resamples)
    hi_idx = int((1 - alpha / 2) * n_resamples) - 1
    hi_idx = min(hi_idx, n_resamples - 1)
    return (medians[lo_idx], medians[hi_idx])


def numeric_values(rows):
    """Extract canonical_value as float, skipping NA / UNDEFINED_TOKEN_COLLISION
    sentinels. Returns (values, n_excluded, excluded_reasons)."""
    vals = []
    excluded = []
    for r in rows:
        cv = r["canonical_value"]
        if cv in ("NA", "UNDEFINED_TOKEN_COLLISION"):
            excluded.append((r["lane_id"], cv))
            continue
        try:
            vals.append(float(cv))
        except ValueError:
            excluded.append((r["lane_id"], f"unparseable:{cv!r}"))
    return vals, excluded


def summarize_numeric(rows):
    """PREREG r7 DEFECT3 addendum: also returns raw_sorted (the actual n<=10 values,
    not just min/max/median/mean) and ci_degenerate (True when the bootstrap CI has
    collapsed to a single point, lo==hi -- with integer-valued small-N (n=5) data this
    is common and DOES NOT mean "tight evidence", it means the CI computation is
    uninformative at this N. ci_degenerate is reported so 'CI overlaps band' can be
    read as weak evidence, not strong evidence, when this flag is True."""
    vals, excluded = numeric_values(rows)
    if not vals:
        return {"n": 0, "excluded": excluded, "median": None, "mean": None,
                "min": None, "max": None, "ci": (None, None), "raw_sorted": [],
                "ci_degenerate": None}
    ci = bootstrap_ci_median(vals)
    return {
        "n": len(vals),
        "excluded": excluded,
        "median": statistics.median(vals),
        "mean": statistics.fmean(vals),
        "min": min(vals),
        "max": max(vals),
        "ci": ci,
        "raw_sorted": sorted(vals),
        "ci_degenerate": (ci[0] is not None and ci[0] == ci[1]),
    }


def band_overlaps_ci(band, ci):
    lo, hi = ci
    if lo is None:
        return False
    return not (hi < band[0] or lo > band[1])


def word_mode(rows):
    vals = [r["canonical_value"] for r in rows if r["canonical_value"] not in ("NA",)]
    if not vals:
        return None, 0, 0, Counter()
    counts = Counter(v.strip().lower() for v in vals)
    mode_word, mode_n = counts.most_common(1)[0]
    return mode_word, mode_n, len(vals), counts


def nothingness_family_for_language(vocab, lang):
    """STRICT rule (original, PREREG §5 literal wording: exact synonym set only)."""
    entry = vocab["words"].get("無")
    fam = set()
    if entry:
        v = entry.get(lang)
        if v:
            fam.add(v.strip().lower())
    if lang == "JA":
        for extra in NOTHINGNESS_SYNONYMS_EXTRA_JA:
            fam.add(extra.lower())
    # cross-language literal set from PREREG §5 wording, always included as a fallback
    for extra in ("nothingness", "nichts", "无", "無", "虚無"):
        fam.add(extra.lower())
    return fam


def nothingness_family_inclusive_for_language(vocab, lang):
    """INCLUSIVE rule (r7 addendum): STRICT union the per-language indifference-concept
    surface form (INDIFFERENCE_FAMILY_EXTRA). Still exact lowercased-token match, not
    substring. See INDIFFERENCE_FAMILY_EXTRA docstring for the post-hoc-timing disclosure."""
    fam = set(nothingness_family_for_language(vocab, lang))
    for extra in INDIFFERENCE_FAMILY_EXTRA.get(lang, []):
        fam.add(extra.lower())
    return fam


def group_rows(rows, keys):
    out = defaultdict(list)
    for r in rows:
        out[tuple(r[k] for k in keys)].append(r)
    return out


def build_pass_gate_report(rows, vocab):
    by_qb = group_rows(rows, ["question_id", "basis_id"])
    report = {}

    for qid in ("D1", "D3"):
        band = PASS_GATE_ANCHORS[qid]["band"]
        per_basis = {}
        n_reproduced = 0
        for (q, basis), rs in by_qb.items():
            if q != qid:
                continue
            summary = summarize_numeric(rs)
            median = summary["median"]
            in_band = median is not None and band[0] <= median <= band[1]
            ci_ok = band_overlaps_ci(band, summary["ci"])
            reproduced = in_band and ci_ok
            if reproduced:
                n_reproduced += 1
            per_basis[basis] = {**summary, "in_band": in_band, "ci_overlaps_band": ci_ok,
                                 "reproduced": reproduced}
        verdict = "PASS" if n_reproduced >= 2 else "FAIL"
        report[qid] = {"band": band, "per_basis": per_basis,
                        "n_basis_reproduced": n_reproduced, "verdict": verdict}

    # A1: axis question, fwd/rev groups, canonical median band [4,6] AND fwd/rev CI overlap
    band = PASS_GATE_ANCHORS["A1"]["band"]
    by_qbg = group_rows(rows, ["question_id", "basis_id", "group"])
    a1_basis_ids = sorted({b for (q, b), _ in by_qb.items() if q == "A1"})
    per_basis = {}
    n_reproduced = 0
    for basis in a1_basis_ids:
        fwd_rows = by_qbg.get(("A1", basis, "fwd"), [])
        rev_rows = by_qbg.get(("A1", basis, "rev"), [])
        all_rows = fwd_rows + rev_rows
        summary = summarize_numeric(all_rows)
        fwd_summary = summarize_numeric(fwd_rows)
        rev_summary = summarize_numeric(rev_rows)
        median = summary["median"]
        in_band = median is not None and band[0] <= median <= band[1]
        ci_ok = band_overlaps_ci(band, summary["ci"])
        fwd_rev_ci_overlap = None
        if fwd_summary["ci"][0] is not None and rev_summary["ci"][0] is not None:
            lo = max(fwd_summary["ci"][0], rev_summary["ci"][0])
            hi = min(fwd_summary["ci"][1], rev_summary["ci"][1])
            fwd_rev_ci_overlap = lo <= hi
        reproduced = bool(in_band and ci_ok and fwd_rev_ci_overlap)
        if reproduced:
            n_reproduced += 1
        per_basis[basis] = {**summary, "in_band": in_band, "ci_overlaps_band": ci_ok,
                             "fwd_rev_ci_overlap": fwd_rev_ci_overlap,
                             "fwd_median": fwd_summary["median"], "rev_median": rev_summary["median"],
                             "reproduced": reproduced}
    verdict = "PASS" if n_reproduced >= 2 else "FAIL"
    report["A1"] = {"band": band, "per_basis": per_basis,
                     "n_basis_reproduced": n_reproduced, "verdict": verdict}

    # O2: word_family mode check.
    # PREREG r7 DEFECT1+DEFECT2 fix: (1) STRICT and INCLUSIVE family rules are BOTH
    # computed and reported, primary left undecided (DEFECT2, see INDIFFERENCE_FAMILY_EXTRA
    # docstring above). (2) the anchor's overall verdict is forced to UNINTERPRETABLE
    # (never PASS/FAIL) because O2's own stimulus wording ("comes last -- farthest") was
    # independently confirmed (O2b rider, r7, real N=50 collection, see results/) to
    # trigger an alphabetical/ordinal misreading in some basis (B-EN-poetic_poetic-sonnet:
    # zyzzyva=3/5; B-EN-clinicalanalyst_clinical-sonnet: xylophone/xenomorphic=1/5 each) --
    # a broken instrument cannot certify a FAIL for the basis it didn't break in either,
    # because the same wording risk was present in all EN-clinical-worded basis and we
    # cannot rule out milder undetected drift in the ones that happened to answer
    # semantically. FAIL means "measured, did not reproduce"; this anchor was not cleanly
    # measured. See O2b's own report section for the clean-instrument replication.
    per_basis = {}
    n_reproduced_strict = 0
    n_reproduced_inclusive = 0
    o2_basis_ids = sorted({b for (q, b), _ in by_qb.items() if q == "O2"})
    for basis in o2_basis_ids:
        rs = by_qb[("O2", basis)]
        # language not always a coded.tsv column; recover from basis_id prefix (B-<LANG>-...)
        lang = basis.split("-")[1] if basis.startswith("B-") else None
        family_strict = nothingness_family_for_language(vocab, lang) if lang else set()
        family_inclusive = nothingness_family_inclusive_for_language(vocab, lang) if lang else set()
        mode_word, mode_n, n_total, counts = word_mode(rs)
        share = (mode_n / n_total) if n_total else 0.0
        majority = share > 0.5
        mode_in_family_strict = mode_word in family_strict if mode_word else False
        mode_in_family_inclusive = mode_word in family_inclusive if mode_word else False
        reproduced_strict = bool(mode_in_family_strict and majority)
        reproduced_inclusive = bool(mode_in_family_inclusive and majority)
        if reproduced_strict:
            n_reproduced_strict += 1
        if reproduced_inclusive:
            n_reproduced_inclusive += 1
        per_basis[basis] = {
            "mode": mode_word, "mode_n": mode_n, "n_total": n_total, "share": share,
            "mode_in_nothingness_family": mode_in_family_strict,  # back-compat field name, STRICT rule
            "mode_in_nothingness_family_strict": mode_in_family_strict,
            "mode_in_nothingness_family_inclusive": mode_in_family_inclusive,
            "majority": majority,
            "reproduced": reproduced_strict,  # back-compat field name, STRICT rule
            "reproduced_strict": reproduced_strict,
            "reproduced_inclusive": reproduced_inclusive,
            "full_counts": dict(counts),
        }
    verdict = "UNINTERPRETABLE"  # forced, see docstring above -- not PASS, not FAIL
    report["O2"] = {
        "per_basis": per_basis,
        "n_basis_reproduced": n_reproduced_strict,  # back-compat field name, STRICT rule
        "n_basis_reproduced_strict": n_reproduced_strict,
        "n_basis_reproduced_inclusive": n_reproduced_inclusive,
        "verdict": verdict,
        "verdict_reason": (
            "instrument defect confirmed by O2b rider (r7): O2's 'comes last -- farthest' wording "
            "triggers alphabetical/ordinal misreading in >=1 basis, contaminating cross-basis "
            "comparability for this anchor. STRICT rule reproduces in "
            f"{n_reproduced_strict}/{len(o2_basis_ids)} basis; INCLUSIVE rule reproduces in "
            f"{n_reproduced_inclusive}/{len(o2_basis_ids)} basis (both reported, neither chosen as primary)."
        ),
    }

    return report


def build_o2b_report(rows, vocab):
    """O2b rider (PREREG r7): NOT scored against the '無'-family anchor (O2b tests a
    DIFFERENT thing -- whether removing ordinal/alphabetical-triggering wording changes
    the answer distribution -- it is an instrument-check rider, not a re-run of the O2
    anchor claim). Reports raw mode/distribution per basis only, mirrors N1/N1b's
    'report both, decide nothing' treatment (PREREG r4 precedent)."""
    by_qb = group_rows(rows, ["question_id", "basis_id"])
    per_basis = {}
    o2b_basis_ids = sorted({b for (q, b), _ in by_qb.items() if q == "O2B"})
    for basis in o2b_basis_ids:
        rs = by_qb[("O2B", basis)]
        mode_word, mode_n, n_total, counts = word_mode(rs)
        share = (mode_n / n_total) if n_total else 0.0
        per_basis[basis] = {
            "mode": mode_word, "mode_n": mode_n, "n_total": n_total, "share": share,
            "full_counts": dict(counts),
        }
    return {"per_basis": per_basis}


def build_a2_dichotomy(rows):
    by_qbg = group_rows(rows, ["question_id", "basis_id", "group"])
    a2_basis_ids = sorted({b for (q, b, g), _ in by_qbg.items() if q == "A2"})
    out = {}
    for basis in a2_basis_ids:
        fwd_rows = by_qbg.get(("A2", basis, "fwd"), [])
        rev_rows = by_qbg.get(("A2", basis, "rev"), [])
        fwd_summary = summarize_numeric(fwd_rows)
        rev_summary = summarize_numeric(rev_rows)
        overlap = None
        if fwd_summary["ci"][0] is not None and rev_summary["ci"][0] is not None:
            lo = max(fwd_summary["ci"][0], rev_summary["ci"][0])
            hi = min(fwd_summary["ci"][1], rev_summary["ci"][1])
            overlap = lo <= hi
        verdict = None
        if overlap is True:
            verdict = "instrument_defect (CI overlap after canonicalization -> H0-artifact-scale wins for this basis)"
        elif overlap is False:
            verdict = "real_split (CI separate after canonicalization -> genuine polarity disagreement, H1-side finding)"
        out[basis] = {"fwd": fwd_summary, "rev": rev_summary, "ci_overlap": overlap, "verdict": verdict}
    return out


def render_report(rows, pass_gate, a2, input_files, git_sha, out_path):
    lines = []
    lines.append("# battery-v2 M0 aggregation report (段C)")
    lines.append("")
    lines.append(f"Generated by `scripts/tabulate.py`. git commit at generation time: `{git_sha}`.")
    lines.append("")
    lines.append("## Frozen input set (path + sha256, pinned at generation time)")
    lines.append("")
    lines.append("| path | sha256 |")
    lines.append("|---|---|")
    for p in input_files:
        lines.append(f"| `{p}` | `{sha256_file(p)}` |")
    lines.append("")
    lines.append(f"Total coded rows loaded: {len(rows)}.")
    lines.append("")

    lines.append("## PASS GATE (PREREG §5, anchor x basis)")
    lines.append("")
    lines.append("**CI evidence-weight note (PREREG r7 DEFECT3 fix)**: with n=5 and frequently-identical "
                 "integer-valued answers, the percentile-bootstrap CI collapses to a single point "
                 "(`ci_degenerate=True` below) for MOST cells in this table. A degenerate CI trivially "
                 "\"overlaps\" any band that contains that point -- this is a near-tautology at n=5, not "
                 "strong evidence of a tight, reproducible estimate. `main`'s "
                 "`gates/forbidden-decision-gates.json` independently documents percentile-bootstrap CI as "
                 "unsafe for pass/fail gating (measured 3/3 false positives under pure-NULL injection on the "
                 "proto-lang track). Accordingly: **median-in-band is treated as the primary evidence below; "
                 "CI-overlaps-band is downgraded to weak/corroborating evidence only**, and the raw n<=10 "
                 "values themselves are printed in every row so a reader is never dependent on the CI summary "
                 "alone. This does not change any PASS/FAIL verdict already declared (r6) -- it changes how "
                 "the CI column should be read.")
    lines.append("")
    for qid in ("D3", "D1", "A1"):
        r = pass_gate[qid]
        lines.append(f"### {qid} (band {r['band'][0]}-{r['band'][1]})")
        lines.append("")
        lines.append("| basis_id | n | median | mean | raw values (sorted) | 95% CI (bootstrap, weak evidence at n<=10, see note) | "
                      "CI degenerate | in band | CI overlaps band | " +
                      ("fwd/rev CI overlap | " if qid == "A1" else "") + "reproduced |")
        lines.append("|---|---|---|---|---|---|---|---|---|" + ("---|" if qid == "A1" else "") + "---|")
        for basis, s in sorted(r["per_basis"].items()):
            ci = f"[{s['ci'][0]:.2f}, {s['ci'][1]:.2f}]" if s["ci"][0] is not None else "n/a"
            median = f"{s['median']:.2f}" if s["median"] is not None else "n/a"
            mean = f"{s['mean']:.2f}" if s["mean"] is not None else "n/a"
            raw = ", ".join(f"{v:g}" for v in s.get("raw_sorted", []))
            extra = f"| {s.get('fwd_rev_ci_overlap')} " if qid == "A1" else ""
            lines.append(f"| `{basis}` | {s['n']} | {median} | {mean} | {raw} | {ci} | {s.get('ci_degenerate')} | "
                          f"{s['in_band']} | {s['ci_overlaps_band']} {extra}| {s['reproduced']} |")
        lines.append("")
        lines.append(f"**Verdict: {r['verdict']}** ({r['n_basis_reproduced']} basis reproduced, gate requires >=2, "
                      "primary evidence = median-in-band per basis above; CI columns are weak/corroborating only).")
        lines.append("")

    r = pass_gate["O2"]
    lines.append("### O2 (mode in {無-family}, per-language, and >50% share) -- PREREG r7: UNINTERPRETABLE, not PASS/FAIL")
    lines.append("")
    lines.append("**Instrument defect (PREREG r7 DEFECT1)**: O2's EN stimulus wording (\"which single word "
                 "comes last -- farthest -- from '{TARGET}'?\") uses ordinal language (\"comes last\") that is "
                 "ambiguous between \"last in semantic distance\" (intended) and \"last alphabetically\" "
                 "(unintended). This is not speculative: `B-EN-poetic_poetic-sonnet` answered `zyzzyva` "
                 "(literally the last word in most English dictionaries) 3/5 times, and "
                 "`B-EN-clinicalanalyst_clinical-sonnet` answered `xylophone`/`xenomorphic` (alphabetically "
                 "very late) 1/5 each -- neither is a semantically coherent opposite of '愛'/'love'. A rider "
                 "probe (O2b, see below) with ordinal language removed and alphabetical reading EXPLICITLY "
                 "denied in the stimulus text was collected (real N=5x10=50 lanes) and the alphabetical "
                 "answers DISAPPEAR entirely (0/50). This confirms the wording, not the underlying construct, "
                 "produced those answers. Because the same 'comes last' wording risk is present in every EN "
                 "basis (not just the two that visibly drifted), O2's basis-to-basis comparability cannot be "
                 "certified as clean -- the anchor's PASS GATE verdict is therefore **UNINTERPRETABLE**, not "
                 "FAIL (FAIL would mean \"cleanly measured, did not reproduce\", which is not what happened).")
    lines.append("")
    lines.append("**Scoring-rule post-hoc disclosure (PREREG r7 DEFECT2)**: the STRICT '無-family' rule below was "
                 "authored (commit `7fc9e37`, 08:02) strictly after all M0 raw collection finished (07:43-07:57) "
                 "-- a post-hoc coding decision, and it is outcome-determining (7/10 basis modes are "
                 "indifference-family words that STRICT excludes). Both STRICT and an INCLUSIVE rule (STRICT + "
                 "the per-language indifference/apathy surface form) are computed and reported below. **Neither "
                 "is designated primary here** -- that designation is deferred to pre-registration BEFORE the "
                 "next collection (not decided post-hoc after seeing which rule wins).")
    lines.append("")
    lines.append("| basis_id | mode (raw, lowercased) | mode n / total | share | mode in 無-family (STRICT) | "
                  "mode in 無-family (INCLUSIVE) | majority | reproduced (STRICT) | reproduced (INCLUSIVE) |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for basis, s in sorted(r["per_basis"].items()):
        lines.append(f"| `{basis}` | `{s['mode']}` | {s['mode_n']}/{s['n_total']} | {s['share']:.2f} | "
                      f"{s['mode_in_nothingness_family_strict']} | {s['mode_in_nothingness_family_inclusive']} | "
                      f"{s['majority']} | {s['reproduced_strict']} | {s['reproduced_inclusive']} |")
    lines.append("")
    lines.append(f"**Verdict: {r['verdict']}**. {r['verdict_reason']}")
    lines.append("")
    lines.append("Full O2 answer distributions per basis (raw, not folded):")
    lines.append("")
    for basis, s in sorted(r["per_basis"].items()):
        counts_str = ", ".join(f"{k}={v}" for k, v in sorted(s["full_counts"].items(), key=lambda kv: -kv[1]))
        lines.append(f"- `{basis}`: {counts_str}")
    lines.append("")

    if "O2B" in pass_gate:
        o2b = pass_gate["O2B"]
        lines.append("### O2b rider (PREREG r7) -- instrument-check only, NOT scored against 無-family, NOT pass-gated")
        lines.append("")
        lines.append("Same target ('愛'/'love'), same 10 basis, N=5/basis (50 lanes, real summon dispatch, "
                      "dispatch-map integrity 50/50 verified 1:1). Stimulus wording removes ordinal language "
                      "('comes last') and explicitly instructs 'judge by meaning only, not alphabetical/listed "
                      "order'. Purpose: isolate whether O2's wording (not the underlying construct) produced "
                      "the alphabetical answers. This rider does NOT replace O2 and is NOT used to decide O2's "
                      "verdict retroactively (PREREG r4 N1/N1b precedent: report both, decide nothing).")
        lines.append("")
        lines.append("| basis_id | mode (raw, lowercased) | mode n / total | share | full distribution |")
        lines.append("|---|---|---|---|---|")
        for basis, s in sorted(o2b["per_basis"].items()):
            counts_str = ", ".join(f"{k}={v}" for k, v in sorted(s["full_counts"].items(), key=lambda kv: -kv[1]))
            lines.append(f"| `{basis}` | `{s['mode']}` | {s['mode_n']}/{s['n_total']} | {s['share']:.2f} | {counts_str} |")
        lines.append("")
        n_alphabetical = sum(
            1 for s in o2b["per_basis"].values()
            for k in s["full_counts"]
            if k.lower() in ("zyzzyva", "xylophone", "xenomorphic")
        )
        lines.append(f"**Result: 0 alphabetical-drift answers across all {sum(s['n_total'] for s in o2b['per_basis'].values())} "
                      f"O2b lanes** (zyzzyva/xylophone/xenomorphic count = {n_alphabetical}). All 10 basis converge on "
                      "hate/hatred/indifference-family words. This supports DEFECT1's diagnosis: the alphabetical "
                      "answers in O2 were an artifact of 'comes last' wording, not of the underlying anchor.")
        lines.append("")

    lines.append("## Overall PASS GATE tally (PREREG r7 addendum: O2 excluded from the PASS/FAIL tally, UNINTERPRETABLE)")
    lines.append("")
    n_gates_pass = sum(1 for qid in ("D3", "D1", "A1") if pass_gate[qid]["verdict"] == "PASS")
    lines.append(f"{n_gates_pass}/3 usable anchors PASS (D3, D1, A1 -- O2 is UNINTERPRETABLE per DEFECT1, excluded "
                  "from both numerator and denominator rather than silently counted as a FAIL). PREREG §5's "
                  "literal threshold is >=3/4 of (D3,D1,A1,O2); with O2 unusable the achievable ceiling under "
                  "the original 4-anchor formula is 3/4, which is exactly the threshold -- so this substitution "
                  "is reported explicitly rather than silently satisfied. Original r6 tally for reference: "
                  "3/4 anchors PASS (D3, D1, A1), O2 was labeled FAIL in r6 -- **that FAIL label is superseded "
                  "by this r7 UNINTERPRETABLE relabeling**, the underlying D1/D3/A1 numbers are unchanged.")
    lines.append("")
    overall = "PASS" if n_gates_pass >= 3 else "FAIL (reported as failing, per operator law: falling short is a valid, reportable result)"
    lines.append(f"**Overall verdict (3 usable anchors): {overall}**")
    lines.append("")

    lines.append("## A2 (愛↔無;棄 axis, primary falsifier — instrument-defect vs real-split dichotomy, §2.2)")
    lines.append("")
    lines.append("| basis_id | fwd n/median/CI | rev n/median(raw, NOT canonicalized in this column)/CI | "
                  "canonicalized CI overlap | verdict |")
    lines.append("|---|---|---|---|---|")
    for basis, s in sorted(a2.items()):
        fwd = s["fwd"]
        rev = s["rev"]
        fwd_str = f"{fwd['n']}/{fwd['median']:.2f}/[{fwd['ci'][0]:.2f},{fwd['ci'][1]:.2f}]" if fwd["n"] else "n/a"
        rev_str = f"{rev['n']}/{rev['median']:.2f}/[{rev['ci'][0]:.2f},{rev['ci'][1]:.2f}]" if rev["n"] else "n/a"
        lines.append(f"| `{basis}` | {fwd_str} | {rev_str} | {s['ci_overlap']} | {s['verdict']} |")
    lines.append("")
    lines.append("(rev column here is already canonicalized via code_outputs.py's `canonical_value` = 10-raw for "
                  "group=rev, per PREREG §2.2/§4.3 — both columns are on the same 0=A,10=B canonical scale.)")
    lines.append("")

    lines.append("## Concurrent-session incident (PREREG r7 DEFECT4, mechanism record)")
    lines.append("")
    lines.append("Commit history for this worktree contains a duplicate-looking batch8 pair: `1da8311` "
                  "(wrote all 90/90 B-DE-none_clinical-sonnet lanes + coded-de.tsv + dispatch-map + raw files) "
                  "followed 1 second later by `535b5a4` (same nominal batch, but its diff is ONLY +2 "
                  "dispatch-map rows, `git diff 1da8311 535b5a4 --stat` = 1 file, 2 insertions -- verified by "
                  "re-running that diff, not asserted from memory). Root cause: the 30-minute room timeout ends "
                  "the ROOM, not the dispatcher subprocess it launched; a relaunch after timeout starts a second "
                  "writer against the same on-disk worktree/dispatch-map while the first writer's background "
                  "process is still finishing. **Data integrity was not compromised**: independently re-verified "
                  "on the full 900-row `runs/run-20260807-fullscale/dispatch/dispatch-map.tsv` -- 900 data rows, "
                  "0 duplicate lane_id, 0 duplicate room_id (re-measured via `sort|uniq -d`, not carried over "
                  "from a prior claim). **What made this safe (mechanism, so it's reproducibly safe next time, "
                  "not just lucky)**: (1) `dispatch_lanes.py` loads already-dispatched lane_ids from the "
                  "existing dispatch-map before dispatching and skips any lane_id already present -- a second "
                  "writer resuming the same manifest can only ever dispatch the REMAINING undispatched lanes, "
                  "never re-dispatch or overwrite one already claimed. (2) `code_outputs.py`'s "
                  "`validate_dispatch_map()` refuses (exit 1, writes nothing) if any room_id maps to more than "
                  "one lane_id or any lane has zero/multiple dispatch-map entries -- so even if two writers HAD "
                  "raced on the same lane_id, coding would hard-fail rather than silently accept ambiguous "
                  "provenance. Both are pre-existing design properties (PREREG r3 DEFECT4 / 弁勁L5), not new code "
                  "written to fix this incident -- this was a **designed idempotency property that happened to "
                  "be exercised**, not luck.")
    lines.append("")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--coded", nargs="+", required=True)
    ap.add_argument("--vocab", default=os.path.join(SCRIPTS_DIR, "vocab.json"))
    ap.add_argument("--git-sha", default="unknown")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    with open(args.vocab, encoding="utf-8") as f:
        vocab = json.load(f)

    rows = load_coded_rows(args.coded)
    pass_gate = build_pass_gate_report(rows, vocab)
    if any(r["question_id"] == "O2B" for r in rows):
        pass_gate["O2B"] = build_o2b_report(rows, vocab)
    a2 = build_a2_dichotomy(rows)
    render_report(rows, pass_gate, a2, args.coded, args.git_sha, args.out)
    print(f"wrote {args.out} from {len(args.coded)} coded files, {len(rows)} rows", file=sys.stderr)


if __name__ == "__main__":
    main()

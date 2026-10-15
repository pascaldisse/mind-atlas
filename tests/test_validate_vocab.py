#!/usr/bin/env python3
"""Fixture tests for scripts/validate_vocab.py's mechanical checks.

Each test builds an isolated fixture repo (vocab/*.json + vocab.json) under
a scratch directory *inside the repo* (never /tmp -- see .scratch/ in
.gitignore) and runs validate_vocab.main() against it via --root, asserting
the expected checks fire (or don't).

Several fixtures use real entries copied verbatim from this repo's own
vocab.json (the de-collision cluster around Nebel/Opfer/Leere/Zuneigung,
and the real de==en planet-name entries) rather than only synthetic
data, per lane law: satisfying self-authored fixtures alone has no
external validity.

Collision semantics (lane law, post scope-change): a token collision
(two ids sharing one language-column token) is a LEXICAL FACT, not a
violation -- German/Chinese genuinely lack a distinguishing word for some
concept pairs. The violation is an *unannotated* collision: build_vocab.py
must attach a `token_collision` field, and validate_vocab.py checks that
field against an independently recomputed ground truth.
"""
import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRATCH = ROOT / ".scratch" / "test_validate_vocab"
sys.path.insert(0, str(ROOT / "scripts"))
import build_vocab  # noqa: E402


def base_entry(**overrides):
    e = {
        "id": "placeholder",
        "ja": "仮",
        "en": "placeholder",
        "de": "Platzhalter",
        "zh": "占位符",
        "domain": "cosmology",
        "layer": 1,
        "v1_anchor": False,
        "embed_en": True,
        "notes": "",
    }
    e.update(overrides)
    return e


def write_fixture_repo(name, domain_files):
    """domain_files: dict[str, list[entry]] -> writes vocab/<name>.json each,
    then regenerates a matching vocab.json via build_vocab.build_merged
    (this also attaches token_collision) so the repo is self-consistent by
    default. Returns the repo root Path."""
    repo = SCRATCH / name
    if repo.exists():
        shutil.rmtree(repo)
    vocab_dir = repo / "vocab"
    vocab_dir.mkdir(parents=True)
    for domain, entries in domain_files.items():
        (vocab_dir / f"{domain}.json").write_text(
            json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    merged, _ = build_vocab.build_merged(vocab_dir)
    (repo / "vocab.json").write_text(
        json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return repo


def run_validator(repo):
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/validate_vocab.py"), "--root", str(repo)],
        text=True,
        capture_output=True,
    )
    return proc.returncode, proc.stdout, proc.stderr


class ValidateVocabFixtures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        SCRATCH.mkdir(parents=True, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        if SCRATCH.exists():
            shutil.rmtree(SCRATCH)

    def test_clean_fixture_passes(self):
        entries = [
            base_entry(id="sky", ja="空", en="sky", de="Himmel", zh="天空"),
            base_entry(id="star", ja="星", en="star", de="Stern", zh="星星"),
            base_entry(
                id="no_de_word",
                ja="侘寂",
                en="wabi-sabi",
                de=None,
                zh=None,
                notes="no single German/Chinese lexeme; periphrastic only",
            ),
        ]
        repo = write_fixture_repo("clean", {"cosmology": entries})
        code, out, err = run_validator(repo)
        self.assertEqual(code, 0, msg=f"stdout={out}\nstderr={err}")
        self.assertIn("OK: no violations", out)
        self.assertIn("species=0", out)

    def test_real_de_duplicate_cluster_is_annotated_not_a_violation(self):
        # Verbatim from this repo's vocab.json (git show HEAD:vocab.json),
        # the exact Nebel/Opfer/Leere/Zuneigung cluster the audit found.
        # A collision alone must NOT fail validation once build_vocab.py
        # has annotated it -- these are real lexical facts, not defects.
        entries = [
            base_entry(id="fog", ja="霧", en="fog", de="Nebel", zh="雾"),
            base_entry(
                id="nebula", ja="星雲", en="nebula", de="Nebel", zh="星云",
                notes="German 'Nebel' is the standard astronomical term, "
                "same lexeme as weather 'fog/mist'",
            ),
            base_entry(
                id="offering_religious", ja="供物", en="offering", de="Opfer",
                zh="供品",
                notes="German 'Opfer' covers both religious offering and "
                "sacrifice/victim; same word reused at id=sacrifice_religious",
            ),
            base_entry(
                id="sacrifice_religious", ja="犠牲", en="sacrifice", de="Opfer",
                zh="牺牲",
            ),
            base_entry(
                id="victim", ja="被害者", en="victim", de="Opfer", zh="受害者",
                domain="relations",
                notes="German shared with id=offering_religious/"
                "sacrifice_religious; real polysemy",
            ),
            base_entry(id="void", ja="虚空", en="void", de="Leere", zh="虚空", layer=2),
            base_entry(
                id="emptiness_emotional", ja="空虚", en="emptiness", de="Leere",
                zh="空虚", domain="emotion",
                notes="German shares 'Leere' with the cosmological id=void; "
                "same underlying concept, different register",
            ),
            base_entry(
                id="affection", ja="愛情", en="affection", de="Zuneigung",
                zh="爱意", domain="emotion",
            ),
            base_entry(
                id="fondness", ja="好意", en="fondness", de="Zuneigung",
                zh="好感", domain="emotion",
            ),
        ]
        repo = write_fixture_repo("real-de-dup", {"cosmology": entries})
        code, out, err = run_validator(repo)
        self.assertEqual(code, 0, msg=f"stdout={out}\nstderr={err}")
        self.assertIn("OK: no violations", out)
        # audit summary must still surface the real numbers (informational)
        self.assertIn("species=4", out)  # Nebel, Opfer, Leere, Zuneigung
        self.assertIn("affected=9", out)  # 2+3+2+2
        self.assertIn("surplus=5", out)  # 9-4
        # and build_vocab really did attach the annotation
        vocab = json.loads((repo / "vocab.json").read_text(encoding="utf-8"))
        by_id = {e["id"]: e for e in vocab}
        self.assertEqual(
            by_id["offering_religious"]["token_collision"],
            {"de": ["offering_religious", "sacrifice_religious", "victim"]},
        )

    def test_missing_collision_annotation_fires(self):
        # Same real collision, but simulate a stale/hand-edited vocab.json
        # where the annotation was stripped after the fact.
        entries = [
            base_entry(id="fog3", ja="霧3", en="fog3", de="Nebel3", zh="雾3"),
            base_entry(id="nebula3", ja="星雲3", en="nebula3", de="Nebel3", zh="星云3"),
        ]
        repo = write_fixture_repo("missing-annotation", {"cosmology": entries})
        vocab_path = repo / "vocab.json"
        vocab = json.loads(vocab_path.read_text(encoding="utf-8"))
        for e in vocab:
            if e["id"] == "fog3":
                e["token_collision"] = None  # simulate stripped/stale annotation
        vocab_path.write_text(json.dumps(vocab, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        code, out, err = run_validator(repo)
        self.assertEqual(code, 1)
        self.assertIn("id 'fog3': token_collision is None, expected", err)
        self.assertIn("run scripts/build_vocab.py", err)

    def test_null_heavy_fixture_does_not_move_dup_metric(self):
        # 40 entries, all de/zh null with justifying notes, zero duplicates.
        entries = [
            base_entry(
                id=f"null_case_{i}", ja=f"仮{i}", en=f"placeholder{i}",
                de=None, zh=None,
                notes="no attested lexeme in either language; periphrastic only",
            )
            for i in range(40)
        ]
        repo = write_fixture_repo("null-heavy", {"cosmology": entries})
        code, out, err = run_validator(repo)
        self.assertEqual(code, 0, msg=f"stdout={out}\nstderr={err}")
        self.assertIn("de: null=40  species=0  affected=0  surplus=0", out)
        self.assertIn("zh: null=40  species=0  affected=0  surplus=0", out)

    def test_null_count_does_not_move_real_duplicate_metric(self):
        # Mix: 2 real de-duplicate entries + 40 unrelated null entries.
        # The audit must report species=1/affected=2/surplus=1 regardless
        # of how many nulls are also present (the failure mode the audit
        # actually hit: null count leaking into the duplicate count).
        # Both are validly annotated by build_vocab, so exit code is 0.
        dup_entries = [
            base_entry(id="fog2", ja="霧2", en="fog2", de="Nebel2", zh="雾2"),
            base_entry(id="nebula2", ja="星雲2", en="nebula2", de="Nebel2", zh="星云2"),
        ]
        null_entries = [
            base_entry(
                id=f"null_mix_{i}", ja=f"仮{i}", en=f"ph{i}", de=None, zh=None,
                notes="no attested lexeme",
            )
            for i in range(40)
        ]
        repo = write_fixture_repo("mixed-null-and-dup", {"cosmology": dup_entries + null_entries})
        code, out, err = run_validator(repo)
        self.assertEqual(code, 0, msg=f"stdout={out}\nstderr={err}")
        self.assertIn("de: null=40  species=1  affected=2  surplus=1", out)

    def test_real_de_eq_en_allowlisted_planets_pass(self):
        # Verbatim from this repo: 3 of the 7 known de==en entries. These are
        # ALLOWLISTED (international/proper-noun astronomical names), so the
        # check must NOT fire. Operator decision 3, 2026-08-06.
        entries = [
            base_entry(id="jupiter_planet", ja="木星", en="Jupiter", de="Jupiter", zh="木星"),
            base_entry(id="mars_planet", ja="火星", en="Mars", de="Mars", zh="火星"),
            base_entry(id="venus_planet", ja="金星", en="Venus", de="Venus", zh="金星"),
        ]
        repo = write_fixture_repo("de-eq-en-allowlisted", {"cosmology": entries})
        code, out, err = run_validator(repo)
        self.assertEqual(code, 0, msg=f"stdout={out}\nstderr={err}")

    def test_de_eq_en_outside_allowlist_fires(self):
        # Same shape, ids NOT on the allowlist -> must fire. This is the half
        # of the contract the allowlist must never swallow. (Real German/English
        # identical lexemes; ids are not in DE_EN_IDENTICAL_ALLOWLIST.)
        entries = [
            base_entry(id="hotel_daily", ja="ホテル", en="Hotel", de="Hotel", zh="酒店"),
            base_entry(id="radio_daily", ja="ラジオ", en="Radio", de="Radio", zh="收音机"),
        ]
        repo = write_fixture_repo("de-eq-en-not-allowlisted", {"daily": entries})
        code, out, err = run_validator(repo)
        self.assertEqual(code, 1)
        self.assertIn("id 'hotel_daily': de == en == 'Hotel'", err)
        self.assertIn("id 'radio_daily': de == en == 'Radio'", err)

    def test_real_bracket_slash_notation_fires(self):
        # Verbatim from this repo: en parenthetical-context entries and a
        # de gender-suffix entry, exactly the pattern the audit found (64
        # en + 21 de real cases).
        entries = [
            base_entry(id="balance_design", ja="バランス", en="balance (design)",
                       de="Balance", zh="平衡",
                       notes="disambiguated id, design-aesthetic sense"),
            base_entry(id="acquaintance", ja="知人", en="acquaintance",
                       de="Bekannte(r)", zh="熟人", domain="relations"),
            base_entry(id="apology_daily", ja="すみません", en="excuse me / sorry",
                       de="Entschuldigung", zh="不好意思", domain="daily",
                       notes="disambiguated id, everyday-politeness sense"),
        ]
        repo = write_fixture_repo("bracket-slash", {"cosmology": entries[:1],
                                                      "relations": entries[1:2],
                                                      "daily": entries[2:3]})
        code, out, err = run_validator(repo)
        self.assertEqual(code, 1)
        self.assertIn(
            "id 'balance_design': en token 'balance (design)' contains "
            "'(' ')' or '/'", err,
        )
        self.assertIn(
            "id 'acquaintance': de token 'Bekannte(r)' contains "
            "'(' ')' or '/'", err,
        )
        self.assertIn(
            "id 'apology_daily': en token 'excuse me / sorry' contains "
            "'(' ')' or '/'", err,
        )

    def test_zh_traditional_contamination_fires(self):
        # 愛 is a real, ICU-attested Traditional form of Simplified 爱
        # (proven: StringTransform 'Traditional-Simplified' changes it).
        # zh should never hold Traditional forms in this vocab.
        entries = [
            base_entry(id="love_bad", ja="愛", en="love", de="Liebe", zh="愛"),
            base_entry(id="love_ok", ja="愛情", en="affection2", de="Zuneigung2", zh="爱意2"),
        ]
        repo = write_fixture_repo("zh-traditional", {"emotion": entries})
        code, out, err = run_validator(repo)
        self.assertEqual(code, 1)
        self.assertIn(
            "zh field '愛' (ids ['love_bad']) contains Traditional-only forms; "
            "ICU Traditional-Simplified transform yields '爱'", err,
        )
        self.assertNotIn("爱意2", err)  # already-Simplified entry must not fire

    def test_zh_ja_same_form_is_not_flagged(self):
        # zh == ja is explicitly NOT a violation (audited separately,
        # DEFECT 0 across 211 real cases) -- must not regress into a
        # false positive.
        entries = [
            base_entry(id="light", ja="光", en="light", de="Licht", zh="光"),
            base_entry(id="mother", ja="母", en="mother", de="Mutter", zh="母"),
        ]
        repo = write_fixture_repo("zh-eq-ja", {"cosmology": entries})
        code, out, err = run_validator(repo)
        self.assertEqual(code, 0, msg=f"stdout={out}\nstderr={err}")

    def test_embed_en_truthiness_antipattern_fires(self):
        repo = write_fixture_repo(
            "embed-truthy",
            {"cosmology": [base_entry(id="sky4", ja="空4", en="sky4", de="Himmel4", zh="天空4")]},
        )
        (repo / "scripts").mkdir(parents=True)
        (repo / "scripts" / "consumer.py").write_text(
            'def coverage(entries):\n'
            '    return sum(1 for e in entries if not e["embed_en"])\n',
            encoding="utf-8",
        )
        code, out, err = run_validator(repo)
        self.assertEqual(code, 1)
        self.assertIn("truthy check on embed_en without an explicit", err)
        self.assertIn("consumer.py:2:", err)

    def test_embed_en_explicit_comparison_does_not_fire(self):
        repo = write_fixture_repo(
            "embed-explicit",
            {"cosmology": [base_entry(id="sky5", ja="空5", en="sky5", de="Himmel5", zh="天空5")]},
        )
        (repo / "scripts").mkdir(parents=True)
        (repo / "scripts" / "consumer.py").write_text(
            'def coverage(entries):\n'
            '    return sum(1 for e in entries if e["embed_en"] is True)\n',
            encoding="utf-8",
        )
        code, out, err = run_validator(repo)
        self.assertEqual(code, 0, msg=f"stdout={out}\nstderr={err}")

    def test_stale_vocab_json_fires(self):
        entries = [base_entry(id="sky2", ja="空2", en="sky2", de="Himmel2", zh="天空2")]
        repo = write_fixture_repo("stale", {"cosmology": entries})
        # Corrupt the committed vocab.json so it no longer matches the
        # freshly-merged vocab/*.json sources (drop the one entry).
        (repo / "vocab.json").write_text("[]\n", encoding="utf-8")
        code, out, err = run_validator(repo)
        self.assertEqual(code, 1)
        self.assertIn("vocab.json is STALE relative to vocab/*.json", err)
        self.assertIn("sources have 1 entries, vocab.json has 0", err)

    def test_fresh_vocab_json_is_not_stale(self):
        entries = [base_entry(id="sky3", ja="空3", en="sky3", de="Himmel3", zh="天空3")]
        repo = write_fixture_repo("fresh", {"cosmology": entries})
        code, out, err = run_validator(repo)
        self.assertEqual(code, 0, msg=f"stdout={out}\nstderr={err}")


if __name__ == "__main__":
    unittest.main()

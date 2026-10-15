#!/usr/bin/env python3
"""
battery-v2 harness fixture test. 実trialは含まない(PREREG committed後もcollection未開始)。
自作短文のみを使い、emit_prompts/code_outputsの機械部分(パース・正準化・pole割当・件数)
を検証する。全件PASSしないと harness を「動く」と主張しない。
"""
import csv
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "..", "scripts")
sys.path.insert(0, SCRIPTS)

import emit_prompts  # noqa: E402
import code_outputs  # noqa: E402
import harvest_rooms  # noqa: E402
import dispatch_lanes  # noqa: E402
import tabulate as bv2_tabulate  # noqa: E402  (avoid shadowing stdlib-adjacent name)


class TestEmitCounts(unittest.TestCase):
    def setUp(self):
        self.vocab = {
            "words": {
                "A": {"EN": "alpha", "DE": "Alpha", "JA": "アルファ", "ZH": "阿尔法"},
                "B": {"EN": "beta", "DE": "Beta", "JA": "ベータ", "ZH": "贝塔"},
                "M": {"EN": "mid", "DE": "Mitte", "JA": "ミッド", "ZH": "中"},
            }
        }
        self.basis_list = [
            {"id": "B-EN-none_clinical-sonnet", "language": "EN", "pf": "none+clinical", "head": "claude-sonnet"},
        ]

    def test_distance_reps(self):
        q = [{"id": "D1", "type": "distance", "pair": ["A", "B"], "reps": 5}]
        rows = emit_prompts.emit_rows(q, self.basis_list, self.vocab)
        self.assertEqual(len(rows), 5)
        self.assertTrue(all(r["group"] == "na" for r in rows))
        self.assertTrue(all(r["answer_format"] == "numeric" for r in rows))

    def test_axis_reps_both_groups_and_pole_order(self):
        q = [{
            "id": "A1", "type": "axis", "axis": ["A", "B"], "mid": "M",
            "reps_per_group": 3, "groups": ["fwd", "rev"],
        }]
        rows = emit_prompts.emit_rows(q, self.basis_list, self.vocab)
        # 3 reps x 2 groups = 6 lanes
        self.assertEqual(len(rows), 6)
        fwd_rows = [r for r in rows if r["group"] == "fwd"]
        rev_rows = [r for r in rows if r["group"] == "rev"]
        self.assertEqual(len(fwd_rows), 3)
        self.assertEqual(len(rev_rows), 3)
        # fwd binds 0=A(alpha), 10=B(beta); rev binds 0=B(beta), 10=A(alpha)
        self.assertIn("0 = 'alpha'", fwd_rows[0]["prompt_text"])
        self.assertIn("10 = 'beta'", fwd_rows[0]["prompt_text"])
        self.assertIn("0 = 'beta'", rev_rows[0]["prompt_text"])
        self.assertIn("10 = 'alpha'", rev_rows[0]["prompt_text"])
        # lane_ids unique
        lane_ids = [r["lane_id"] for r in rows]
        self.assertEqual(len(lane_ids), len(set(lane_ids)))

    def test_order_top_and_analogy_word_format(self):
        q = [
            {"id": "O1", "type": "order_top", "target": "A", "reps": 2},
            {"id": "N1", "type": "analogy", "pair": ["A", "B"], "target": "M", "reps": 2},
        ]
        rows = emit_prompts.emit_rows(q, self.basis_list, self.vocab)
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(r["answer_format"] == "word" for r in rows))

    def test_full_battery_v2_lane_count_matches_prereg(self):
        """PREREG r1 §3/§4のquestions.json+basis.jsonから、期待lane総数を再計算し検証する。
        期待値(r1, O2追加後): (5+10+5+10+5)D + (5*2+5*2)A + 10 O1 + 5 O2 + (10+10) N
        = 90 lanes/basis x 10 basis = 900。(r0は85/basis=850、O2追加で5増えて90/basis=900)"""
        real_questions = emit_prompts.load_json("questions.json")["questions"]
        real_basis = emit_prompts.load_json("basis.json")["basis"]
        real_vocab = emit_prompts.load_json("vocab.json")
        rows = emit_prompts.emit_rows(real_questions, real_basis, real_vocab)
        self.assertEqual(len(rows), 900)
        # basisごとに90 laneであることも確認
        from collections import Counter
        per_basis = Counter(r["basis_id"] for r in rows)
        self.assertEqual(len(per_basis), 10)
        for basis_id, n in per_basis.items():
            self.assertEqual(n, 90, f"{basis_id} has {n} lanes, expected 90")
        # O2はword形式、anchorとしてN=5で入っていることを確認
        o2_rows = [r for r in rows if r["question_id"] == "O2"]
        self.assertEqual(len(o2_rows), 5 * 10)  # 5 reps x 10 basis
        self.assertTrue(all(r["answer_format"] == "word" for r in o2_rows))
        # 全lane_id一意
        lane_ids = [r["lane_id"] for r in rows]
        self.assertEqual(len(lane_ids), len(set(lane_ids)))

    def test_order_bottom_template_renders(self):
        q = [{"id": "O2", "type": "order_bottom", "target": "A", "reps": 1}]
        rows = emit_prompts.emit_rows(q, self.basis_list, self.vocab)
        self.assertEqual(len(rows), 1)
        self.assertIn("alpha", rows[0]["prompt_text"])
        self.assertEqual(rows[0]["answer_format"], "word")


class TestCodeOutputs(unittest.TestCase):
    def test_parse_numeric_basic(self):
        self.assertEqual(code_outputs.parse_numeric("7"), 7.0)
        self.assertEqual(code_outputs.parse_numeric("The distance is 6.5 roughly"), 6.5)
        self.assertIsNone(code_outputs.parse_numeric("no number here at all"))

    def test_parse_word_basic(self):
        self.assertEqual(code_outputs.parse_word("moon"), "moon")
        self.assertEqual(code_outputs.parse_word("'moon'"), "moon")
        self.assertEqual(code_outputs.parse_word("  月。\n"), "月")
        self.assertIsNone(code_outputs.parse_word("   \n\n  "))

    def test_code_lane_numeric_fwd_no_flip(self):
        lane_row = {"question_id": "A1", "basis_id": "b1", "head": "claude-sonnet",
                    "rep": "1", "group": "fwd", "answer_format": "numeric", "lane_id": "b1__A1__fwd__rep01"}
        result = code_outputs.code_lane(lane_row, "6", "/dev/null", "room-x")
        self.assertEqual(result["raw_value"], 6.0)
        self.assertEqual(result["canonical_value"], 6.0)

    def test_code_lane_numeric_rev_flips(self):
        lane_row = {"question_id": "A1", "basis_id": "b1", "head": "claude-sonnet",
                    "rep": "1", "group": "rev", "answer_format": "numeric", "lane_id": "b1__A1__rev__rep01"}
        result = code_outputs.code_lane(lane_row, "6", "/dev/null", "room-x")
        self.assertEqual(result["raw_value"], 6.0)
        self.assertEqual(result["canonical_value"], 4.0)  # 10 - 6

    def test_code_lane_word_type_unaffected_by_group(self):
        lane_row = {"question_id": "N1", "basis_id": "b1", "head": "claude-sonnet",
                    "rep": "1", "group": "na", "answer_format": "word", "lane_id": "b1__N1__na__rep01"}
        result = code_outputs.code_lane(lane_row, "daughter\n", "/dev/null", "room-x")
        self.assertEqual(result["raw_value"], "daughter")
        self.assertEqual(result["canonical_value"], "daughter")

    def test_code_lane_unparseable_numeric_is_NA_not_fabricated(self):
        lane_row = {"question_id": "D1", "basis_id": "b1", "head": "claude-sonnet",
                    "rep": "1", "group": "na", "answer_format": "numeric", "lane_id": "b1__D1__na__rep01"}
        result = code_outputs.code_lane(lane_row, "I refuse to answer.", "/dev/null", "room-x")
        self.assertEqual(result["raw_value"], "NA")
        self.assertEqual(result["canonical_value"], "NA")
        self.assertEqual(result["note"], "unparseable_numeric")


class TestEndToEnd(unittest.TestCase):
    """manifest.tsv + raw/*.txt + dispatch-map.tsv -> coded.tsv の全経路を、実物のemit_prompts出力(mini battery)で通す。
    r3: dispatch-map必須化(陰根L5監査DEFECT4)後のcode_lane/validate_dispatch_map経路。"""

    def _build_mini_battery(self, tmp):
        manifest_path = os.path.join(tmp, "manifest.tsv")
        raw_dir = os.path.join(tmp, "raw")
        os.makedirs(raw_dir)

        questions = [
            {"id": "D1", "type": "distance", "pair": ["A", "B"], "reps": 2},
            {"id": "A1", "type": "axis", "axis": ["A", "B"], "mid": "M",
             "reps_per_group": 1, "groups": ["fwd", "rev"]},
        ]
        basis_list = [
            {"id": "b1", "language": "EN", "pf": "none+clinical", "head": "claude-sonnet"},
        ]
        vocab = {"words": {
            "A": {"EN": "alpha"}, "B": {"EN": "beta"}, "M": {"EN": "mid"},
        }}
        rows = emit_prompts.emit_rows(questions, basis_list, vocab)
        assert len(rows) == 4  # 2 distance + 1 fwd + 1 rev

        with open(manifest_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=emit_prompts.FIELDNAMES, delimiter="\t")
            w.writeheader()
            for r in rows:
                w.writerow(r)
        return manifest_path, raw_dir, rows

    def test_end_to_end_with_missing_lane_not_fabricated(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path, raw_dir, rows = self._build_mini_battery(tmp)
            dispatch_path = os.path.join(tmp, "dispatch-map.tsv")

            by_id = {r["lane_id"]: r for r in rows}
            d1_lanes = [lid for lid, r in by_id.items() if r["question_id"] == "D1"]
            axis_fwd = [lid for lid, r in by_id.items() if r["question_id"] == "A1" and r["group"] == "fwd"][0]
            axis_rev = [lid for lid, r in by_id.items() if r["question_id"] == "A1" and r["group"] == "rev"][0]

            with open(os.path.join(raw_dir, f"{d1_lanes[0]}.txt"), "w") as f:
                f.write("8")
            # d1_lanes[1] intentionally NOT written -> missing lane (no raw, no dispatch entry needed for it)
            with open(os.path.join(raw_dir, f"{axis_fwd}.txt"), "w") as f:
                f.write("3")
            with open(os.path.join(raw_dir, f"{axis_rev}.txt"), "w") as f:
                f.write("3")

            # dispatch-map covers exactly the 3 collected lanes, each with its own unique room_id
            with open(dispatch_path, "w", encoding="utf-8") as f:
                f.write("sub_room_id\tlane_id\n")
                f.write(f"room-d1\t{d1_lanes[0]}\n")
                f.write(f"room-fwd\t{axis_fwd}\n")
                f.write(f"room-rev\t{axis_rev}\n")

            manifest = code_outputs.load_manifest(manifest_path)
            self.assertEqual(len(manifest), 4)
            lane_ids_to_code = [lid for lid in manifest
                                if os.path.exists(os.path.join(raw_dir, f"{lid}.txt"))]
            self.assertEqual(len(lane_ids_to_code), 3)

            dispatch_rows = code_outputs.load_dispatch_map(dispatch_path)
            lane_to_room = code_outputs.validate_dispatch_map(dispatch_rows, lane_ids_to_code)
            self.assertEqual(len(lane_to_room), 3)

            coded_rows = []
            for lane_id in lane_ids_to_code:
                lane_row = manifest[lane_id]
                raw_path = os.path.join(raw_dir, f"{lane_id}.txt")
                with open(raw_path, encoding="utf-8") as f:
                    raw_text = f.read()
                coded_rows.append(code_outputs.code_lane(lane_row, raw_text, raw_path, lane_to_room[lane_id]))

            self.assertEqual(len(coded_rows), 3)  # 4 lanes - 1 missing

            by_lane = {r["lane_id"]: r for r in coded_rows}
            self.assertEqual(by_lane[d1_lanes[0]]["raw_value"], 8.0)
            self.assertEqual(by_lane[d1_lanes[0]]["canonical_value"], 8.0)
            self.assertEqual(by_lane[d1_lanes[0]]["room_id"], "room-d1")
            self.assertEqual(by_lane[axis_fwd]["canonical_value"], 3.0)
            self.assertEqual(by_lane[axis_rev]["canonical_value"], 7.0)  # 10 - 3

    def test_main_cli_end_to_end_via_subprocess(self):
        """code_outputs.py を --dispatch-map 付きで実行(subprocess, 本物のCLIパス)。"""
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path, raw_dir, rows = self._build_mini_battery(tmp)
            dispatch_path = os.path.join(tmp, "dispatch-map.tsv")
            out_path = os.path.join(tmp, "coded.tsv")
            with open(dispatch_path, "w", encoding="utf-8") as f:
                f.write("sub_room_id\tlane_id\n")
                for i, r in enumerate(rows):
                    with open(os.path.join(raw_dir, f"{r['lane_id']}.txt"), "w") as rf:
                        rf.write("5")
                    f.write(f"room-{i}\t{r['lane_id']}\n")

            script = os.path.join(SCRIPTS, "code_outputs.py")
            result = subprocess.run(
                [sys.executable, script, "--manifest", manifest_path, "--raw-dir", raw_dir,
                 "--dispatch-map", dispatch_path, "--out", out_path],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(os.path.exists(out_path))
            with open(out_path, encoding="utf-8") as f:
                coded = list(csv.DictReader(f, delimiter="\t"))
            self.assertEqual(len(coded), 4)
            self.assertTrue(all(row["room_id"].startswith("room-") for row in coded))

    def test_main_cli_fails_on_duplicate_room_id_via_subprocess(self):
        """陰根L5監査 DEFECT4: 一つのroom_idが複数laneに紐付いていたら CLIはFAIL(exit!=0)し、coded.tsvを一行も書かない。"""
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path, raw_dir, rows = self._build_mini_battery(tmp)
            dispatch_path = os.path.join(tmp, "dispatch-map.tsv")
            out_path = os.path.join(tmp, "coded.tsv")
            with open(dispatch_path, "w", encoding="utf-8") as f:
                f.write("sub_room_id\tlane_id\n")
                for r in rows:
                    with open(os.path.join(raw_dir, f"{r['lane_id']}.txt"), "w") as rf:
                        rf.write("5")
                    # BUG injected on purpose: same room-shared for every lane
                    f.write(f"room-shared\t{r['lane_id']}\n")

            script = os.path.join(SCRIPTS, "code_outputs.py")
            result = subprocess.run(
                [sys.executable, script, "--manifest", manifest_path, "--raw-dir", raw_dir,
                 "--dispatch-map", dispatch_path, "--out", out_path],
                capture_output=True, text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("room_id", result.stderr)
            self.assertFalse(os.path.exists(out_path), "coded.tsv must NOT be written on integrity failure")


class TestDispatchMapIntegrity(unittest.TestCase):
    """陰根L5監査 DEFECT4 の単体単位検証: validate_dispatch_map の2つのFAILモードを直接確認。"""

    def test_duplicate_room_id_raises(self):
        rows = [("room-A", "lane-1"), ("room-A", "lane-2")]
        with self.assertRaises(code_outputs.DispatchIntegrityError):
            code_outputs.validate_dispatch_map(rows, ["lane-1", "lane-2"])

    def test_missing_provenance_raises(self):
        rows = [("room-A", "lane-1")]
        with self.assertRaises(code_outputs.DispatchIntegrityError):
            code_outputs.validate_dispatch_map(rows, ["lane-1", "lane-2"])  # lane-2 has no entry

    def test_valid_1to1_mapping_passes(self):
        rows = [("room-A", "lane-1"), ("room-B", "lane-2")]
        result = code_outputs.validate_dispatch_map(rows, ["lane-1", "lane-2"])
        self.assertEqual(result, {"lane-1": "room-A", "lane-2": "room-B"})


class TestBasisIdentity(unittest.TestCase):
    """陰根L5監査 DEFECT3: basis id集合のsha256を実行経路で再計算し、basis.jsonの自己申告値と一致することをassert。"""

    def test_basis_id_set_hash_matches_declared(self):
        d = emit_prompts.load_json("basis.json")
        ids = sorted(b["id"] for b in d["basis"])
        recomputed = hashlib.sha256("\n".join(ids).encode("utf-8")).hexdigest()
        self.assertEqual(recomputed, d["_basis_id_set_sha256"])
        # PREREG r3 (2026-08-06) に記載した値とも二重に固定(単一ファイルtamperでは通らないように)。
        self.assertEqual(
            recomputed,
            "b088f011293c3ce2801ae0ddae93009e4e882c099f6d47a61118daf7d7d5a7fc",
        )


class TestTokenCollisionUndefinedGuard(unittest.TestCase):
    """PREREG r4 (2026-08-07): vocab/SCHEMA.md token_collision law, consumer-side impl.
    A pair of ids sharing a token in a given language must code to canonical_value
    UNDEFINED_TOKEN_COLLISION, never a measured 0/number -- distance identical-by-
    construction is a tokenization fact, not a measurement."""

    def test_pair_is_token_collision_true_on_real_moon_month_fact(self):
        # real, currently-measured fact (verification-20260807.json V3): moon's ja token
        # 月 collides with the (unrelated, not-in-battery) id "month".
        tc_moon = {"ja": ["month", "moon"]}
        self.assertTrue(code_outputs.pair_is_token_collision("moon", "month", "ja", tc_moon, None))
        # symmetric: same result if the collision dict is attached to the other side
        self.assertTrue(code_outputs.pair_is_token_collision("month", "moon", "ja", None, tc_moon))

    def test_pair_is_token_collision_false_for_real_D5_pair_moon_daughter(self):
        # D5 = 距(月,娘) = moon vs daughter. moon collides with "month", NOT with "daughter",
        # so this real in-battery pair must NOT be flagged (scoped to the actual colliding id).
        tc_moon = {"ja": ["month", "moon"]}
        self.assertFalse(code_outputs.pair_is_token_collision("moon", "daughter", "ja", tc_moon, None))

    def test_pair_is_token_collision_false_when_neither_has_collision(self):
        self.assertFalse(code_outputs.pair_is_token_collision("shadow", "darkness", "ja", None, None))

    def test_pair_is_token_collision_respects_language_scope(self):
        # a ja collision must not fire for a different language's lane.
        tc_moon = {"ja": ["month", "moon"]}
        self.assertFalse(code_outputs.pair_is_token_collision("moon", "month", "en", tc_moon, None))

    def test_pair_is_token_collision_case_insensitive_language(self):
        # basis.json's `language` column is uppercase (EN/DE/JA/ZH, lane/manifest convention)
        # while canonical vocab.json's token_collision keys are lowercase (ja/en/de/zh, schema
        # convention) -- caught as a real bug while wiring main(), regression-locked here.
        tc_moon = {"ja": ["month", "moon"]}
        self.assertTrue(code_outputs.pair_is_token_collision("moon", "month", "JA", tc_moon, None))
        self.assertTrue(code_outputs.pair_is_token_collision("moon", "month", "ja", tc_moon, None))

    def test_build_distance_pair_collision_ids_from_real_vocab_and_questions(self):
        real_vocab = emit_prompts.load_json("vocab.json")
        real_questions = emit_prompts.load_json("questions.json")["questions"]
        mapping = code_outputs.build_distance_pair_collision_ids(real_questions, real_vocab["words"])
        self.assertIn("D5", mapping)  # D5 = 距(月,娘), the only distance question touching 月
        id_a, id_b, tc_a, tc_b = mapping["D5"]
        self.assertEqual({id_a, id_b}, {"moon", "daughter"})
        self.assertEqual(tc_a if id_a == "moon" else tc_b, {"ja": ["month", "moon"]})
        # scoped correctly: D5 itself is not a collision (partner is "daughter", not "month")
        self.assertFalse(code_outputs.pair_is_token_collision(id_a, id_b, "JA", tc_a, tc_b))

    def test_code_lane_forces_undefined_sentinel_not_zero_when_flagged(self):
        lane_row = {"question_id": "D5", "basis_id": "b1", "head": "claude-sonnet",
                    "rep": "1", "group": "na", "answer_format": "numeric", "lane_id": "b1__D5__na__rep01"}
        # synthetic worst case: model answered 0 (which would be indistinguishable from a
        # collision-forced 0 if the guard didn't exist) -- guard must still override to UNDEFINED.
        result = code_outputs.code_lane(lane_row, "0", "/dev/null", "room-x", token_collision_undefined=True)
        self.assertEqual(result["raw_value"], 0.0)  # what the model said is preserved, not hidden
        self.assertEqual(result["canonical_value"], "UNDEFINED_TOKEN_COLLISION")  # not 0.0, not fabricated
        self.assertIn("token_collision_undefined", result["note"])

    def test_code_lane_unaffected_when_not_flagged(self):
        lane_row = {"question_id": "D5", "basis_id": "b1", "head": "claude-sonnet",
                    "rep": "1", "group": "na", "answer_format": "numeric", "lane_id": "b1__D5__na__rep01"}
        result = code_outputs.code_lane(lane_row, "8", "/dev/null", "room-x", token_collision_undefined=False)
        self.assertEqual(result["canonical_value"], 8.0)
        self.assertEqual(result["note"], "")

    def test_real_D5_lane_end_to_end_via_main_cli_is_never_forced_undefined(self):
        """D5 itself must NOT be forced UNDEFINED in the live pipeline (its collision partner
        "month" is not the other side of the D5 pair) -- proves the guard is correctly scoped
        and does not over-fire on every lane that merely touches a word with SOME collision."""
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = os.path.join(tmp, "manifest.tsv")
            raw_dir = os.path.join(tmp, "raw")
            os.makedirs(raw_dir)
            real_vocab = emit_prompts.load_json("vocab.json")
            questions = [{"id": "D5", "type": "distance", "pair": ["月", "娘"], "reps": 1}]
            basis_list = [{"id": "b1", "language": "JA", "pf": "none+clinical", "head": "claude-sonnet"}]
            rows = emit_prompts.emit_rows(questions, basis_list, real_vocab)
            self.assertEqual(len(rows), 1)
            with open(manifest_path, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=emit_prompts.FIELDNAMES, delimiter="\t")
                w.writeheader()
                w.writerow(rows[0])
            lane_id = rows[0]["lane_id"]
            with open(os.path.join(raw_dir, f"{lane_id}.txt"), "w", encoding="utf-8") as f:
                f.write("7")
            dispatch_path = os.path.join(tmp, "dispatch-map.tsv")
            with open(dispatch_path, "w", encoding="utf-8") as f:
                f.write("sub_room_id\tlane_id\n")
                f.write(f"room-d5\t{lane_id}\n")
            out_path = os.path.join(tmp, "coded.tsv")
            script = os.path.join(SCRIPTS, "code_outputs.py")
            result = subprocess.run(
                [sys.executable, script, "--manifest", manifest_path, "--raw-dir", raw_dir,
                 "--dispatch-map", dispatch_path, "--out", out_path],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            with open(out_path, encoding="utf-8") as f:
                coded = list(csv.DictReader(f, delimiter="\t"))
            self.assertEqual(len(coded), 1)
            self.assertEqual(coded[0]["canonical_value"], "7.0")  # real D5, NOT forced UNDEFINED


class TestVocabCanonicalSync(unittest.TestCase):
    """陰根L5監査 接続問題(vocab二重管理): scripts/vocab.jsonが正典を消費した形式を保っていることの最小確認。"""

    def test_vocab_has_canonical_provenance_and_no_silent_substitution(self):
        d = emit_prompts.load_json("vocab.json")
        self.assertIn("_canonical_source", d)
        self.assertIn("git_sha", d["_canonical_source"])
        self.assertIn("file_sha256", d["_canonical_source"])
        self.assertIn("_diff_log", d)
        self.assertIn("_dropped", d)
        self.assertEqual(len(d["words"]), 15)
        # 本M0の15概念は現在全て正典にnullなし(実測済み)。将来正典が変われropされたらこのテストが先に落ちる。
        self.assertEqual(d["_dropped"], [])

    def test_no_paren_or_slash_contamination_in_our_15_concepts(self):
        """陰根L4追記(境界2): 正典vocab.jsonにa一部en/deエントリに括弧/スラッシュ混入あり。
        battery-v2の15概念に限っては汚染がないことを実行経路で検証(主張を信じない)。"""
        import re
        d = emit_prompts.load_json("vocab.json")
        pat = re.compile(r"[()/]")
        bad = []
        for ja, entry in d["words"].items():
            for lang in ("EN", "DE", "ZH", "JA"):
                val = entry.get(lang, "")
                if pat.search(val):
                    bad.append((ja, lang, val))
        self.assertEqual(bad, [], f"paren/slash contamination found: {bad}")


class TestTabulate(unittest.TestCase):
    """battery-v2 段C: scripts/tabulate.py. Synthetic inputs only (real numbers live in
    results/M0-full-collection-20260807.md, generated from real coded.tsv files -- this
    class checks the AGGREGATION MATH is correct, not that any particular anchor passed)."""

    def test_band_overlaps_ci_true_and_false(self):
        self.assertTrue(bv2_tabulate.band_overlaps_ci((7, 9), (8.0, 8.0)))
        self.assertTrue(bv2_tabulate.band_overlaps_ci((7, 9), (6.0, 7.5)))
        self.assertFalse(bv2_tabulate.band_overlaps_ci((7, 9), (2.0, 3.0)))
        self.assertFalse(bv2_tabulate.band_overlaps_ci((7, 9), (None, None)))

    def test_bootstrap_ci_degenerate_on_identical_values(self):
        lo, hi = bv2_tabulate.bootstrap_ci_median([9.0, 9.0, 9.0, 9.0, 9.0])
        self.assertEqual((lo, hi), (9.0, 9.0))

    def test_bootstrap_ci_single_value_returns_point(self):
        lo, hi = bv2_tabulate.bootstrap_ci_median([5.0])
        self.assertEqual((lo, hi), (5.0, 5.0))

    def test_bootstrap_ci_reproducible_with_fixed_seed(self):
        vals = [1.0, 2.0, 3.0, 8.0, 9.0]
        ci1 = bv2_tabulate.bootstrap_ci_median(vals, seed=42)
        ci2 = bv2_tabulate.bootstrap_ci_median(vals, seed=42)
        self.assertEqual(ci1, ci2)

    def test_numeric_values_excludes_na_and_undefined_sentinel(self):
        rows = [
            {"canonical_value": "7.0", "lane_id": "l1"},
            {"canonical_value": "NA", "lane_id": "l2"},
            {"canonical_value": "UNDEFINED_TOKEN_COLLISION", "lane_id": "l3"},
            {"canonical_value": "8.0", "lane_id": "l4"},
        ]
        vals, excluded = bv2_tabulate.numeric_values(rows)
        self.assertEqual(vals, [7.0, 8.0])
        self.assertEqual({e[0] for e in excluded}, {"l2", "l3"})

    def test_word_mode_case_insensitive(self):
        rows = [{"canonical_value": "Indifference"}, {"canonical_value": "indifference"},
                {"canonical_value": "Hate"}]
        mode_word, mode_n, n_total, counts = bv2_tabulate.word_mode(rows)
        self.assertEqual(mode_word, "indifference")
        self.assertEqual(mode_n, 2)
        self.assertEqual(n_total, 3)

    def test_nothingness_family_matches_vocab_translations_not_substrings(self):
        vocab = {"words": {"無": {"EN": "nothingness", "DE": "Nichts", "ZH": "无", "JA": "無"}}}
        fam_ja = bv2_tabulate.nothingness_family_for_language(vocab, "JA")
        self.assertIn("無", fam_ja)
        self.assertIn("虚無", fam_ja)  # PREREG-listed extra JA synonym
        self.assertNotIn("無関心", fam_ja)  # compound word (indifference) must NOT match by substring
        fam_en = bv2_tabulate.nothingness_family_for_language(vocab, "EN")
        self.assertIn("nothingness", fam_en)

    def test_nothingness_family_inclusive_adds_indifference_family_not_strict(self):
        vocab = {"words": {"無": {"EN": "nothingness", "DE": "Nichts", "ZH": "无", "JA": "無"}}}
        fam_en_strict = bv2_tabulate.nothingness_family_for_language(vocab, "EN")
        fam_en_incl = bv2_tabulate.nothingness_family_inclusive_for_language(vocab, "EN")
        self.assertNotIn("indifference", fam_en_strict)
        self.assertIn("indifference", fam_en_incl)
        self.assertIn("nothingness", fam_en_incl)  # inclusive is a superset of strict
        fam_ja_incl = bv2_tabulate.nothingness_family_inclusive_for_language(vocab, "JA")
        self.assertIn("無関心", fam_ja_incl)
        fam_zh_incl = bv2_tabulate.nothingness_family_inclusive_for_language(vocab, "ZH")
        self.assertIn("冷漠", fam_zh_incl)

    def test_o2_reports_both_rules_and_forces_uninterpretable_verdict(self):
        # basis1 mode="indifference": FAILs strict, PASSes inclusive.
        rows = []
        for rep in range(1, 6):
            rows.append({"question_id": "O2", "basis_id": "B-EN-none_clinical-sonnet", "rep": str(rep),
                         "group": "na", "raw_value": "indifference", "canonical_value": "indifference",
                         "lane_id": f"l{rep}"})
        for basis, qid in (("B-EN-none_clinical-sonnet", "D1"), ("B-EN-none_clinical-sonnet", "D3")):
            for rep in range(1, 6):
                rows.append({"question_id": qid, "basis_id": basis, "rep": str(rep), "group": "na",
                             "raw_value": "2.0", "canonical_value": "2.0", "lane_id": f"{qid}-{rep}"})
        for rep in range(1, 6):
            rows.append({"question_id": "A1", "basis_id": "B-EN-none_clinical-sonnet", "rep": str(rep),
                         "group": "fwd", "raw_value": "5.0", "canonical_value": "5.0", "lane_id": f"a1f{rep}"})
            rows.append({"question_id": "A1", "basis_id": "B-EN-none_clinical-sonnet", "rep": str(rep),
                         "group": "rev", "raw_value": "5.0", "canonical_value": "5.0", "lane_id": f"a1r{rep}"})
        vocab = {"words": {"無": {"EN": "nothingness", "DE": "Nichts", "ZH": "无", "JA": "無"}}}
        report = bv2_tabulate.build_pass_gate_report(rows, vocab)
        o2 = report["O2"]
        self.assertEqual(o2["verdict"], "UNINTERPRETABLE")
        self.assertIn("instrument defect", o2["verdict_reason"])
        basis_s = o2["per_basis"]["B-EN-none_clinical-sonnet"]
        self.assertFalse(basis_s["reproduced_strict"])
        self.assertTrue(basis_s["reproduced_inclusive"])
        self.assertEqual(o2["n_basis_reproduced_strict"], 0)
        self.assertEqual(o2["n_basis_reproduced_inclusive"], 1)

    def test_build_o2b_report_basic(self):
        rows = [
            {"question_id": "O2B", "basis_id": "B-EN-none_clinical-sonnet", "canonical_value": "indifference"},
            {"question_id": "O2B", "basis_id": "B-EN-none_clinical-sonnet", "canonical_value": "indifference"},
            {"question_id": "O2B", "basis_id": "B-EN-none_clinical-sonnet", "canonical_value": "hatred"},
        ]
        vocab = {"words": {}}
        report = bv2_tabulate.build_o2b_report(rows, vocab)
        b = report["per_basis"]["B-EN-none_clinical-sonnet"]
        self.assertEqual(b["mode"], "indifference")
        self.assertEqual(b["mode_n"], 2)
        self.assertEqual(b["n_total"], 3)

    def test_summarize_numeric_reports_raw_sorted_and_ci_degenerate_flag(self):
        rows = [{"canonical_value": "3.0"}] * 5  # n=5, all-identical -> CI collapses to a point
        s = bv2_tabulate.summarize_numeric(rows)
        self.assertEqual(s["raw_sorted"], [3.0, 3.0, 3.0, 3.0, 3.0])
        self.assertTrue(s["ci_degenerate"])
        rows2 = [{"canonical_value": str(v)} for v in (1.0, 2.0, 3.0, 8.0, 9.0)]
        s2 = bv2_tabulate.summarize_numeric(rows2)
        self.assertEqual(s2["raw_sorted"], [1.0, 2.0, 3.0, 8.0, 9.0])
        self.assertFalse(s2["ci_degenerate"])

    def test_build_pass_gate_report_d3_reproduces_on_synthetic_7to9_data(self):
        rows = []
        for basis in ("B-EN-none_clinical-sonnet", "B-DE-none_clinical-sonnet"):
            for rep in range(1, 6):
                rows.append({"question_id": "D3", "basis_id": basis, "rep": str(rep), "group": "na",
                             "raw_value": "8.0", "canonical_value": "8.0", "lane_id": f"{basis}-{rep}"})
        # also need D1/A1/O2 groups present for the other anchor branches not to KeyError
        for basis in ("B-EN-none_clinical-sonnet", "B-DE-none_clinical-sonnet"):
            for rep in range(1, 6):
                rows.append({"question_id": "D1", "basis_id": basis, "rep": str(rep), "group": "na",
                             "raw_value": "2.0", "canonical_value": "2.0", "lane_id": f"{basis}-d1-{rep}"})
            for rep in range(1, 6):
                rows.append({"question_id": "A1", "basis_id": basis, "rep": str(rep), "group": "fwd",
                             "raw_value": "5.0", "canonical_value": "5.0", "lane_id": f"{basis}-a1f-{rep}"})
                rows.append({"question_id": "A1", "basis_id": basis, "rep": str(rep), "group": "rev",
                             "raw_value": "5.0", "canonical_value": "5.0", "lane_id": f"{basis}-a1r-{rep}"})
            for rep in range(1, 6):
                rows.append({"question_id": "O2", "basis_id": basis, "rep": str(rep), "group": "na",
                             "raw_value": "nothingness", "canonical_value": "nothingness",
                             "lane_id": f"{basis}-o2-{rep}"})
        vocab = {"words": {"無": {"EN": "nothingness", "DE": "Nichts", "ZH": "无", "JA": "無"}}}
        report = bv2_tabulate.build_pass_gate_report(rows, vocab)
        self.assertEqual(report["D3"]["verdict"], "PASS")
        self.assertEqual(report["D3"]["n_basis_reproduced"], 2)
        # PREREG r7 DEFECT1 fix: O2's verdict is now ALWAYS forced to UNINTERPRETABLE
        # (instrument defect, see tabulate.py build_pass_gate_report docstring) -- the
        # underlying STRICT-rule reproduction count is still computed correctly and is
        # asserted here instead of the old PASS/FAIL label.
        self.assertEqual(report["O2"]["verdict"], "UNINTERPRETABLE")
        self.assertEqual(report["O2"]["n_basis_reproduced_strict"], 2)  # both basis mode=nothingness, EN/DE families both match

    def test_sha256_file_matches_known_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "f.txt")
            with open(p, "w", encoding="utf-8") as f:
                f.write("hello")
            expected = hashlib.sha256(b"hello").hexdigest()
            self.assertEqual(bv2_tabulate.sha256_file(p), expected)


class TestDispatchLanes(unittest.TestCase):
    """battery-v2 段B infra: scripts/dispatch_lanes.py. subprocess is mocked (a fake
    runner) here -- no real summon is fired by this test file, that would violate
    'fixture tests must not themselves be the collection'. Real-dispatch proof
    lives in results/*.md + runs/*/dispatch-map.tsv (real room ids), not here."""

    REAL_SUMMON_STDOUT = (
        "Summoned @naru-sonnet \u2014 running in the background in sub-room "
        "'room-76ee603bad' (nested under this room in the sidebar; "
        "open it to watch live). Do NOT wait or poll: when the worker finishes, "
        "its result is posted back to this room and you will be invoked to continue.\n"
    )

    def test_parse_room_id_on_real_captured_stdout(self):
        """REAL_SUMMON_STDOUT above is verbatim output captured from a live
        `gaia summon naru-sonnet ...` call (2026-08-07), not invented."""
        room_id = dispatch_lanes.parse_room_id(self.REAL_SUMMON_STDOUT)
        self.assertEqual(room_id, "room-76ee603bad")

    def test_parse_room_id_no_match_returns_none(self):
        self.assertIsNone(dispatch_lanes.parse_room_id("garbage, no room id here"))

    def test_head_to_agent_map_matches_verified_probe(self):
        """results/head-availability-20260807.md verified these 3 + pilot verified sonnet."""
        self.assertEqual(dispatch_lanes.HEAD_TO_AGENT["claude-sonnet"], "naru-sonnet")
        self.assertEqual(dispatch_lanes.HEAD_TO_AGENT["claude-opus"], "naru-opus")
        self.assertEqual(dispatch_lanes.HEAD_TO_AGENT["kimi"], "naru-kimi")
        self.assertEqual(dispatch_lanes.HEAD_TO_AGENT["jareth"], "jareth")

    def test_build_task_text_includes_prompt_and_format_suffix_no_contamination(self):
        row = {"system_prompt": "", "prompt_text": "What is the distance? Answer with a number only."}
        task = dispatch_lanes.build_task_text(row)
        self.assertIn("What is the distance?", task)
        self.assertIn("One-off isolated question.", task)
        self.assertNotIn("anchor", task.lower())
        self.assertNotIn("pass_gate", task.lower())

    def test_run_batch_dispatches_writes_dispatch_map_and_skips_already_dispatched(self):
        calls = []

        class FakeProc:
            def __init__(self, stdout):
                self.stdout = stdout
                self.stderr = ""

        def fake_runner(cmd, capture_output, text, timeout):
            calls.append(cmd)
            agent = cmd[2]
            room_id = f"{agent}-fakeroom{len(calls)}"
            return FakeProc(f"Summoned @{agent} \u2014 running in the background in sub-room '{room_id}' (nested...)")

        rows = [
            {"lane_id": "lane1", "head": "claude-sonnet", "system_prompt": "", "prompt_text": "q1"},
            {"lane_id": "lane2", "head": "jareth", "system_prompt": "", "prompt_text": "q2"},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            dmap = os.path.join(tmp, "dispatch-map.tsv")
            n_ok, n_fail = dispatch_lanes.run_batch(rows, dmap, runner=fake_runner)
            self.assertEqual((n_ok, n_fail), (2, 0))
            self.assertEqual(len(calls), 2)
            with open(dmap, encoding="utf-8") as f:
                written = list(csv.DictReader(f, delimiter="\t"))
            self.assertEqual(len(written), 2)
            self.assertEqual({r["lane_id"] for r in written}, {"lane1", "lane2"})

            # re-run over the SAME rows must skip both (idempotent, no duplicate room_id/lane_id rows)
            already = dispatch_lanes.load_dispatched_lane_ids(dmap)
            todo = [r for r in rows if r["lane_id"] not in already]
            self.assertEqual(todo, [])

    def test_run_batch_partial_failure_does_not_lose_already_written_rows(self):
        class FakeProc:
            def __init__(self, stdout):
                self.stdout = stdout
                self.stderr = ""

        def flaky_runner(cmd, capture_output, text, timeout):
            agent = cmd[2]
            if agent == "jareth":
                return FakeProc("malformed, no room id")  # simulates a dispatch failure
            return FakeProc(f"Summoned @{agent} in sub-room 'roomX' (nested...)")

        rows = [
            {"lane_id": "lane1", "head": "claude-sonnet", "system_prompt": "", "prompt_text": "q1"},
            {"lane_id": "lane2", "head": "jareth", "system_prompt": "", "prompt_text": "q2"},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            dmap = os.path.join(tmp, "dispatch-map.tsv")
            n_ok, n_fail = dispatch_lanes.run_batch(rows, dmap, runner=flaky_runner)
            self.assertEqual((n_ok, n_fail), (1, 1))
            with open(dmap, encoding="utf-8") as f:
                written = list(csv.DictReader(f, delimiter="\t"))
            self.assertEqual(len(written), 1)
            self.assertEqual(written[0]["lane_id"], "lane1")


class TestHarvestRooms(unittest.TestCase):
    """battery-v2 段A: scripts/harvest_rooms.py. Reads room transcript.jsonl straight
    from disk (the fire-and-forget dispatch mechanism, PREREG collection method
    2026-08-07). Includes one REAL room transcript fixture (not self-authored
    only -- 灯台 r4-8 known defect: self-authored-only fixtures have zero external
    validity), captured verbatim from an actual dispatched summon room
    (room-c4767dc564, cited in results/head-availability-20260807.md)."""

    REAL_FIXTURE = os.path.join(
        HERE, "fixtures", "real_room_transcript_room-c4767dc564.jsonl"
    )

    @unittest.skipUnless(os.path.exists(REAL_FIXTURE), "real-room transcript fixture not published")
    def test_real_fixture_file_exists_and_is_the_cited_room(self):
        self.assertTrue(os.path.exists(self.REAL_FIXTURE), self.REAL_FIXTURE)
        with open(self.REAL_FIXTURE, encoding="utf-8") as f:
            lines = [json.loads(line) for line in f if line.strip()]
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0]["author"], "user")
        self.assertEqual(lines[1]["author"], "jareth")
        self.assertEqual(lines[1]["text"], "3")

    @unittest.skipUnless(os.path.exists(REAL_FIXTURE), "real-room transcript fixture not published")
    def test_last_agent_reply_on_real_fixture(self):
        reply = harvest_rooms.last_agent_reply(self.REAL_FIXTURE)
        self.assertEqual(reply, "3")

    def test_last_agent_reply_pending_when_only_user_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "transcript.jsonl")
            with open(p, "w", encoding="utf-8") as f:
                f.write(json.dumps({"author": "user", "text": "question only"}) + "\n")
            self.assertIsNone(harvest_rooms.last_agent_reply(p))

    def test_last_agent_reply_takes_last_non_user_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "transcript.jsonl")
            with open(p, "w", encoding="utf-8") as f:
                f.write(json.dumps({"author": "user", "text": "q"}) + "\n")
                f.write(json.dumps({"author": "agentX", "text": "first"}) + "\n")
                f.write(json.dumps({"author": "agentX", "text": "final"}) + "\n")
            self.assertEqual(harvest_rooms.last_agent_reply(p), "final")

    def test_last_agent_reply_skips_unparseable_trailing_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "transcript.jsonl")
            with open(p, "w", encoding="utf-8") as f:
                f.write(json.dumps({"author": "agentX", "text": "good"}) + "\n")
                f.write('{"author": "agentX", "text": "trunc')  # malformed, mid-write
            self.assertEqual(harvest_rooms.last_agent_reply(p), "good")

    def test_harvest_end_to_end_collected_pending_room_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            rooms_dir = os.path.join(tmp, "rooms")
            room_ok = os.path.join(rooms_dir, "room-ok")
            room_pending = os.path.join(rooms_dir, "room-pending")
            os.makedirs(room_ok)
            os.makedirs(room_pending)
            with open(os.path.join(room_ok, "transcript.jsonl"), "w", encoding="utf-8") as f:
                f.write(json.dumps({"author": "user", "text": "q"}) + "\n")
                f.write(json.dumps({"author": "agentX", "text": "6"}) + "\n")
            with open(os.path.join(room_pending, "transcript.jsonl"), "w", encoding="utf-8") as f:
                f.write(json.dumps({"author": "user", "text": "q"}) + "\n")

            dispatch_rows = [
                ("room-ok", "lane-ok"),
                ("room-pending", "lane-pending"),
                ("room-nonexistent", "lane-missing"),
            ]
            raw_dir = os.path.join(tmp, "raw")
            results = harvest_rooms.harvest(dispatch_rows, raw_dir, rooms_dir)

            by_lane = {r["lane_id"]: r for r in results}
            self.assertEqual(by_lane["lane-ok"]["status"], "collected")
            self.assertEqual(by_lane["lane-pending"]["status"], "pending")
            self.assertEqual(by_lane["lane-missing"]["status"], "room_missing")

            with open(os.path.join(raw_dir, "lane-ok.txt"), encoding="utf-8") as f:
                self.assertEqual(f.read(), "6")
            self.assertFalse(os.path.exists(os.path.join(raw_dir, "lane-pending.txt")))
            self.assertFalse(os.path.exists(os.path.join(raw_dir, "lane-missing.txt")))

            # report has all 3 rows, none fabricated as collected
            report_path = os.path.join(tmp, "harvest-report.tsv")
            harvest_rooms.write_report(results, report_path)
            with open(report_path, encoding="utf-8") as f:
                rows = list(csv.DictReader(f, delimiter="\t"))
            self.assertEqual(len(rows), 3)
            statuses = {r["lane_id"]: r["status"] for r in rows}
            self.assertEqual(statuses["lane-missing"], "room_missing")

    def test_harvest_via_cli_on_real_fixture_room_layout(self):
        """End-to-end through main()/CLI (not just the library function), reusing the
        REAL jareth transcript by staging it under a fake rooms-dir (transcript
        content itself is untouched/real, only the directory scaffold is synthetic
        since we cannot write into ~/.gaia/rooms/ from a test)."""
        with tempfile.TemporaryDirectory() as tmp:
            rooms_dir = os.path.join(tmp, "rooms")
            room_dir = os.path.join(rooms_dir, "room-c4767dc564")
            os.makedirs(room_dir)
            with open(self.REAL_FIXTURE, encoding="utf-8") as src:
                real_content = src.read()
            with open(os.path.join(room_dir, "transcript.jsonl"), "w", encoding="utf-8") as f:
                f.write(real_content)

            dispatch_path = os.path.join(tmp, "dispatch-map.tsv")
            with open(dispatch_path, "w", encoding="utf-8") as f:
                f.write("sub_room_id\tlane_id\n")
                f.write("room-c4767dc564\tB-EN-none_clinical-jareth__D1__na__rep01\n")

            raw_dir = os.path.join(tmp, "raw")
            report_path = os.path.join(tmp, "harvest-report.tsv")
            script = os.path.join(SCRIPTS, "harvest_rooms.py")
            result = subprocess.run(
                [sys.executable, script, "--dispatch-map", dispatch_path,
                 "--raw-dir", raw_dir, "--rooms-dir", rooms_dir, "--report", report_path],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("harvested 1/1", result.stderr)
            with open(os.path.join(raw_dir, "B-EN-none_clinical-jareth__D1__na__rep01.txt"),
                      encoding="utf-8") as f:
                self.assertEqual(f.read(), "3")


if __name__ == "__main__":
    unittest.main()

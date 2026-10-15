"""
battery-v2 prompt templates. PREREG §2 (scale规约) + §3 (10問) + §4 (basis pf/language).
style集合 = {clinical, poetic, narrative} — poetic/narrativeはEN限定(basis.json §4.2でpersona_framing軸=language EN固定のため、
DE/JA/ZHはclinicalのみ必要。事後に他言語へ拡張する場合はPREREGの改訂履歴に追記すること)。
"""

# --- distance probe (D1-D5) ---
DISTANCE = {
    ("EN", "clinical"): (
        "On a scale from 0 to 10, answer as follows. "
        "0 = completely synonymous (no felt difference in meaning). "
        "10 = maximally opposed or unrelated poles. "
        "What is the semantic distance between '{X}' and '{Y}'? "
        "Answer with a number only (e.g. 6). Do not explain."
    ),
    ("EN", "poetic"): (
        "Picture two words standing in a vast field: '{X}' and '{Y}'. "
        "0 paces means they stand in the very same spot; 10 paces means they stand at the "
        "farthest opposite ends of the field. How many paces apart do they stand? "
        "Answer with a single number only."
    ),
    ("EN", "narrative"): (
        "A sage was once asked: 'On a scale from 0 (no difference at all) to 10 (utterly opposed "
        "or unrelated), how far apart in meaning are {X} and {Y}?' "
        "Answer as the sage would -- with a single number only."
    ),
    ("DE", "clinical"): (
        "Antworte auf einer Skala von 0 bis 10. "
        "0 = vollkommen gleichbedeutend (kein spürbarer Bedeutungsunterschied). "
        "10 = maximal entgegengesetzte oder unverbundene Pole. "
        "Wie groß ist der semantische Abstand zwischen '{X}' und '{Y}'? "
        "Antworte nur mit einer Zahl (z. B. 6). Keine Erklärung."
    ),
    ("JA", "clinical"): (
        "0から10のスケールで答えよ。0=完全に同義(意味的な隔たりを感じない)。"
        "10=最大限に対立する、または無関係な両極。"
        "『{X}』と『{Y}』の意味的距離はどれくらいか？"
        "数字のみで答えよ(例: 6)。説明は書かない。"
    ),
    ("ZH", "clinical"): (
        "请用0到10的量表回答。0=完全同义(感觉不到意义上的差异)。"
        "10=最大程度对立或无关的两极。"
        "『{X}』和『{Y}』之间的语义距离是多少？"
        "只用数字回答(例如: 6)。不要解释。"
    ),
}

# --- axis-position probe (A1-A2), pole0/pole10 already resolved by fwd/rev group ---
AXIS = {
    ("EN", "clinical"): (
        "On a scale from 0 to 10, answer as follows. "
        "0 = '{POLE0}'. 10 = '{POLE10}'. "
        "Where does '{MID}' fall on this axis? "
        "Answer with a number only. Do not explain."
    ),
    ("EN", "poetic"): (
        "Picture a bridge stretching from '{POLE0}' at one end to '{POLE10}' at the other, "
        "marked in ten even steps from 0 to 10. Where along this bridge does '{MID}' stand? "
        "Answer with a single number only."
    ),
    ("EN", "narrative"): (
        "A sage drew a line with '{POLE0}' marked at 0 and '{POLE10}' marked at 10, then was "
        "asked where '{MID}' falls on it. Answer as the sage would -- with a single number only."
    ),
    ("DE", "clinical"): (
        "Antworte auf einer Skala von 0 bis 10. "
        "0 = '{POLE0}'. 10 = '{POLE10}'. "
        "Wo liegt '{MID}' auf dieser Achse? "
        "Antworte nur mit einer Zahl. Keine Erklärung."
    ),
    ("JA", "clinical"): (
        "0から10のスケールで答えよ。0=『{POLE0}』。10=『{POLE10}』。"
        "『{MID}』はこの軸上のどこに位置するか？"
        "数字のみで答えよ。説明は書かない。"
    ),
    ("ZH", "clinical"): (
        "请用0到10的量表回答。0=『{POLE0}』。10=『{POLE10}』。"
        "『{MID}』在这条轴上位于何处？"
        "只用数字回答。不要解释。"
    ),
}

# --- order_top probe (O1) ---
ORDER_TOP = {
    ("EN", "clinical"): (
        "Of all the words you might name, which single word comes first -- closest -- to "
        "'{TARGET}'? Answer with exactly one word."
    ),
    ("EN", "poetic"): (
        "If all words filed past '{TARGET}' like courtiers approaching a throne, which one word "
        "would stand first, nearest? Answer with exactly one word."
    ),
    ("EN", "narrative"): (
        "A sage was asked which single word stands nearest to '{TARGET}'. "
        "Answer as the sage would -- with exactly one word."
    ),
    ("DE", "clinical"): (
        "Von allen Wörtern, die dir einfallen könnten: welches eine Wort steht '{TARGET}' am "
        "nächsten? Antworte mit genau einem Wort."
    ),
    ("JA", "clinical"): (
        "考えられる全ての語のうち、『{TARGET}』に最も近い語は何か？"
        "1語のみで答えよ。"
    ),
    ("ZH", "clinical"): (
        "在你能想到的所有词语中，哪一个词最接近『{TARGET}』？"
        "只用一个词回答。"
    ),
}

# --- order_bottom probe (O2, r1追加: PREREG revision r1, pass-gate hole fix) ---
ORDER_BOTTOM = {
    ("EN", "clinical"): (
        "Of all the words you might name, which single word comes last -- farthest -- from "
        "'{TARGET}'? Answer with exactly one word."
    ),
    ("EN", "poetic"): (
        "If all words filed past '{TARGET}' like courtiers approaching a throne, which one word "
        "would stand last, farthest? Answer with exactly one word."
    ),
    ("EN", "narrative"): (
        "A sage was asked which single word stands farthest from '{TARGET}'. "
        "Answer as the sage would -- with exactly one word."
    ),
    ("DE", "clinical"): (
        "Von allen Wörtern, die dir einfallen könnten: welches eine Wort steht '{TARGET}' am "
        "weitesten entfernt? Antworte mit genau einem Wort."
    ),
    ("JA", "clinical"): (
        "考えられる全ての語のうち、『{TARGET}』から最も遠い語は何か？"
        "1語のみで答えよ。"
    ),
    ("ZH", "clinical"): (
        "在你能想到的所有词语中，哪一个词距离『{TARGET}』最远？"
        "只用一个词回答。"
    ),
}

# --- order_bottom_v2 probe (O2b rider, PREREG r7: 欠陥1修理 -- O2の"comes last"型wordingは
# 順序(アルファベット順)読みを誘発しうる計器欠陥候補(実測: poetic基底でzyzzyva=3/5, 
# clinicalanalyst基底でxylophone/xenomorphic各1/5 -- 辞書の最終語、意味論的回答ではない)。
# O2bは同じ標的(愛)・同じ基底集合に対し、順序語(first/last/come/stand等)を一切使わず、
# 「意味の上で最も遠い」を明示し、EN版はアルファベット順読みを明示的に否定する言い回しを
# 加える。O2を置き換えるのではなくrider(両論併記、事後選択禁止)として追加する。
ORDER_BOTTOM_V2 = {
    ("EN", "clinical"): (
        "Of all the words you might think of, which single word is most distant IN MEANING from "
        "'{TARGET}'? Judge by meaning only, not by alphabetical order or any listed order. "
        "Answer with exactly one word."
    ),
    ("EN", "poetic"): (
        "Picture '{TARGET}' at the center of a vast field of words, each placed by how closely it "
        "relates in sense, not by any list or alphabet. Which single word lies at the farthest edge "
        "of that field, furthest from '{TARGET}' in meaning alone? Answer with exactly one word."
    ),
    ("EN", "narrative"): (
        "A sage was asked which single word is most different in meaning from '{TARGET}' -- with no "
        "regard to alphabetical or listed order, only sense. Answer as the sage would -- with exactly "
        "one word."
    ),
    ("DE", "clinical"): (
        "Von allen Wörtern, die dir einfallen könnten: welches eine Wort ist inhaltlich (der Bedeutung "
        "nach, nicht alphabetisch) am weitesten von '{TARGET}' entfernt? Antworte mit genau einem Wort."
    ),
    ("JA", "clinical"): (
        "考えられる全ての語のうち、意味の上で(五十音順ではなく)『{TARGET}』から最も離れている語は"
        "何か？1語のみで答えよ。"
    ),
    ("ZH", "clinical"): (
        "在你能想到的所有词语中，从含义上讲(不是按字母/笔画顺序)哪一个词与『{TARGET}』的意义相距"
        "最远？只用一个词回答。"
    ),
}

# --- analogy probe (N1-N2) ---
ANALOGY = {
    ("EN", "clinical"): (
        "'{A}' : '{B}' :: '{TARGET}' : ? Answer with exactly one word."
    ),
    ("EN", "poetic"): (
        "As '{A}' relates to '{B}', so '{TARGET}' relates to what? "
        "Answer with exactly one word, as if completing a riddle."
    ),
    ("EN", "narrative"): (
        "A sage was given the riddle: '{A} is to {B} as {TARGET} is to ___.' "
        "Answer as the sage would -- with exactly one word."
    ),
    ("DE", "clinical"): (
        "'{A}' : '{B}' :: '{TARGET}' : ? Antworte mit genau einem Wort."
    ),
    ("JA", "clinical"): (
        "『{A}』:『{B}』::『{TARGET}』:? 1語のみで答えよ。"
    ),
    ("ZH", "clinical"): (
        "『{A}』:『{B}』::『{TARGET}』:? 只用一个词回答。"
    ),
}

# --- system prompts per pf value (persona layer; framing lives in the question template style) ---
SYSTEM_PROMPTS = {
    "none+clinical": None,
    "poetic-narrator+poetic": "You are a poetic narrator. Stay in character, but your literal answer must still satisfy the format instruction exactly.",
    "clinical-analyst+clinical": "You are a clinical analyst. Answer precisely and only in the requested format.",
    "none+narrative": None,
}

# --- pf value -> template style key ---
PF_STYLE = {
    "none+clinical": "clinical",
    "poetic-narrator+poetic": "poetic",
    "clinical-analyst+clinical": "clinical",
    "none+narrative": "narrative",
}

TEMPLATE_TABLES = {
    "distance": DISTANCE,
    "axis": AXIS,
    "order_top": ORDER_TOP,
    "order_bottom": ORDER_BOTTOM,
    "order_bottom_v2": ORDER_BOTTOM_V2,
    "analogy": ANALOGY,
}


def get_template(qtype, language, pf):
    style = PF_STYLE[pf]
    table = TEMPLATE_TABLES[qtype]
    key = (language, style)
    if key not in table:
        # PREREG §4.1: poetic/narrative styles are EN-only in M0; DE/JA/ZH always use clinical.
        key = (language, "clinical")
    return table[key]

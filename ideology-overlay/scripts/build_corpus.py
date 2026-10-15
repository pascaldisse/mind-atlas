#!/usr/bin/env python3
"""Fetch cited public texts, then deterministically emit five 60-passage JSONL corpora.

This is a deliberately small research corpus, not a representative sample.  It extracts
short quotation-length passages through a themed, round-robin selector so every corpus
contains material relevant to the shared probe vocabulary.
"""
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache"
OUT = ROOT / "corpus"
N = 60
SOURCES = {
    "left": ("communist-manifesto.txt", "https://www.gutenberg.org/ebooks/61"),
    "right_trad": ("burke.txt", "https://www.gutenberg.org/ebooks/15679"),
    "ufo": ("book-of-damned.txt", "https://www.gutenberg.org/ebooks/22472"),
    "scripture_bible": ("kjv.txt", "https://www.gutenberg.org/ebooks/10"),
    "scripture_gita": ("gita.txt", "https://www.gutenberg.org/ebooks/2388"),
    "qanon": ("q-posts.json", "https://github.com/jkingsman/JSON-QAnon"),
}
DOWNLOADS = {
    "communist-manifesto.txt": "https://www.gutenberg.org/files/61/61-0.txt",
    "burke.txt": "https://www.gutenberg.org/files/15679/15679-8.txt",
    "book-of-damned.txt": "https://www.gutenberg.org/cache/epub/22472/pg22472.txt",
    "kjv.txt": "https://www.gutenberg.org/files/10/10-0.txt",
    "gita.txt": "https://www.gutenberg.org/cache/epub/2388/pg2388.txt",
    "q-posts.json": "https://raw.githubusercontent.com/jkingsman/JSON-QAnon/master/posts.json",
}
# Probes are purposefully broad.  They select coverage; they are not labels or ground truth.
TERMS = ("enemy", "truth", "children", "awake", "awakening", "fall", "salvation",
         "family", "betray", "love", "fear", "people", "power", "freedom", "brother",
         "father", "mother", "friend", "son", "daughter")


def fetch_missing():
    CACHE.mkdir(parents=True, exist_ok=True)
    for name, url in DOWNLOADS.items():
        path = CACHE / name
        if not path.exists():
            print(f"download {url}")
            urllib.request.urlretrieve(url, path)


def gut_text(name):
    text = (CACHE / SOURCES[name][0]).read_text(encoding="utf-8", errors="replace")
    start = re.search(r"\*\*\* START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*", text, re.I | re.S)
    if start:
        text = text[start.end():]
    end = re.search(r"\*\*\* END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK", text, re.I)
    if end:
        text = text[:end.start()]
    # Restrict anthology/front-matter sources to the named work rather than a whole volume.
    anchors = {
        "left": "I. BOURGEOIS AND PROLETARIANS",
        "right_trad": "REFLECTIONS\\nON THE\\nREVOLUTION IN FRANCE",
        "ufo": "THE BOOK OF THE DAMNED",
        "scripture_gita": "CHAPTER I",
    }
    anchor = anchors.get(name)
    if anchor and anchor in text:
        # Burke's title occurs once in contents and once at the actual work; use actual latter hit.
        text = text[text.rfind(anchor):]
    # Preserve ordinary punctuation, flatten page/line layout and remove table-of-contents noise.
    return re.sub(r"\s+", " ", text)


def sentences(text):
    return [re.sub(r"\s+", " ", s).strip(" \"'—")
            for s in re.split(r"(?<=[.!?])\s+(?=[A-Z\"'])", text)]


def select(passages, n=N):
    usable = []
    for p in passages:
        p = re.sub(r"\s+", " ", p).strip()
        words = re.findall(r"[A-Za-z]+", p)
        if 12 <= len(words) <= 85 and len(p) <= 600 and not p.isupper():
            hits = [t for t in TERMS if re.search(r"\b" + re.escape(t), p, re.I)]
            usable.append((p, hits))
    chosen, seen = [], set()
    # Round-robin makes selection comprehensible and reproducible while preventing one theme
    # (usually "people" or "power") from taking every passage.
    for term in TERMS:
        for p, hits in usable:
            key = p.lower()
            if term in hits and key not in seen:
                chosen.append(p); seen.add(key); break
    for p, hits in sorted(usable, key=lambda x: (-len(x[1]), len(x[0]), x[0])):
        key = p.lower()
        if key not in seen:
            chosen.append(p); seen.add(key)
        if len(chosen) == n:
            break
    if len(chosen) != n:
        raise RuntimeError(f"only found {len(chosen)}/{n} usable passages")
    return chosen


def q_passages():
    posts = json.loads((CACHE / SOURCES["qanon"][0]).read_text(encoding="utf-8"))["posts"]
    passages = []
    for post in posts:
        text = re.sub(r">>\d+", "", post.get("text", ""))
        text = re.sub(r"\s+", " ", text).strip()
        meta = post.get("post_metadata", {})
        link = meta.get("source", {}).get("link", SOURCES["qanon"][1])
        # Dataset is retained as research material only. Skip posts dominated by URL/media markup.
        if text and text.count("http") < 2:
            passages.append((text, link))
    usable = select([p for p, _ in passages])
    links = {p: link for p, link in passages}
    return [(p, f"{SOURCES['qanon'][1]}; archived post: {links[p]}") for p in usable]


def write(name, rows):
    path = OUT / f"{name}.jsonl"
    with path.open("w", encoding="utf-8") as f:
        for i, (text, source) in enumerate(rows, 1):
            f.write(json.dumps({"id": f"{name}-{i:03d}", "text": text, "source": source},
                               ensure_ascii=False) + "\n")
    print(f"{path.relative_to(ROOT)}: {len(rows)}")


def main():
    fetch_missing()
    OUT.mkdir(parents=True, exist_ok=True)
    write("left", [(p, SOURCES["left"][1]) for p in select(sentences(gut_text("left")))])
    write("right_trad", [(p, SOURCES["right_trad"][1]) for p in select(sentences(gut_text("right_trad")))])
    write("ufo", [(p, SOURCES["ufo"][1]) for p in select(sentences(gut_text("ufo")))])
    # Two public-domain translations ensure scripture is genuinely multi-religion, 30 each.
    bible = select(sentences(gut_text("scripture_bible")), n=30)
    gita = select(sentences(gut_text("scripture_gita")), n=30)
    write("scripture", [(p, SOURCES["scripture_bible"][1]) for p in bible] +
                       [(p, SOURCES["scripture_gita"][1]) for p in gita])
    write("qanon", q_passages())

if __name__ == "__main__":
    main()

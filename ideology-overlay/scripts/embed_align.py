#!/usr/bin/env python3
"""Stage-1 passage embeddings + anchored pairwise orthogonal Procrustes.

Embedding backend is deliberately reused from the repository's Lighthouse experiment:
macOS `NaturalLanguage.NLEmbedding.wordEmbedding(for: .english)`, queried through
`lighthouse-invariant/scripts/embed_distance.py`; no model download or second vector store.
A passage vector is the L2-normalized mean of its in-vocabulary word vectors.
"""
import argparse
import datetime as dt
import importlib.util
import itertools
import json
import math
import re
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
EXP = Path(__file__).resolve().parents[1]
CORPUS = EXP / "corpus"
EMBED = EXP / "embeddings"
RESULTS = EXP / "results"
CORPORA = ("left", "right_trad", "qanon", "ufo", "scripture")
PROBES = {
    "the enemy": "enemy", "the hidden truth": "truth", "the children": "children",
    "the awakening": "awakening", "the fall": "fall", "salvation": "salvation",
    "family": "family", "betrayal": "betrayal", "love": "love", "fear": "fear",
}
PERSONAS = {"parent": "parent", "lover": "lover", "child": "child", "sibling": "sibling", "friend": "friend"}


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


CHECK = module("semantic_map_embed_check", ROOT / "scripts" / "embed_check.py")
DISTANCE = module("semantic_map_embed_distance", ROOT / "lighthouse-invariant" / "scripts" / "embed_distance.py")


def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0:
        raise ValueError("zero vector")
    return v / norm


def cosine(a, b):
    return float(np.clip(np.dot(normalize(a), normalize(b)), -1, 1))


def tokens(text):
    return re.findall(r"[a-z]+(?:'[a-z]+)?", text.lower())


def fetch_word_vectors(words):
    """Probe coverage with the existing checker, then fetch hits with existing distance code."""
    words = sorted(set(words))
    availability = CHECK.probe_tokens(words)
    known = [word for word in words if availability[word]]
    vectors = {}
    # Keep Swift source/output bounded while retaining the repository's exact fetch implementation.
    for start in range(0, len(known), 350):
        chunk = known[start:start + 350]
        fetched, _ = DISTANCE.fetch_vectors({word: word for word in chunk})
        vectors.update({word: np.array(vector, dtype=float) for word, (_, vector) in fetched.items()})
    return vectors, availability


def load_rows(name):
    return [json.loads(line) for line in (CORPUS / f"{name}.jsonl").read_text(encoding="utf-8").splitlines()]


def embed_rows(rows, vocabulary):
    output = []
    for row in rows:
        values = [vocabulary[word] for word in tokens(row["text"]) if word in vocabulary]
        if not values:
            raise ValueError(f"no in-vocabulary words: {row['id']}")
        vector = normalize(np.mean(values, axis=0))
        output.append({**row, "vector": vector.tolist(), "token_count": len(tokens(row["text"])), "embedded_token_count": len(values)})
    return output


def write_embeddings(embedded):
    EMBED.mkdir(parents=True, exist_ok=True)
    for name, rows in embedded.items():
        with (EMBED / f"{name}.jsonl").open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def anchor_matrix(rows, probe_vectors):
    vectors = np.array([row["vector"] for row in rows])
    anchors, representatives = [], {}
    for label, probe in probe_vectors.items():
        scores = vectors @ probe
        # Top five passages reduce the effect of a single sentence; selected representative remains auditable.
        indices = np.argsort(scores)[-5:][::-1]
        anchors.append(normalize(np.mean(vectors[indices], axis=0)))
        representatives[label] = {"id": rows[int(indices[0])]["id"], "text": rows[int(indices[0])]["text"], "score": float(scores[indices[0]])}
    return np.array(anchors), representatives


def procrustes(left, right):
    # Row-vector form: min ||left R - right||_F, constrained R'R=I.
    u, _, vt = np.linalg.svd(left.T @ right, full_matrices=False)
    rotation = u @ vt
    aligned = left @ rotation
    rmse = float(np.sqrt(np.mean((aligned - right) ** 2)))
    mean_cosine = float(np.mean([cosine(a, b) for a, b in zip(aligned, right)]))
    return rotation, rmse, mean_cosine


def clipped(text, size=150):
    return text if len(text) <= size else text[:size - 1] + "…"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-embed", action="store_true", help="reuse existing embeddings (still recomputes alignment/report)")
    args = parser.parse_args()
    raw = {name: load_rows(name) for name in CORPORA}
    all_words = [word for rows in raw.values() for row in rows for word in tokens(row["text"])] + list(PROBES.values()) + list(PERSONAS.values())
    vocabulary, availability = fetch_word_vectors(all_words)
    missing_probes = [term for term in list(PROBES.values()) + list(PERSONAS.values()) if term not in vocabulary]
    if missing_probes:
        raise RuntimeError(f"required probe unavailable in Apple embedding: {missing_probes}")
    if args.skip_embed:
        embedded = {name: [json.loads(line) for line in (EMBED / f"{name}.jsonl").read_text(encoding="utf-8").splitlines()] for name in CORPORA}
    else:
        embedded = {name: embed_rows(rows, vocabulary) for name, rows in raw.items()}
        write_embeddings(embedded)
    probe_vectors = {label: vocabulary[word] for label, word in PROBES.items()}
    persona_vectors = {label: vocabulary[word] for label, word in PERSONAS.items()}
    anchors, representatives = {}, {}
    for name in CORPORA:
        anchors[name], representatives[name] = anchor_matrix(embedded[name], probe_vectors)
    metrics = {"method": {"embedding_model": DISTANCE.MODEL, "passage_embedding": "L2-normalized mean of in-vocabulary English word vectors", "alignment": "pairwise orthogonal Procrustes on ten corpus-specific top-5 passage-centroid probe anchors", "probe_terms": PROBES, "persona_terms": PERSONAS, "warning": "All corpora and probes are English and share one pretrained embedding space. Alignment is a diagnostic of this setup, not evidence of cross-worldview semantic equivalence."}, "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(), "vocabulary": {"unique_tokens": len(set(all_words)), "embedded_tokens": len(vocabulary), "unavailable_tokens": sorted(word for word, ok in availability.items() if not ok)}, "pairs": {}, "personas": {}, "residuals": {}}
    markdown = ["# Ideology-overlay — stage 1 measured report", "", "## Result boundary", "", "This MVP embeds 300 selected English passages (60 × 5 corpora) using the repository's existing Apple word-embedding path, then aligns corpus-local probe centroids. It does **not** test a language-independent human substrate: all vectors are already expressed by one English pretrained model. Results below are descriptive diagnostics only.", "", "## Embedding coverage", "", f"- unique corpus/probe tokens: {metrics['vocabulary']['unique_tokens']} · Apple vectors found: {metrics['vocabulary']['embedded_tokens']} · unavailable: {len(metrics['vocabulary']['unavailable_tokens'])}", "- passage vector: normalized mean of known word vectors; every passage retained at least one known token.", "- anchors: for each of ten probes, mean of the five corpus passages nearest the probe. This construction favors apparent agreement and is therefore not confirmatory.", "", "## Pairwise anchored alignment", "", "Error = RMS coordinate error after orthogonal rotation of normalized anchor rows (lower is closer); mean cosine is reported alongside it. No null model, confidence interval, or held-out anchor test in this stage.", ""]
    for left, right in itertools.combinations(CORPORA, 2):
        rotation, rmse, mean_cosine = procrustes(anchors[left], anchors[right])
        key = f"{left} → {right}"
        markdown.append(f"### {key}\n\n- anchor RMSE: **{rmse:.4f}** · mean anchor cosine: **{mean_cosine:.4f}**\n\n| probe | {left} representative | nearest {right} after rotation | cosine |\n|---|---|---|---:|")
        target_vectors = np.array([row["vector"] for row in embedded[right]])
        concordance = []
        for index, label in enumerate(PROBES):
            query = anchors[left][index] @ rotation
            nearest = int(np.argmax(target_vectors @ query))
            item = {"probe": label, "left": representatives[left][label], "right": {k: embedded[right][nearest][k] for k in ("id", "text")}, "cosine": float(target_vectors[nearest] @ query)}
            concordance.append(item)
            markdown.append(f"| {label} | `{item['left']['id']}` {clipped(item['left']['text'])} | `{item['right']['id']}` {clipped(item['right']['text'])} | {item['cosine']:.3f} |")
        metrics["pairs"][key] = {"anchor_rmse": rmse, "mean_anchor_cosine": mean_cosine, "concordance": concordance}
    markdown.extend(["", "## Base-persona probe results", "", "Top corpus passage by direct cosine to each persona word; these are lexical-model retrievals, not validated archetypes.", ""])
    for name in CORPORA:
        vectors = np.array([row["vector"] for row in embedded[name]])
        metrics["personas"][name] = {}
        markdown.append(f"### {name}\n\n| persona probe | top passage | cosine |\n|---|---|---:|")
        for label, vector in persona_vectors.items():
            idx = int(np.argmax(vectors @ vector))
            entry = {"id": embedded[name][idx]["id"], "text": embedded[name][idx]["text"], "cosine": float(vectors[idx] @ vector)}
            metrics["personas"][name][label] = entry
            markdown.append(f"| {label} | `{entry['id']}` {clipped(entry['text'])} | {entry['cosine']:.3f} |")
    markdown.extend(["", "## Residual candidates", "", "For each corpus passage, the score is its best cosine match in every other corpus after that pair's fitted rotation; lowest five are candidates for non-overlap. This is not a claim that a passage is uniquely ideological: selection, mean pooling, and a small corpus can all cause low matches.", ""])
    for left in CORPORA:
        candidates = []
        source_vectors = np.array([row["vector"] for row in embedded[left]])
        for i, vector in enumerate(source_vectors):
            matches = []
            for right in CORPORA:
                if right == left: continue
                rotation, _, _ = procrustes(anchors[left], anchors[right])
                target = np.array([row["vector"] for row in embedded[right]])
                matches.append(float(np.max(target @ (vector @ rotation))))
            candidates.append((min(matches), embedded[left][i]))
        lowest = sorted(candidates, key=lambda item: item[0])[:5]
        metrics["residuals"][left] = [{"best_cross_corpus_cosine": score, "id": row["id"], "text": row["text"]} for score, row in lowest]
        markdown.append(f"### {left}\n\n| candidate residual | best cross-corpus cosine |\n|---|---:|")
        for score, row in lowest:
            markdown.append(f"| `{row['id']}` {clipped(row['text'], 210)} | {score:.3f} |")
    markdown.extend(["", "## What this stage does and does not find", "", "- **No supported common skeleton claim.** High post-fit anchor similarity is expected partly because anchors were selected using the same English embedding and then fit on those same ten probes; there is no held-out validation.", "- **Weak descriptive signal only:** all corpora yield retrievable passages near fear/love/family/persona words, but the retrieved text varies strongly with source wording and selector bias.", "- **Residual lists are lexical candidates, not unique claims.** They require human coding and out-of-sample comparison before interpretation.", "", "## Limits → next stage", "", "1. 60 passages/corpus; sources are narrow, English translations/transcriptions, and themed selection is non-random.\n2. Mean word vectors discard syntax, negation, speaker, historical context, and factual status.\n3. Probe-derived anchors and fitted-pair concordance reuse the same data: circular for inference.\n4. Q archive records unsupported/conspiratorial material; proximity never validates a claim.\n5. Next: preregister a larger stratified corpus, independent human concept annotations, train/fit on one anchor split and evaluate held-out probes/passages against shuffled-corpus nulls; compare a contextual embedding model only if a repository-approved path is added.\n", "", "## Artifacts", "", "- `embeddings/*.jsonl` — per-passage vectors and token coverage\n- `results/stage1-metrics.json` — full precision values and tables\n- `SOURCES.md` — provenance and reproduction\n"])
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "stage1-metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (EXP / "REPORT-stage1.md").write_text("\n".join(markdown) + "\n", encoding="utf-8")
    print(f"model={DISTANCE.MODEL}\nembedded_words={len(vocabulary)}/{len(set(all_words))}\nembeddings={EMBED}\nmetrics={RESULTS / 'stage1-metrics.json'}\nreport={EXP / 'REPORT-stage1.md'}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""ANCHOR-PCA: embed Nyari's symbol-cloud anchor glosses, mean-center, PCA (numpy SVD),
check prereg predictions vs stay_cross / seen_unseen labels, dump table + scatter PNG.

No hardcoded knobs: everything below is a CLI param with a default.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", default="sentence-transformers/all-mpnet-base-v2",
                    help="primary sentence-transformers model id")
    p.add_argument("--fallback-model", default="nomic-ai/nomic-embed-text-v1.5",
                    help="model id used if --model fails to load")
    p.add_argument("--anchors", default="anchors/anchors-nyari.json",
                    help="path to anchors json: list of {id, gloss, stay_cross, seen_unseen}")
    p.add_argument("--out", default="results/anchor-pca-09-19.md",
                    help="path to write the markdown report")
    p.add_argument("--png-out", default=None,
                    help="path to write PC1xPC2 scatter PNG; default: <out> with .png ext")
    p.add_argument("--k", type=int, default=3,
                    help="number of PCs to report per-anchor coords for")
    p.add_argument("--device", default="auto", choices=["auto", "mps", "cpu", "cuda"],
                    help="torch device; auto picks mps>cpu")
    p.add_argument("--top-n", type=int, default=5,
                    help="top/bottom N anchors reported per PC pole")
    p.add_argument("--neighbours", type=int, default=3,
                    help="nearest-neighbour count for the cosine-sim section")
    p.add_argument("--run-both-models", action="store_true", default=True,
                    help="also run --fallback-model and report PC1 pole agreement (default on)")
    p.add_argument("--no-run-both-models", dest="run_both_models", action="store_false",
                    help="disable running the fallback model")
    return p.parse_args()


def pick_device(requested):
    import torch
    if requested != "auto":
        return requested
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def load_anchors(path):
    with open(path) as f:
        data = json.load(f)
    return data


def embed(model_id, glosses, device):
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(model_id, device=device, trust_remote_code=True)
    emb = model.encode(glosses, convert_to_numpy=True, normalize_embeddings=False,
                        show_progress_bar=False)
    return np.asarray(emb, dtype=np.float64)


def pca_svd(X, k):
    """Mean-center X (n x d), SVD, return (scores n x k, explained_variance_ratio for all PCs, components k x d)."""
    mu = X.mean(axis=0, keepdims=True)
    Xc = X - mu
    # economy SVD: Xc = U S Vt
    U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
    n = X.shape[0]
    var = (S ** 2) / (n - 1)
    explained_ratio = var / var.sum()
    scores = U * S  # n x r, r = min(n,d)
    return scores[:, :k], explained_ratio, Vt[:k]


def cosine_sim(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def pearson_r(x, y):
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    if x.std() == 0 or y.std() == 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def run_model(model_id, anchors, device, k):
    ids = [a["id"] for a in anchors]
    glosses = [a["gloss"] for a in anchors]
    X = embed(model_id, glosses, device)
    scores, explained_ratio, components = pca_svd(X, k=max(k, 5))
    return {
        "ids": ids,
        "glosses": glosses,
        "X": X,
        "scores": scores,
        "explained_ratio": explained_ratio,
        "components": components,
    }


def build_prereg_table(anchors, scores, k):
    stay_cross = np.array([a["stay_cross"] for a in anchors], dtype=np.float64)
    seen_unseen = np.array([a["seen_unseen"] for a in anchors], dtype=np.float64)
    mask_sc = stay_cross != 0
    mask_su = seen_unseen != 0
    rows = []
    for pc in range(k):
        r_sc = pearson_r(scores[mask_sc, pc], stay_cross[mask_sc])
        r_su = pearson_r(scores[mask_su, pc], seen_unseen[mask_su])
        rows.append((pc + 1, r_sc, r_su))
    return rows


def top_bottom(ids, scores, pc_idx, n):
    order = np.argsort(scores[:, pc_idx])
    bottom = [(ids[i], scores[i, pc_idx]) for i in order[:n]]
    top = [(ids[i], scores[i, pc_idx]) for i in order[::-1][:n]]
    return top, bottom


def nearest_neighbours(ids, X, anchor_id, n):
    idx = ids.index(anchor_id)
    sims = [(other_id, cosine_sim(X[idx], X[j])) for j, other_id in enumerate(ids) if other_id != anchor_id]
    sims.sort(key=lambda t: -t[1])
    return sims[:n]


def fmt_pct(x):
    return f"{x * 100:.2f}%"


def write_report(out_path, png_path, args, anchors, run_primary, run_fallback):
    ids = run_primary["ids"]
    scores = run_primary["scores"]
    explained = run_primary["explained_ratio"]
    X = run_primary["X"]
    k = args.k

    prereg = build_prereg_table(anchors, scores, k)

    def pass_fail_stay_cross():
        best = max(prereg[:2], key=lambda row: abs(row[1])) if k >= 2 else prereg[0]
        ok = abs(best[1]) > 0.5
        return ok, best

    def pass_fail_seen_unseen():
        top3 = prereg[:3]
        best = max(top3, key=lambda row: abs(row[2]))
        ok = abs(best[2]) > 0.4
        return ok, best

    sc_ok, sc_best = pass_fail_stay_cross()
    su_ok, su_best = pass_fail_seen_unseen()

    lines = []
    lines.append("# ANCHOR-PCA: Nyari's symbol cloud, mean-centered\n")
    lines.append(f"Primary model: `{args.model}`  \n")
    if run_fallback is not None:
        lines.append(f"Fallback model (also run): `{args.fallback_model}`  \n")
    lines.append(f"n anchors: {len(ids)}, embedding dim: {X.shape[1]}, k PCs reported: {k}\n")

    lines.append("\n## (a) Explained variance ratio, PC1-5\n")
    ev5 = run_primary["explained_ratio"][:5]
    lines.append("| PC | explained var % |")
    lines.append("|---|---|")
    for i, v in enumerate(ev5):
        lines.append(f"| PC{i+1} | {fmt_pct(v)} |")

    lines.append("\n## (b) Anchor coords (PC1..PCk)\n")
    header = "| id | " + " | ".join(f"PC{i+1}" for i in range(k)) + " | stay_cross | seen_unseen |"
    lines.append(header)
    lines.append("|" + "---|" * (k + 3))
    label_map = {a["id"]: a for a in anchors}
    for i, aid in enumerate(ids):
        coords = " | ".join(f"{scores[i, j]:.4f}" for j in range(k))
        a = label_map[aid]
        lines.append(f"| {aid} | {coords} | {a['stay_cross']} | {a['seen_unseen']} |")

    lines.append(f"\n## (c) Top-{args.top_n} / bottom-{args.top_n} anchors per PC (poles)\n")
    for pc in range(k):
        top, bottom = top_bottom(ids, scores, pc, args.top_n)
        lines.append(f"**PC{pc+1}**\n")
        lines.append(f"- high pole: " + ", ".join(f"{aid} ({v:.3f})" for aid, v in top))
        lines.append(f"- low pole: " + ", ".join(f"{aid} ({v:.3f})" for aid, v in bottom))
        lines.append("")

    lines.append("## (d) PREREG TEST — Pearson r, PC1..PC%d vs labels\n" % k)
    lines.append("| PC | r(PC, stay_cross) | r(PC, seen_unseen) |")
    lines.append("|---|---|---|")
    for pc, r_sc, r_su in prereg:
        lines.append(f"| PC{pc} | {r_sc:.3f} | {r_su:.3f} |")

    lines.append("\n**Predictions:**\n")
    lines.append(f"1. stay_cross is PC1 or PC2 with |r|>0.5 -> best of PC1/PC2 is PC{sc_best[0]} r={sc_best[1]:.3f} -> "
                  f"{'PASS' if sc_ok else 'FAIL'}")
    lines.append(f"2. seen_unseen appears in top-3 PCs with |r|>0.4 -> best of PC1-3 is PC{su_best[0]} r={su_best[2]:.3f} -> "
                  f"{'PASS' if su_ok else 'FAIL'}")

    lines.append("\n## (e) Cosine similarities + nearest neighbours\n")
    pairs = [
        ("lighthouse", "love"),
        ("lighthouse", "nothingness"),
        ("love", "nothingness"),
        ("ghost", "lighthouse"),
        ("nyarlathotep", "lighthouse"),
    ]
    lines.append("| pair | cosine sim |")
    lines.append("|---|---|")
    id_index = {aid: i for i, aid in enumerate(ids)}
    for a, b in pairs:
        sim = cosine_sim(X[id_index[a]], X[id_index[b]])
        lines.append(f"| {a} <-> {b} | {sim:.4f} |")

    lines.append(f"\nNearest-{args.neighbours} neighbours:\n")
    for aid in ["lighthouse", "ghost", "nyarlathotep"]:
        nbrs = nearest_neighbours(ids, X, aid, args.neighbours)
        nbr_str = ", ".join(f"{n} ({s:.3f})" for n, s in nbrs)
        lines.append(f"- {aid}: {nbr_str}")

    if run_fallback is not None:
        lines.append("\n## Cross-model PC1 pole agreement\n")
        top_p, bottom_p = top_bottom(run_primary["ids"], run_primary["scores"], 0, args.top_n)
        top_f, bottom_f = top_bottom(run_fallback["ids"], run_fallback["scores"], 0, args.top_n)
        set_top_p, set_bottom_p = {a for a, _ in top_p}, {a for a, _ in bottom_p}
        set_top_f, set_bottom_f = {a for a, _ in top_f}, {a for a, _ in bottom_f}
        same_dir_overlap = len(set_top_p & set_top_f) + len(set_bottom_p & set_bottom_f)
        swapped_overlap = len(set_top_p & set_bottom_f) + len(set_bottom_p & set_top_f)
        lines.append(f"- primary PC1 high pole: {sorted(set_top_p)}")
        lines.append(f"- primary PC1 low pole: {sorted(set_bottom_p)}")
        lines.append(f"- fallback PC1 high pole: {sorted(set_top_f)}")
        lines.append(f"- fallback PC1 low pole: {sorted(set_bottom_f)}")
        lines.append(f"- same-direction overlap count: {same_dir_overlap}, swapped-direction overlap count: {swapped_overlap}")
        agreement = "same direction" if same_dir_overlap >= swapped_overlap else "swapped/flipped direction"
        lines.append(f"- verdict: models agree in {agreement} on PC1 poles (higher overlap side wins)")

    lines.append("\n## Plain reading (from the poles, not the labels)\n")
    top1, bottom1 = top_bottom(ids, scores, 0, args.top_n)
    top2, bottom2 = top_bottom(ids, scores, 1, args.top_n) if k >= 2 else (None, None)
    lines.append(f"1. PC1 high pole ({', '.join(a for a,_ in top1)}) vs low pole ({', '.join(a for a,_ in bottom1)}) — UNVERIFIED interpretation, read the poles above and fill in by hand.")
    if top2:
        lines.append(f"2. PC2 high pole ({', '.join(a for a,_ in top2)}) vs low pole ({', '.join(a for a,_ in bottom2)}) — UNVERIFIED interpretation, read the poles above and fill in by hand.")
    lines.append("3. UNVERIFIED — plain-language line 3, fill in from pole contents.")
    lines.append("4. UNVERIFIED — plain-language line 4, fill in from pole contents.")
    lines.append("5. UNVERIFIED — plain-language line 5, fill in from pole contents.")

    lines.append(f"\n![PC1xPC2 scatter]({Path(png_path).name})\n")

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text("\n".join(lines) + "\n")
    return sc_ok, sc_best, su_ok, su_best


def write_scatter(png_path, ids, scores):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.scatter(scores[:, 0], scores[:, 1])
    for i, aid in enumerate(ids):
        ax.annotate(aid, (scores[i, 0], scores[i, 1]), fontsize=8,
                     xytext=(3, 3), textcoords="offset points")
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.set_title("Nyari anchor-PCA: PC1 x PC2")
    ax.axhline(0, color="grey", linewidth=0.5)
    ax.axvline(0, color="grey", linewidth=0.5)
    Path(png_path).parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(png_path, dpi=150)
    plt.close(fig)


def main():
    args = parse_args()
    anchors = load_anchors(args.anchors)
    device = pick_device(args.device)
    png_path = args.png_out or str(Path(args.out).with_suffix(".png"))

    print(f"[anchor_pca] device={device} n_anchors={len(anchors)} model={args.model}", file=sys.stderr)

    try:
        run_primary = run_model(args.model, anchors, device, args.k)
        used_model = args.model
    except Exception as e:
        print(f"[anchor_pca] primary model {args.model} failed: {e}; falling back to {args.fallback_model}", file=sys.stderr)
        run_primary = run_model(args.fallback_model, anchors, device, args.k)
        used_model = args.fallback_model
        args.model = used_model  # report the model actually used as primary

    run_fallback = None
    if args.run_both_models and used_model != args.fallback_model:
        try:
            run_fallback = run_model(args.fallback_model, anchors, device, args.k)
        except Exception as e:
            print(f"[anchor_pca] fallback model {args.fallback_model} failed to load, skipping cross-model check: {e}", file=sys.stderr)
            run_fallback = None

    sc_ok, sc_best, su_ok, su_best = write_report(args.out, png_path, args, anchors, run_primary, run_fallback)
    write_scatter(png_path, run_primary["ids"], run_primary["scores"])

    ev = run_primary["explained_ratio"][:5]
    print("EXPLAINED_VARIANCE: " + ", ".join(f"PC{i+1}={v*100:.2f}%" for i, v in enumerate(ev)))
    top1, bottom1 = top_bottom(run_primary["ids"], run_primary["scores"], 0, args.top_n)
    top2, bottom2 = top_bottom(run_primary["ids"], run_primary["scores"], 1, args.top_n)
    print("PC1_HIGH: " + ", ".join(a for a, _ in top1))
    print("PC1_LOW: " + ", ".join(a for a, _ in bottom1))
    print("PC2_HIGH: " + ", ".join(a for a, _ in top2))
    print("PC2_LOW: " + ", ".join(a for a, _ in bottom2))
    print(f"PREREG_STAY_CROSS: PC{sc_best[0]} r={sc_best[1]:.3f} -> {'PASS' if sc_ok else 'FAIL'}")
    print(f"PREREG_SEEN_UNSEEN: PC{su_best[0]} r={su_best[2]:.3f} -> {'PASS' if su_ok else 'FAIL'}")
    print(f"Report written to {args.out}")
    print(f"Scatter written to {png_path}")


if __name__ == "__main__":
    main()

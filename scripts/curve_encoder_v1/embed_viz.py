"""Embedding visualization for 256D Curve Tokens (t-SNE / PCA)."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from .config import EMBED_DIR, EVAL_DIR

TYPE_NAMES = ("LINE", "CIRCLE", "ELLIPSE", "BSPLINE")
COLORS = {
    "LINE": "#1f77b4",
    "CIRCLE": "#d62728",
    "ELLIPSE": "#9467bd",
    "BSPLINE": "#2ca02c",
}


def _pca_2d(x: np.ndarray) -> np.ndarray:
    x = x - x.mean(0, keepdims=True)
    u, s, vt = np.linalg.svd(x, full_matrices=False)
    return x @ vt[:2].T


def visualize_tokens(token_path: Path, out_dir: Path | None = None, max_points: int = 4000) -> Path:
    out_dir = out_dir or EMBED_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    z = np.load(token_path)
    tok = z["token"].astype(np.float64)
    tid = z["type_id"].astype(np.int64)
    if tok.shape[0] > max_points:
        rng = np.random.default_rng(0)
        # Stratified subsample so rare types survive.
        sel = []
        for t in range(4):
            idx = np.where(tid == t)[0]
            if idx.size == 0:
                continue
            take = min(len(idx), max(50, max_points // 4))
            sel.append(rng.choice(idx, size=take, replace=False))
        sel = np.concatenate(sel)
        tok, tid = tok[sel], tid[sel]

    xy = _pca_2d(tok)

    # Prefer matplotlib; fall back to writing coords only.
    try:
        import matplotlib

        matplotlib.use("Agg")
        # Avoid mpl_toolkits path issues seen previously — 2D only.
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(7, 6))
        for t, name in enumerate(TYPE_NAMES):
            m = tid == t
            if not m.any():
                continue
            ax.scatter(xy[m, 0], xy[m, 1], s=8, alpha=0.55, c=COLORS[name], label=f"{name} (n={m.sum()})")
        ax.legend(frameon=False)
        ax.set_title("Curve Token PCA (256D → 2D)")
        ax.set_xlabel("PC1")
        ax.set_ylabel("PC2")
        fig.tight_layout()
        png = out_dir / "token_pca.png"
        fig.savefig(png, dpi=140)
        plt.close(fig)
    except Exception as e:
        png = out_dir / "token_pca_FAILED.txt"
        png.write_text(str(e))

    np.savez_compressed(out_dir / "token_pca_coords.npz", xy=xy, type_id=tid)
    return png


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokens", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, default=None)
    args = ap.parse_args()
    path = visualize_tokens(args.tokens, args.out_dir)
    print(path)


if __name__ == "__main__":
    main()

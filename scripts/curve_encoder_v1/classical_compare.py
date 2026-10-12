"""Classical fitting vs neural encoder on the same noisy / partial test conditions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from curve_token_v1.fit_curves_from_points import fit_circle, fit_ellipse, fit_line

from .config import CACHE_DIR, EVAL_DIR, NOISE_LEVELS, PARTIAL_FRACS
from .metrics import _angle_deg, _summarize, confusion_and_f1


def _partial_indices(n: int, frac: float, closed: bool, rng: np.random.Generator) -> np.ndarray:
    keep = max(2, int(round(frac * n)))
    if closed:
        start = int(rng.integers(0, n))
        return np.array([(start + k) % n for k in range(keep)], dtype=np.int64)
    start = int(rng.integers(0, max(1, n - keep + 1)))
    return np.arange(start, start + keep, dtype=np.int64)


def classical_on_cache(
    split: str = "test",
    noise_rel: float = 0.0,
    partial_frac: float = 1.0,
    target_diagonal: float = 6.0,
    seed: int = 0,
    max_curves: int | None = None,
) -> dict:
    z = np.load(CACHE_DIR / "curves_cache.npz", allow_pickle=True)
    split_id = {"train": 0, "val": 1, "test": 2}[split]
    idx = np.where(z["encoder_split"] == split_id)[0]
    if max_curves is not None and len(idx) > max_curves:
        rng0 = np.random.default_rng(seed)
        idx = np.sort(rng0.choice(idx, size=max_curves, replace=False))

    type_true, type_pred = [], []
    line_dir, circ_n, circ_r, ell_ax = [], [], [], []
    ok_flags = []

    print(f"  classical fitting {len(idx)} curves  noise={noise_rel} partial={partial_frac}", flush=True)
    for k, j in enumerate(idx):
        if (k + 1) % 500 == 0:
            print(f"    classical {k+1}/{len(idx)}", flush=True)
        rng = np.random.default_rng(seed + 13 * int(j) + 3)
        xyz = z["xyz_n"][j].astype(np.float64).copy()
        tid = int(z["type_id"][j])
        closed = bool(z["is_closed"][j])
        params = z["params"][j].astype(np.float64).copy()

        if partial_frac < 1.0 - 1e-9:
            sel = _partial_indices(xyz.shape[0], partial_frac, closed, rng)
        else:
            sel = np.arange(xyz.shape[0], dtype=np.int64)
        pts = xyz[sel]
        if noise_rel > 0:
            pts = pts + rng.normal(0.0, noise_rel * target_diagonal, size=pts.shape)
        # Match neural encoder: curve-local frame from observed points.
        centroid = pts.mean(axis=0)
        pts = pts - centroid
        params[0:3] = params[0:3] - centroid

        # Classical fitter is type-oracle for a fair param-error comparison, but we
        # also try all types and pick lowest residual for type accuracy.
        candidates = []
        try:
            candidates.append(("LINE", fit_line(pts), None))
        except Exception as e:
            candidates.append(("LINE", {"ok": False}, str(e)))
        try:
            candidates.append(("CIRCLE", fit_circle(pts), None))
        except Exception as e:
            candidates.append(("CIRCLE", {"ok": False}, str(e)))
        try:
            candidates.append(("ELLIPSE", fit_ellipse(pts), None))
        except Exception as e:
            candidates.append(("ELLIPSE", {"ok": False}, str(e)))

        # Choose by rms residual among successful fits. BSPLINE GT → classical cannot
        # win type match via analytic fitters here; mark as OTHER-like failure.
        best = None
        best_rms = float("inf")
        for name, fit, _ in candidates:
            if fit.get("ok", True) is False and "rms_residual" not in fit:
                continue
            rms = float(fit.get("rms_residual", 1e9))
            if rms < best_rms:
                best_rms = rms
                best = (name, fit)
        if best is None:
            pred_tid = -1
            ok_flags.append(False)
        else:
            pred_name, fit = best
            pred_tid = {"LINE": 0, "CIRCLE": 1, "ELLIPSE": 2}.get(pred_name, -1)
            ok_flags.append(True)

            # Oracle-type param errors (use GT type's fitter) for geometry metrics.
            if tid == 0:
                fl = fit_line(pts)
                ang = _angle_deg(
                    np.asarray(fl["direction"], dtype=np.float64)[None],
                    params[3:6][None],
                    abs_cos=True,
                )[0]
                line_dir.append(ang)
            elif tid == 1:
                fc = fit_circle(pts)
                if fc.get("ok", True):
                    circ_n.append(
                        _angle_deg(
                            np.asarray(fc["normal"], dtype=np.float64)[None],
                            params[3:6][None],
                            abs_cos=True,
                        )[0]
                    )
                    circ_r.append(abs(float(fc["radius"]) - float(params[6])))
            elif tid == 2:
                fe = fit_ellipse(pts)
                if fe.get("ok", True):
                    ell_ax.append(
                        _angle_deg(
                            np.asarray(fe["major_axis"], dtype=np.float64)[None],
                            params[6:9][None],
                            abs_cos=True,
                        )[0]
                    )

        type_true.append(tid)
        # Map failed / bspline-as-analytic to a wrong class (3) so F1 reflects miss.
        type_pred.append(pred_tid if pred_tid >= 0 else 3)

    type_true = np.asarray(type_true, dtype=np.int64)
    type_pred = np.asarray(type_pred, dtype=np.int64)
    # Restrict classification metrics to LINE/CIRCLE/ELLIPSE (classical has no BSPLINE head).
    analytic = type_true <= 2
    clf = confusion_and_f1(type_true[analytic], type_pred[analytic], n_types=4)
    return {
        "n": int(len(idx)),
        "n_analytic": int(analytic.sum()),
        "noise_rel": noise_rel,
        "partial_frac": partial_frac,
        "fit_success_rate": float(np.mean(ok_flags)) if ok_flags else 0.0,
        "classification_analytic_only": clf,
        "CURVE_TYPE_MACRO_F1_analytic": clf["macro_f1"],
        "LINE_DIRECTION_ERROR": _summarize(np.asarray(line_dir, dtype=np.float64)),
        "CIRCLE_NORMAL_ERROR": _summarize(np.asarray(circ_n, dtype=np.float64)),
        "CIRCLE_RADIUS_ERROR": _summarize(np.asarray(circ_r, dtype=np.float64)),
        "ELLIPSE_AXIS_ERROR": _summarize(np.asarray(ell_ax, dtype=np.float64)),
    }


def run_classical_suite(out_dir: Path | None = None, max_curves: int | None = None) -> dict:
    out_dir = out_dir or (EVAL_DIR / "classical_fitting")
    out_dir.mkdir(parents=True, exist_ok=True)
    suite = {"clean": None, "noise": {}, "partial": {}}
    suite["clean"] = classical_on_cache(noise_rel=0.0, partial_frac=1.0, max_curves=max_curves)
    # Skip 0.0 / 1.0 — already covered by clean.
    for n in NOISE_LEVELS:
        if n <= 0:
            continue
        suite["noise"][f"{n:g}"] = classical_on_cache(
            noise_rel=n, partial_frac=1.0, max_curves=max_curves, seed=11
        )
    for f in PARTIAL_FRACS:
        if abs(f - 1.0) < 1e-12:
            continue
        suite["partial"][f"{f:g}"] = classical_on_cache(
            noise_rel=0.0, partial_frac=f, max_curves=max_curves, seed=22
        )
    # Mirror clean into the noise/partial tables for report convenience.
    suite["noise"]["0"] = suite["clean"]
    suite["partial"]["1"] = suite["clean"]
    (out_dir / "classical_suite.json").write_text(json.dumps(suite, indent=2))
    return suite


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-curves", type=int, default=None)
    args = ap.parse_args()
    suite = run_classical_suite(max_curves=args.max_curves)
    print(json.dumps({"clean_macro_f1": suite["clean"]["CURVE_TYPE_MACRO_F1_analytic"],
                      "noise_1e-3": suite["noise"].get("0.001")}, indent=2))


if __name__ == "__main__":
    main()

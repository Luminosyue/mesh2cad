#!/usr/bin/env python3
"""Train SpatialLM with the Curve Token stream.

Installs the runtime patches, then hands over to SpatialLM's own ``run_exp``, so
the training loop, optimizer and freezing logic are byte-identical to J0/J2.

    python3 scripts/spatiallm_curve_token_v1/train_curve_token_spatiallm.py \
        scripts/spatiallm_curve_token_v1/configs/curve100_m2_curvetoken.yaml
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SPATIALLM_ROOT = REPO_ROOT / "SpatialLM"
for p in (str(SPATIALLM_ROOT), str(REPO_ROOT / "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)


def main() -> int:
    if len(sys.argv) < 2:
        raise SystemExit(f"usage: {sys.argv[0]} <config.yaml>")
    config = Path(sys.argv[1]).resolve()
    if not config.is_file():
        raise SystemExit(f"config not found: {config}")

    # Relative paths inside the SpatialLM configs (models/, saves/, ../dataset)
    # are resolved against the SpatialLM root.
    os.chdir(SPATIALLM_ROOT)

    # This entrypoint is exclusively for the curve-token M2 arm. Set the
    # model-side flag before SpatialLM imports/builds the model factory.
    os.environ.setdefault("CAD_SECOND_STREAM", "curve_tokens")
    os.environ.setdefault("CAD_USE_SEPARATE_EDGE_TOKENS", "1")

    from spatiallm_curve_token_v1 import curve_token_injector

    curve_token_injector.install()

    from spatiallm.tuner.trainer import run_exp

    sys.argv = [sys.argv[0], str(config)]
    run_exp()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

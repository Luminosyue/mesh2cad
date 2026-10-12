#!/usr/bin/env python3
"""CLI wrapper: build the shared 4096-surface-index cache for heldout_best_v2."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from spatiallm_curve_token_v1.surface_cache import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())

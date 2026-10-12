"""Track B Curve Encoder Baseline V1 — Geometry-only Curve Tokens.

Answers: looking only at one curve's (noisy) sampled points, can a network learn
a stable curve representation?

Does NOT connect to Qwen / LLM. Does NOT modify Track A.
"""

from __future__ import annotations

__all__ = ["config"]

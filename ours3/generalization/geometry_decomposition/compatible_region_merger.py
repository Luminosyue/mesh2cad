from __future__ import annotations

from .schema import RefinedPart


def merge_compatible_regions(parts: list[RefinedPart]) -> list[RefinedPart]:
    """Conservative V1: avoid over-merging until parameter-equivalence is proven."""
    return parts


from copy import deepcopy

from .routing_policy import select_candidate


class CandidateOrchestrator:
    """Unifies Qwen, MAC, and geometry candidates before terminal selection."""

    def __init__(self, allowed_builders):
        self.allowed_builders = tuple(allowed_builders)
        self.candidates = []

    def register(self, candidate):
        # Validation may contain live OCC topology evidence (TopoDS_Face), which is
        # intentionally read-only and cannot be pickled/deep-copied.
        item = dict(candidate)
        if "plan" in item:
            item["plan"] = deepcopy(item["plan"])
        item.setdefault("candidate_id", f"CANDIDATE_{len(self.candidates):03d}")
        builder = item.get("builder")
        if builder and builder not in self.allowed_builders:
            item.update(hard_reject=True, safety_pass=False, reject_reason="BUILDER_NOT_ELIGIBLE")
        self.candidates.append(item)
        return item

    def select(self):
        return select_candidate(self.candidates)

    def summary(self):
        winner, rejected = self.select()
        return {
            "candidate_count": len(self.candidates),
            "winning_candidate": winner,
            "rejected_candidates": rejected,
            "allowed_builders": list(self.allowed_builders),
        }

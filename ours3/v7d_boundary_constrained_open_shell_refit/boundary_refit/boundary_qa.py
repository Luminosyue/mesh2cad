"""Formal-vs-diagnostic V7D gate semantics."""

def formal_candidate_accepted(evidence_status, geometry_regression, preview_buildable):
    return evidence_status == "VALID" and not geometry_regression and preview_buildable


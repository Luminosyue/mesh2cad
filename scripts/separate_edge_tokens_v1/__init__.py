"""Separate Edge Point Tokens V1.

Surface and sharp-edge geometry are carried as two independent point clouds,
encoded by one shared pretrained Sonata, and injected into the LLM through two
separate projectors and two special-token regions.

This package is additive: nothing here is imported by the 6-channel baseline or
the 7-channel edge_score experiment.
"""

EXPERIMENT_NAME = "separate_edge_tokens_v1"

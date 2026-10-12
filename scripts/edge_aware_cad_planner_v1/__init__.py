"""Edge-aware CAD Planner (Step 2): Geometry → Feature Planner → DSL → OCC/STEP.

Does NOT train an LLM. Does NOT feed raw 8192 points to the model.
Does NOT build full BRep wires (Point2CAD Route B). Light circle candidates only.
"""

from .geometry_summary import build_geometry_summary, render_cad_brief
from .cad_feature_planner import plan_cad_features, render_operation_plan
from .cad_dsl import execute_dsl, parse_dsl

__all__ = [
    "build_geometry_summary",
    "render_cad_brief",
    "plan_cad_features",
    "render_operation_plan",
    "parse_dsl",
    "execute_dsl",
]

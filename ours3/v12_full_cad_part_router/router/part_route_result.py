from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PartRouteResult:
    case_id: str
    part_id: str
    semantic_role: str
    status: str
    allowed_builders: List[str]
    ranked_builders: List[str]
    selected_candidate_source: Optional[str] = None
    selected_builder: Optional[str] = None
    fresh_brep: bool = False
    historical_step_reused: bool = False
    runtime_remeasurement: bool = False
    blocker: Optional[str] = None
    source_mesh: Optional[str] = None
    source_mesh_sha256: Optional[str] = None
    step_path: Optional[str] = None
    step_sha256: Optional[str] = None
    geometry_qa: Dict[str, Any] = field(default_factory=dict)
    fidelity_qa: Dict[str, Any] = field(default_factory=dict)
    nativeness_qa: Dict[str, Any] = field(default_factory=dict)
    candidate_count: int = 0
    candidate_ids: List[str] = field(default_factory=list)
    transform_metadata: Dict[str, Any] = field(default_factory=dict)
    tts_selection_reason: Optional[str] = None
    tts_rejected_candidates: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)

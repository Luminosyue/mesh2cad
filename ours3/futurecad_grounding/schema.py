from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

TargetType = Literal['FACE', 'EDGE', 'VERTEX']
SelectionMode = Literal['TOP_K', 'ALL_MATCHES', 'EXACT_COUNT']


@dataclass(frozen=True)
class PrimitiveGroundingQuery:
    target_type: TargetType
    natural_language_query: str
    structured_constraints: dict[str, Any] = field(default_factory=dict)
    expected_count: int = 1
    selection_mode: SelectionMode = 'EXACT_COUNT'
    confidence_requirement: float = 0.60

    def __post_init__(self) -> None:
        if self.target_type not in {'FACE', 'EDGE', 'VERTEX'}:
            raise ValueError('PRIMITIVE_TYPE_MISMATCH')
        if self.expected_count < 1:
            raise ValueError('EXPECTED_COUNT_INVALID')

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GroundingCandidate:
    primitive_id: str
    geometry_score: float
    semantic_position_score: float
    topology_score: float
    query_match_score: float
    total_score: float
    evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GroundingResult:
    status: str
    backend_name: str
    inventory_version: str
    query_hash: str
    selected_runtime_ids: list[str] = field(default_factory=list)
    ranked_candidates: list[GroundingCandidate] = field(default_factory=list)
    confidence: float = 0.0
    reject_reason: str | None = None

    @property
    def valid(self) -> bool:
        return self.status == 'GROUNDING_VALID'

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value['valid'] = self.valid
        return value


@dataclass(frozen=True)
class FeatureOperationPlan:
    operation: Literal['FILLET', 'CHAMFER', 'SHELL']
    target_grounding_query: PrimitiveGroundingQuery
    parameter_refs: dict[str, str]
    operation_id: str
    diagnostic_only: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FutureCADProgramProposal:
    proposal_id: str
    base_feature_sequence: list[dict[str, Any]]
    grounding_queries: list[dict[str, Any]]
    numeric_parameter_placeholders: dict[str, str]
    feature_dependencies: dict[str, list[str]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

"""FutureCAD-inspired transient BRep primitive grounding interface."""

from .schema import (
    FeatureOperationPlan,
    FutureCADProgramProposal,
    GroundingCandidate,
    GroundingResult,
    PrimitiveGroundingQuery,
)
from .primitive_inventory import BRepPrimitiveInventory, PartLocalFrame, PrimitiveInventoryBuilder
from .deterministic_grounder import DeterministicBRepGrounder
from .grounding_resolver import GroundingResolver, StaleRuntimePrimitiveError
from .feature_execution_loop import FeatureExecutionLoop

__all__ = [
    'BRepPrimitiveInventory', 'DeterministicBRepGrounder', 'FeatureExecutionLoop',
    'FeatureOperationPlan', 'FutureCADProgramProposal', 'GroundingCandidate',
    'GroundingResolver', 'GroundingResult', 'PartLocalFrame',
    'PrimitiveGroundingQuery', 'PrimitiveInventoryBuilder',
    'StaleRuntimePrimitiveError',
]

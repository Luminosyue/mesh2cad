# V7D2A Chain Identity Evidence Audit

## Outcome

The audit passed. No recovery/refit operation was executed. The FUSELAGE 4/9 ceiling is upstream of V7D1 DAG scoring: all 12 stations have raw intersections, but only 9 stations contain any saved open chain and only S03-S06 contain the two measured chain identities needed to form a seam endpoint pair.

The saved `raw_segment_graph` objects are count summaries only; graph nodes/edges were not persisted. Therefore option A cannot reconstruct the missing FUSELAGE chain geometry from current artifacts. A versioned, offline Geometry Analyzer extraction must persist every raw graph component and its ordered coordinates. Runtime remeasurement remains forbidden.

## Vertical-tail direction audit

The two global-path spikes occur at S04 and S05. The persisted chain geometry alternates by about 178 degrees across adjacent stations despite `orientation_flips_fixed=7`. The implementation reverses point arrays but does not recompute the descriptor later used as the preceding orientation reference. Consequently endpoint indices no longer denote stable physical endpoints; endpoint-state changes line up with the 171.07 and 173.77 degree path turns.

## Coverage semantics

- Raw section: fraction of the 12 requested stations with a measured intersection.
- Open chain: union of stations represented by either selected seam track, divided by 12 requested stations.
- Chain identity and endpoint evidence: stations shared by both selected tracks, divided by their open-chain union support. This preserves the V7D1 4/9 and 6/8 physical ceilings.

## Prohibited operations

DAG weights unchanged; no interpolation, Master Curve, constrained refit, V7C, Sewing, or runtime geometry remeasurement was executed.

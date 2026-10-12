# V7D2B Versioned Chain Evidence Regeneration and Identity Repair

## Gate decision

`V7D2B_VERSIONED_CHAIN_EVIDENCE_REGEN_AND_IDENTITY_REPAIR_PARTIAL`. Evidence persistence and descriptor safety repairs pass, but track recovery does not. No Master Curve, control net, constrained refit, V7C, pcurve, trim, Sewing, Qwen, MAC, or PhysX operation was executed.

## FUSELAGE root cause

All 12 authoritative planes were regenerated from the unchanged measured axis and station planes. S00, S01, and S07 are real closed cycles. S02 and S08-S11 contain exactly one connected simple open component. Only S03-S06 contain at least two trackable open components. Thus the 4/9 seam ceiling is a property of these section observations, not lost serialization, filtering, clustering, or the V7D1 DAG. Four additional components that V7B did not serialize were valid open chains, but all occur inside S03-S06 and do not extend station support. Four tiny open components were retained as rejected evidence rather than silently discarded.

Endpoint clustering showed zero potential over-merges and zero under-merges under the unchanged part-relative tolerance. Every graph now contains node coordinates, source-segment-bound edges, component membership, filters, and rejected geometry.

## VERTICAL_TAIL result

The stale-descriptor bug and dirty/hash guard were repaired: mutating geometry without recomputation is rejected, and reversing with recomputation changes the descriptor hash while keeping geometry/descriptor hashes consistent. Nevertheless, the identical frozen V7D1 tracker still reports two direction flips and two curvature spikes. Therefore stale descriptors were a real defect but not a sufficient cause of the S04/S05 global-path turns; tail geometric branch/chain identity remains ambiguous.

## Required answers

1. FUSELAGE only had two trackable chains at S03-S06 because the other supporting sections physically contain one simple open component; S00/S01/S07 are closed cycles.
2. Offline regeneration recovered the second chain at 0 additional stations.
3. Four previously unpersisted components are valid open chains, all within already-supported S03-S06.
4. No endpoint clustering over-merge or under-merge was detected.
5. FUSELAGE chain identity coverage remains 44.44% (4/9).
6. The tail spikes are not fully caused by the stale descriptor: the defect is reproduced and fixed, but the spikes remain.
7. Both direction reversals do not disappear in the frozen tracker; count remains 2.
8. Canonical chain endpoint identity swaps are 0, but the selected seam path remains invalid.
9. V7D1 DAG weights were not adjusted.
10. Neither part has a valid seam track under the frozen Track Gate.
11. The project is not ready to re-enter Master Curve/control-net/refit.
12. Next choice: FUSELAGE needs a different physical seam evidence formulation for mixed closed/open stations, while the immediate allowed branch is C: continue tail chain identity matching. Do not run V7C.

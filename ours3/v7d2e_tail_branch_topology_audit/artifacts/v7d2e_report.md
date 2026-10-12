# V7D2E Vertical Tail Branch/Topology/Adaptive Station Audit

Gate: **V7D2E_VERTICAL_TAIL_BRANCH_TOPOLOGY_AND_ADAPTIVE_STATION_AUDIT_PASS**

Root cause: **MISSING_INTERMEDIATE_STATION_EVIDENCE** (high confidence). The proximate mechanism is mixed-section serialization loss at S06.

## 1. Why S06 was absent

The source section exists, but the station-level VALID_SINGLE_LOOP serialization discarded three simultaneously present open chains, including dominant COMP_000.

## 2. Was there a usable S06 chain

Yes. 276 raw segments form 4 components: 3 open chains and 1 closed loop. Dominant open COMP_000 has arc length 0.915609.

## 3. Is S07 current branch strongest

Yes. The dominant COMP_000 branch is the source-supported continuation and the local anchored branch ranks first.

## 4. Is there a smoother weaker branch

Yes=True; small-fragment alternatives can be numerically smoother but have weaker whole-chain/length continuity.

## 5. Was it correctly rejected

Yes. Source evidence authority dominates aesthetic smoothness; no CAD/GT metric was consulted.

## 6. Adaptive trajectory

Seven versioned offline stations reduce the S07 long-chord turn from 100.679397 to 48.527716 degrees.

## 7. World-space event

The old coarse trajectory spike exists in world space; after source-measured refinement the >90 degree event disappears.

## 8. Local-frame artifact

No. All saved frames are identical, right-handed, and have zero inter-frame rotation; world/local conclusions agree.

## 9. Section topology

Yes. S06 is MIXED_OPEN_CLOSED and exhibits branch birth/death, which caused the legacy station-level serialization loss.

## 10. Flip or bend

It is not an identity flip. The dominant physical branch persists; one smaller source-supported geometric turn remains after refinement.

## 11. Keep zero-spike requirement

For this event no contract relaxation is needed: measured refinement removes the >90 degree spike without smoothing or threshold changes.

## 12. Why not smooth if true bend

Not applicable to the old 100.68 degree event; in general measured source bends must remain because smoothing would replace evidence with an aesthetic prior.

## 13. Next step

B. V7D2F_ADAPTIVE_STATION_SEAM_RECOVERY, using V7D2E_ADAPTIVE_TAIL evidence and representation-aware handling of the S06 mixed section.

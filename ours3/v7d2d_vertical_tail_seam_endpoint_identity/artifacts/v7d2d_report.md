# V7D2D Vertical-Tail Seam Endpoint Identity Disambiguation

## Gate

`V7D2D_VERTICAL_TAIL_SEAM_ENDPOINT_IDENTITY_DISAMBIGUATION_PARTIAL`. FUSELAGE and the accepted Tail whole-chain track remained byte-for-byte frozen. Endpoint-side identity was separated from endpoint array index and solved jointly for two seams, but the physical endpoint samples on the frozen chain cannot satisfy the zero-flip/zero-spike Gate.

## Required answers

1. V7D2C retained one flip because a valid whole-chain identity does not guarantee that either boundary endpoint trajectory is smooth; S05-S07-S08 bends sharply on the measured TRACK_0 endpoints.
2. The old remaining spike is centered at S07, between S05 and S08.
3. It is not caused solely by selecting endpoint_0 versus endpoint_1 incorrectly. Exhaustive audit of all 2^8 joint FORWARD/SWAP sequences found minimum combined flips=1 and spikes=3 for the two seams; no zero/zero sequence exists.
4. Endpoint array indices and physical SIDE_A/SIDE_B are decoupled by joint state assignments.
5. Physical side identity remains stable through orientation changes; synthetic array swapping preserves the physical seam.
6. Global DP prevents local state chatter and is no worse than greedy, but cannot remove geometry inherent in the frozen chain endpoints.
7. Combined two-seam flips do not reach zero; they remain 1.
8. Combined spikes do not reach zero; the selected two physical boundaries contain 3 total spikes.
9. Maximum P95 remains 1.4518209642 rad, so it does not significantly improve.
10. TAIL_SEAM_A is not valid under the strict Gate.
11. TAIL_SEAM_B is also not valid under the strict Gate.
12. The two seam assignments always use distinct endpoints at each station.
13. Synthetic endpoint array swapping does not alter physical seam identity.
14. No Chamfer or Hausdorff metric was used.
15. FUSELAGE stayed frozen with two 100% seams.
16. TRACK_RECOVERY_READY_FOR_V7D remains false.
17. V7D/V7C must not run.
18. Remaining class is B: CHAIN_GEOMETRY_AMBIGUOUS. With the accepted chain frozen, endpoint identity alone cannot satisfy the requested topology; the next task must revisit the physical whole-chain branch or seam topology rather than tune endpoint weights.

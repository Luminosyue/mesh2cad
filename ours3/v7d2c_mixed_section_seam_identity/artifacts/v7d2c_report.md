# V7D2C Mixed-Section Seam and Tail Chain Identity Recovery

## Gate

`V7D2C_MIXED_SECTION_SEAM_AND_TAIL_CHAIN_IDENTITY_RECOVERY_PARTIAL`. FUSELAGE mixed-section recovery passes, but the Tail seam Track Gate remains partial. Production Master Curve count is zero; Common Control Net, refit, and V7C were not executed.

## Required answers

1. The old 44.4% was not an extraction bug. It was the representation assumption `two open chains per station`; measured FUSELAGE sections legitimately transition among closed loop, single open chain, and multi-open chain.
2. A closed loop contributes latent seam candidates sampled by normalized arc length. Selection is anchor-first and jointly optimized in the station-local frame.
3. No latent point leaves the measured loop; every selected XYZ is one of its measured arc-length samples.
4. A single open chain contributes its two real endpoints to SEAM_A and SEAM_B; it is never duplicated into two chains.
5. S03-S06 are the multi-open high-confidence anchor stations.
6. Both FUSELAGE seam evidence coverages rise from 44.4% to 100%; observed-only support is 75% and latent support is 25%.
7. Two continuous FUSELAGE diagnostic seam tracks are recovered with zero direction flips. They are evidence tracks, not production Master Curves.
8. The old Tail tracker selected locally compatible endpoint pairs before resolving whole-chain branch identity, allowing the chosen point trajectory to reverse near S04/S05.
9. Whole-chain matching selects the persistent longitudinal TRACK_0 branch. It removes one of two old flips/spikes, but S04/S05-derived geometry still has a large turn.
10. Tail flips reduce from 2 to 1, not zero.
11. Curvature spikes reduce from 2 to 1 and P95 from 3.0257 to 1.4518 rad, but remain above Gate.
12. V7D1 DAG weights do not need and were not adjusted.
13. The project is not yet ready for Master Boundary/Common Control Net because the Tail valid seam track count is zero.
14. Next allowed choice is C: continue Tail whole-chain-derived seam identity. Do not run V7C.

# V7A Robust Closed Profile Recovery Report

## Gate

`CURRENT_GATE=V7A_ROBUST_PROFILE_RECOVERY_PARTIAL`

The result is deliberately **PARTIAL**. Across 36 requested CASE09 subset stations, 18 are truthful triangle-plane closed profiles (50.0%); zero profiles were repaired and zero fallback profiles were created. Both contractual pass thresholds remain unmet.

## Per-part outcome

| Part | Watertight | True closed | Small-gap repair | Open shell | Closed rate |
|---|---:|---:|---:|---:|---:|
| MAIN_WING / CADPART_001 | false | 11 | 0 | 1 | 91.7% |
| FUSELAGE / CADPART_000 | false | 3 | 0 | 9 | 25.0% |
| VERTICAL_TAIL / CADPART_005 | false | 4 | 0 | 8 | 33.3% |

True section stations:

- MAIN_WING: `['S00', 'S01', 'S02', 'S03', 'S04', 'S05', 'S06', 'S07', 'S08', 'S09', 'S10']`
- FUSELAGE: `['S00', 'S01', 'S07']`
- VERTICAL_TAIL: `['S06', 'S09', 'S10', 'S11']`

Small-gap repaired stations: `{'CADPART_001': [], 'CADPART_000': [], 'CADPART_005': []}`. Adaptive station shifts selected: `{'CADPART_001': [], 'CADPART_000': [('S00', 0.03, 0.027999999999999997)], 'CADPART_005': [('S06', 0.5427272727272727, 0.5387272727272727)]}`.

## Answers to the ten required questions

1. **Why was the old closed rate only 16.7%?** V7 delegated topology to `trimesh.section().discrete` and then required the returned point array to repeat its first point within a fixed span-relative tolerance. It had no direct triangle-plane segment provenance, endpoint clustering, degree graph, cycle extraction, multi-loop containment, or guarded repair. V7A removes that false-negative mechanism, but the modest gain from 16 to 18 also proves that most remaining failures are not merely that software check.

2. **Dominant failure source?** Source geometry. All three selected source Parts are non-watertight. Fuselage and vertical tail repeatedly produce one or multiple real open chains. No selected profile required a nonzero adaptive station shift, and no open chain met the strict 0.3% normalized small-gap bridge rule. Thus neither station placement nor harmless endpoint noise is the dominant blocker.

3. **Which profiles are true triangle-plane closed loops?** The exact station lists are printed above and stored per station in the geometry analysis JSON. All 18 carry `source=HIGH_POLY_TRIANGLE_PLANE_INTERSECTION` plus raw segment, graph, loop and curve provenance.

4. **Which profiles used small-gap repair?** None. `SMALL_GAP_REPAIRED_PROFILE_RATE=0.0` and every repair list is empty.

5. **Any bbox, convex-hull, ellipse, rectangle, neighbor-copy or other fake closure?** No. `FALLBACK_PROFILE_RATE=0.0`. Those operations are absent from recovery and runtime paths.

6. **Which Part is hardest?** Fuselage by measured closed rate (25%, versus vertical tail 33.3% and main wing 91.7%). Both fuselage and vertical tail are predominantly open-shell sections.

7. **Does LoftBuilder consume the new measured profiles?** Yes. Runtime accepts only valid V7A profile types with triangle-plane provenance and consumes their 64-point numerical representation through one smooth periodic interpolated curve per section. It does not re-section the source mesh, and the sampled polyline is explicitly marked sampling-only.

8. **Do profile perturbations change the BRep?** Yes. Scaling one measured wing profile width to 0.8 changed the STEP SHA-256; swapping S03 and S07 profiles also changed it. An `INVALID_PROFILE` was rejected before building.

9. **What is the remaining technical problem?** For the main wing, robust closed extraction is essentially solved at the measured stations. For fuselage and vertical tail the next honest problem is open-shell upper/lower-chain reconstruction or upstream watertight source repair—not more aggressive forced closure. Upper/lower chains are retained for that future stage.

10. **Ready for complete CASE09 reconstruction?** No. The truthful profile thresholds are unmet, only the three-part contract-validation subset is in scope, and the other CASE09 parts remain outside V7A. The runtime/data-dependency contract is ready; full geometry recovery is not.

## Contract and quality evidence

- V7A tests: 16 passed.
- Untouched V7 regression tests: 35 passed.
- Total: 51 passed, 0 failed.
- V7 contract remains closed: measured axis, measured station and measured profile sources; zero runtime remeasurement, regeneration, clamping or silent overrides.
- Smooth fit aggregate: mean error `0.00024405338335815516`, profile-P95 aggregate `0.000833010806428321`.
- Final STEP is explicitly a three-part validation subset, not a complete CASE09 assembly.

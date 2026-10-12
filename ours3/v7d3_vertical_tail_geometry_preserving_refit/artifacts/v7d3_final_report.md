# V7D3 Vertical Tail Geometry-Preserving Local Boundary Refit

- 1. V7D shared topology was correct because both faces used one OCC edge with two pcurves; fidelity regressed because it rebuilt the shared core globally as a 3x64 net.
- 2. Control-net audit found global drift=True; repaired-master causal=False. Primary cause=REFIT_TOO_GLOBAL.
- 3. The accepted Tail endpoint assignment contains a flip=True; the bounded identity-repair ablation was executed.
- 4. Global max displacement=0.5943134801226805; local max=0.5621781037522369.
- 5. Local-only movement is proven by boundary-strip movement rate=1.0.
- 6. Far-interior V7B preservation: RMS=0.0, P95=0.0.
- 7. The same OCC edge is present in both trimmed faces=True.
- 8. Both pcurves were revalidated=True; P95 3D error=1.11929294177293e-16.
- 9. Valid trimmed faces=2.
- 10. Chamfer V7B/V7D/V7D3=0.010298782545970303/0.023507918076213743/0.010384239294602613.
- 11. Hausdorff V7B/V7D/V7D3=0.25303765500752023/0.47054985066586297/0.2533517329526479.
- 12. SIDE Hausdorff changed from 0.47054985066586297 to 0.2533517329526479.
- 13. V7B-like geometry plus V7D-like shared topology achieved=True.
- 14. FUSELAGE was not modified; hash-equality regression pass=True.
- 15. Formal upgrade to PASS=True; current gate=V7D3_VERTICAL_TAIL_GEOMETRY_PRESERVING_LOCAL_BOUNDARY_REFIT_PASS.
- 16. If PASS, next work can return to V9 per-semantic primitive selector, Qwen Plan-to-Builder, then full CASE09 router.
- 17. If PARTIAL, blocker class=B. local deformation model insufficient; pcurve/trim/topology gates passed=True.

## Evidence

```json
{
  "CURRENT_GATE": "V7D3_VERTICAL_TAIL_GEOMETRY_PRESERVING_LOCAL_BOUNDARY_REFIT_PASS",
  "CASE09_V7D3_PASS": true,
  "FUSELAGE_FROZEN": true,
  "FUSELAGE_INPUT_HASH": "9f714ab21eb24c831fb6c81a1e03bafa26c920c082d3a4008a03402ede218abc",
  "FUSELAGE_OUTPUT_HASH": "9f714ab21eb24c831fb6c81a1e03bafa26c920c082d3a4008a03402ede218abc",
  "FUSELAGE_FROZEN_REGRESSION_PASS": true,
  "TAIL_PRIMARY_GEOMETRY_REGRESSION_CAUSE": "REFIT_TOO_GLOBAL",
  "TAIL_ACCEPTED_MASTER_BOUNDARY_CONTAINS_ENDPOINT_FLIP": true,
  "MASTER_BOUNDARY_REPAIR_CAUSAL": false,
  "TAIL_LOCAL_BOUNDARY_REFIT_USED": true,
  "GLOBAL_TAIL_REFIT_USED": false,
  "BOUNDARY_STRIP_ROWS": 3,
  "TOTAL_CONTROL_POINT_COUNT": 368,
  "MOVED_CONTROL_POINT_COUNT": 16,
  "MOVED_CONTROL_POINT_RATIO": 0.043478260869565216,
  "BOUNDARY_STRIP_MOVEMENT_RATE": 1.0,
  "V7D_MAX_CONTROL_POINT_DISPLACEMENT": 0.9415865962457598,
  "V7D3_MAX_CONTROL_POINT_DISPLACEMENT": 0.5621781037522369,
  "V7D3_INTERIOR_RMS_DEVIATION_FROM_V7B": 0.0,
  "V7D3_INTERIOR_P95_DEVIATION_FROM_V7B": 0.0,
  "ROW_0_MAX_DISPLACEMENT": 0.5621781037522369,
  "ROW_1_MAX_DISPLACEMENT": 0.14054452593805924,
  "ROW_2_MAX_DISPLACEMENT": 0.0,
  "INTERIOR_MAX_DISPLACEMENT": 0.0,
  "VERTICAL_TAIL_CHAMFER_V7B": 0.010298782545970303,
  "VERTICAL_TAIL_CHAMFER_V7D": 0.023507918076213743,
  "VERTICAL_TAIL_CHAMFER_V7D3": 0.010384239294602613,
  "VERTICAL_TAIL_HAUSDORFF_V7B": 0.25303765500752023,
  "VERTICAL_TAIL_HAUSDORFF_V7D": 0.47054985066586297,
  "VERTICAL_TAIL_HAUSDORFF_V7D3": 0.2533517329526479,
  "VERTICAL_TAIL_SIDE_HAUSDORFF_V7D": 0.47054985066586297,
  "VERTICAL_TAIL_SIDE_HAUSDORFF_V7D3": 0.2533517329526479,
  "VERTICAL_TAIL_TIP_HAUSDORFF_V7D3": 0.0352177397697871,
  "VERTICAL_TAIL_ROOT_HAUSDORFF_V7D3": 0.015522706741697537,
  "VERTICAL_TAIL_WORST_REGION_V7D3": "SIDE",
  "VERTICAL_TAIL_A_B_BOUNDARY_P95": 0.0,
  "VERTICAL_TAIL_MASTER_BOUNDARY_COUNT": 1,
  "VERTICAL_TAIL_SHARED_OCC_EDGE_COUNT": 1,
  "VERTICAL_TAIL_PCURVE_COUNT": 2,
  "VERTICAL_TAIL_TRIMMED_FACE_COUNT": 2,
  "SHARED_EDGE_IDENTITY_PRESERVED": true,
  "PCURVE_REVALIDATED": true,
  "PCURVE_3D_P95_ERROR": 1.11929294177293e-16,
  "LOCAL_REFIT_LOCALITY_VALID": true,
  "LOCAL_REFIT_OUTPERFORMS_GLOBAL": true,
  "INTERIOR_ANCHOR_DEPENDENCY_PASS": true,
  "BOUNDARY_STRIP_WIDTH_DEPENDENCY_PASS": true,
  "LOCAL_BOUNDARY_INFLUENCE_TEST_PASS": true,
  "VERTICAL_TAIL_GEOMETRY_REGRESSION": false,
  "MASTER_BOUNDARY_GEOMETRY_INCOMPATIBLE": false,
  "PROFILE_SAMPLE_DERIVED_EDGE_COUNT": 0,
  "FORCED_SEWING_COUNT": 0,
  "LARGE_TOLERANCE_SEWING_REQUIRED": false,
  "MAIN_WING_REGRESSION_PASS": true,
  "V7B_REGRESSION_PASS": true,
  "V7_CONTRACT_REGRESSION_PASS": true,
  "RUNTIME_PROFILE_REMEASUREMENT": false,
  "RUNTIME_BOUNDARY_REDETECTION_FROM_MESH": false,
  "RUNTIME_MASTER_BOUNDARY_RECOMPUTED": false,
  "MASTER_BOUNDARY_IDENTITY_REPAIR_ONLY": true,
  "FINAL_STEP": "/data/home/cuiyuehan/project/mesh2cad/ours3/v7d3_vertical_tail_geometry_preserving_refit/06_candidates/CADPART_005/v7d3_vertical_tail_local_refit.step",
  "FINAL_STEP_SHA256": "ae11f2595c5df3cccf29393a705f8280e114ddb0a5d30ce70f8354476ea44277",
  "FORMAL_TOPOLOGY_STEP": "/data/home/cuiyuehan/project/mesh2cad/ours3/v7d3_vertical_tail_geometry_preserving_refit/07_topology/CADPART_005/v7d3_shared_topology_faces.step",
  "REPORT": "/data/home/cuiyuehan/project/mesh2cad/ours3/v7d3_vertical_tail_geometry_preserving_refit/artifacts/v7d3_final_report.md",
  "COMPARISON_CSV": "/data/home/cuiyuehan/project/mesh2cad/ours3/v7d3_vertical_tail_geometry_preserving_refit/artifacts/v7b_v7d_v7d3_tail_comparison.csv",
  "DEBUG_CONTACT_SHEET": "/data/home/cuiyuehan/project/mesh2cad/ours3/v7d3_vertical_tail_geometry_preserving_refit/artifacts/v7d3_tail_contact_sheet.png",
  "TESTS_PASSED": 0,
  "TESTS_FAILED": 0,
  "BLOCKERS": []
}
```

## Tests

- Passed: 20
- Failed: 0
- JUnit: `/data/home/cuiyuehan/project/mesh2cad/ours3/v7d3_vertical_tail_geometry_preserving_refit/artifacts/pytest.xml`

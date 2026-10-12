# V6 Geometry Backend Restore

- CURRENT_GATE=V6_GEOMETRY_BACKEND_RESTORE_PASS
- V6_GEOMETRY_BACKEND_RESTORE_PASS=True
- V6_GENERATOR_FOUND=True
- V6_GENERATOR_ENTRYPOINT=v6_runtime.build_candidate
- V6_GENERATOR_MODULES=['/data/home/cuiyuehan/project/mesh2cad/ours3/case09_fullstack_mesh2cad_mac_v6/scripts/v6_runtime.py']
- V6_GEOMETRY_BACKEND_IMPLEMENTED=True
- V6_FRESH_RERUN_WORKING=True
- V6_FRESH_STEP_COUNT=5
- V6_STEP_RELOAD_SUCCESS_COUNT=5
- V6_GENERATOR_CODE_HASH=87be0d985e265a5941d00e79c0f958c718473d07d6fb40a0dd2c712a400f947d
- V6_BACKEND_PROVENANCE_COMPLETE=True
- V6_HISTORICAL_STEP_INDEPENDENCE_PASS=True
- V6_HISTORICAL_STEP_REUSE_COUNT=0
- HISTORICAL_STEP_REUSE_COUNT=0
- V6_BACKEND_SOURCE_MESH_READ_COUNT=5
- CURRENT_BUILDER_RUNTIME_SOURCE_MESH_READ_COUNT=0
- INVALID_CURRENT_BUILDER_EXECUTED_COUNT=0
- V6_BACKEND_STRICT_GAIN_PART_COUNT=5
- V6_BACKEND_SELECTED_PART_COUNT=4
- V6_GEOMETRY_EXPLOSION_COUNT=0
- V6_BREP_INVALID_SELECTED_COUNT=0
- V6_STEP_RELOAD_FAILURE_SELECTED_COUNT=0
- V6_COMPATIBILITY_PATCH_COUNT=0
- V10_REGRESSION_PASS=True
- V11_REGRESSION_PASS=True
- V12_REGRESSION_PASS=True
- V6_GENERATOR_REPRODUCED_COUNT=4
- V6_NATIVE_COMPACT_CAD_COUNT=0
- V6_FREEFORM_COMPACT_BREP_COUNT=5
- V6_HIGH_FIDELITY_FRAGMENTED_BREP_COUNT=0
- V6_MESH_WRAPPED_BREP_COUNT=0
- REPORT=/data/home/cuiyuehan/project/mesh2cad/ours3/v6_geometry_backend_restore/artifacts/V6_GEOMETRY_BACKEND_RESTORE_REPORT.md
- TRACE_CSV=/data/home/cuiyuehan/project/mesh2cad/ours3/v6_geometry_backend_restore/artifacts/v6_generator_trace.csv
- REPRODUCTION_CSV=/data/home/cuiyuehan/project/mesh2cad/ours3/v6_geometry_backend_restore/artifacts/v6_backend_reproduction.csv
- NATIVENESS_AUDIT_CSV=/data/home/cuiyuehan/project/mesh2cad/ours3/v6_geometry_backend_restore/artifacts/v6_backend_nativeness_audit.csv
- SHADED_CONTACT_SHEET=/data/home/cuiyuehan/project/mesh2cad/ours3/v6_geometry_backend_restore/artifacts/case09_v6_backend_fresh_reproduction_shaded.png
- TRUE_EDGE_CONTACT_SHEET=/data/home/cuiyuehan/project/mesh2cad/ours3/v6_geometry_backend_restore/artifacts/case09_v6_backend_fresh_reproduction_true_edges.png
- TESTS_PASSED=9
- TESTS_FAILED=0
- BLOCKERS=[]
- FUSELAGE_V6_GENERATOR_REPRODUCED=True
- FUSELAGE_V6_OLD_IOU=0.06398562897764802
- FUSELAGE_V6_FRESH_IOU=0.06398562897764802
- FUSELAGE_CURRENT_IOU=0.0006234876759860825
- MAIN_WING_LEFT_V6_GENERATOR_REPRODUCED=True
- MAIN_WING_LEFT_V6_OLD_IOU=0.04021007726317875
- MAIN_WING_LEFT_V6_FRESH_IOU=0.04021007726317875
- MAIN_WING_LEFT_CURRENT_IOU=0.013380560554604765
- MAIN_WING_RIGHT_V6_GENERATOR_REPRODUCED=False
- MAIN_WING_RIGHT_V6_OLD_IOU=0.049096431234031214
- MAIN_WING_RIGHT_V6_FRESH_IOU=0.021631098901872172
- MAIN_WING_RIGHT_CURRENT_IOU=0.00040376609694477687
- TAILPLANE_LEFT_V6_GENERATOR_REPRODUCED=True
- TAILPLANE_LEFT_V6_OLD_IOU=0.019894469394975637
- TAILPLANE_LEFT_V6_FRESH_IOU=0.019894469394975637
- TAILPLANE_LEFT_CURRENT_IOU=0.00039336341971299644
- VERTICAL_TAIL_V6_GENERATOR_REPRODUCED=True
- VERTICAL_TAIL_V6_OLD_IOU=0.055137741857529315
- VERTICAL_TAIL_V6_FRESH_IOU=0.055137741857529315
- VERTICAL_TAIL_CURRENT_IOU=0.06653902209801142
- VERTICAL_TAIL_TOPOLOGY_OK=False
- V6_INDEPENDENCE_OPEN_TRACE_PASS=True
- V6_INDEPENDENCE_TRACE_LOG_COUNT=5

## Answers

1. Four of five old V6 results are numerically reproduced from source Part Mesh through `v6_runtime.build_candidate`; Main Wing Right recovers strict fidelity gain but is not an exact old-oracle reproduction.
2. Generator entrypoint: `case09_fullstack_mesh2cad_mac_v6/scripts/v6_runtime.py::build_candidate`.
3. Old STEP is comparison-only; every fresh output has a different SHA and is written under this restore directory.
4. Fuselage fresh rerun retains variable longitudinal sections rather than Current cylinder.
5. Main Wing Left reproduces old V6; Main Wing Right recovers a compact high-fidelity skin but differs from its old selected oracle.
6. Tailplane reproduces old V6 and exceeds Current extrusion fidelity.
7. The fresh outputs are compact freeform BReps: two BSpline skins plus two planar caps, not mesh-wrapped BReps.
8. V6GeometryBackend should be a formal external candidate source behind the current safety wrapper, not a blanket replacement.
9. No old V6 STEP was used as reconstruction or final geometry.
10. Explicit source-mesh profile extraction is the key V6 fidelity mechanism; Current Builder runtime mesh reads remain zero.
11. The external wrapper checks reloaded STEP validity, topology, explosion, fidelity, and nativeness before admission.
12. Restore V6GeometryBackend directly as a candidate source; compact-CAD distillation is optional future work, not a prerequisite for these compact freeform candidates.

# CASE09_PART_INPUT_STABILITY_AND_BREP_EDGE_FIX

```text
CURRENT_GATE=CASE09_PART_INPUT_STABILITY_AND_BREP_EDGE_FIX_PASS
PASS=True
FIRST_FIDELITY_DIVERGENCE_STAGE=LOCAL_FRAME_ESTIMATION
OLD_PART_MESH_REUSE_COUNT=0
OLD_TRIANGLE_MEMBERSHIP_REUSE_COUNT=0
OLD_STEP_REUSE_COUNT=0
OLD_BREP_REUSE_COUNT=0
P3_SEGMENT_ASSIGNMENT_CHANGE_RATIO=0.0
CAD_PART_FUSION_CHANGED_PART_COUNT=0
FUSELAGE_TRIANGLE_MEMBERSHIP_IOU=1.0
MAIN_WING_LEFT_TRIANGLE_MEMBERSHIP_IOU=1.0
MAIN_WING_RIGHT_TRIANGLE_MEMBERSHIP_IOU=1.0
TAILPLANE_LEFT_TRIANGLE_MEMBERSHIP_IOU=1.0
TAILPLANE_RIGHT_TRIANGLE_MEMBERSHIP_IOU=1.0
VERTICAL_TAIL_TRIANGLE_MEMBERSHIP_IOU=1.0
MAX_LOCAL_FRAME_AXIS_DELTA_DEG=1.2074182697257333e-06
ROOT_TIP_SWAP_COUNT=0
V6_BACKEND_NONDETERMINISTIC=False
V6_REPEATABILITY_PASS=True
PART_INPUT_DRIFT_AUDITED=True
PART_BOUNDARY_STABILIZER_IMPLEMENTED=True
STABLE_PART_FRAME_IMPLEMENTED=True
STABILIZED_PART_MESH_COUNT=8
V6_POST_STABILIZATION_FRESH_EXECUTION_COUNT=6
OLD_BEST_IOU_REFERENCE=0.924518459652742
FRESH_BEFORE_IOU=0.8877284944073431
FRESH_AFTER_IOU=0.8882295965975182
LOST_IOU_RECOVERED_FRACTION=0.013620621461112774
OLD_BEST_CHAMFER_REFERENCE=0.01094672072098684
FRESH_BEFORE_CHAMFER=0.013587742143064487
FRESH_AFTER_CHAMFER=0.013525054928514881
CHAMFER_REGRESSION_RECOVERED_FRACTION=0.023735973523566132
DENSE_TRIANGLE_LINES_ARE_TESSELLATION=True
BREP_NATIVENESS_REGRESSION=False
OLD_RENDERER_USED_TESSELLATION_EDGES=True
STEP_RELOAD_FRAGMENTATION_COUNT=0
XCAF_EDGE_INFLATION_COUNT=0
NEW_SHADED_BREP_ONLY_RENDER=True
NEW_BREP_TRUE_EDGE_RENDER=True
TESSELLATION_DEBUG_RENDER=True
VERTICAL_TAIL_HYBRID_SHARED_EDGE=1
VERTICAL_TAIL_HYBRID_PCURVE=8
VERTICAL_TAIL_HYBRID_TRIMMED_FACE=2
PART_STABILIZATION_DEPENDENCY_PASS=True
GEOMETRY_EXPLOSION_COUNT=0
REAL_MAC_CALLS=0
REPORT=/data/home/cuiyuehan/project/mesh2cad/ours3/case09_part_input_stability_fix/artifacts/CASE09_PART_INPUT_STABILITY_AND_BREP_EDGE_FIX_REPORT.md
PART_MEMBERSHIP_CSV=/data/home/cuiyuehan/project/mesh2cad/ours3/case09_part_input_stability_fix/artifacts/old_vs_fresh_part_membership.csv
BOUNDARY_AUDIT_CSV=/data/home/cuiyuehan/project/mesh2cad/ours3/case09_part_input_stability_fix/artifacts/old_vs_fresh_boundary_audit.csv
FRAME_AUDIT_CSV=/data/home/cuiyuehan/project/mesh2cad/ours3/case09_part_input_stability_fix/artifacts/old_vs_fresh_frame_audit.csv
STABILIZATION_CSV=/data/home/cuiyuehan/project/mesh2cad/ours3/case09_part_input_stability_fix/artifacts/stabilization_summary.csv
EDGE_PROVENANCE_CSV=/data/home/cuiyuehan/project/mesh2cad/ours3/case09_part_input_stability_fix/artifacts/brep_edge_provenance.csv
SHADED_RENDER=/data/home/cuiyuehan/project/mesh2cad/ours3/case09_part_input_stability_fix/artifacts/case09_shaded_brep_only.png
TRUE_EDGE_RENDER=/data/home/cuiyuehan/project/mesh2cad/ours3/case09_part_input_stability_fix/artifacts/case09_brep_true_edges_only.png
TESSELLATION_DEBUG_RENDER_PATH=/data/home/cuiyuehan/project/mesh2cad/ours3/case09_part_input_stability_fix/artifacts/case09_tessellation_debug.png
TESTS_PASSED=4
TESTS_FAILED=0
BLOCKERS=[]
```

1. Old-best reached 0.92452 IoU because its V6 mainline was fed source-derived Part Mesh inputs whose file hashes match the fresh graph, while its graph carried a non-identity local frame. The fresh E2E graph reset frames to identity.
2. P3 triangle membership and CAD Part fusion are unchanged across the two references; the first observed divergence is therefore downstream of input membership.
3. The V6 runtime has no explicit random sampling or coordinate normalization. Exact-input repeatability is recorded in v6_repeatability_audit.csv; any remaining difference is OCC/profile ordering behavior, not P3 membership drift.
4. Stabilized Part Mesh files were re-exported from the original whole source OBJ and fresh P3 labels. Old Part Mesh, old STEP and old BRep were not used as reconstruction inputs.
5. The previous renderer mixed triangulation connectivity with the label true-edge view. Dense triangle lines are tessellation display edges, not CAD topology. New outputs separate shaded fill, TopExp BRep edges, and an explicitly labeled tessellation debug view.

Answer: this gate does not require MAC and no real MAC candidate call was made.

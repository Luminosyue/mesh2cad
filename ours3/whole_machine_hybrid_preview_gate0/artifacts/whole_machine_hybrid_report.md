# Whole Machine Hybrid Preview Gate 0

Status: **WHOLE_MACHINE_HYBRID_PREVIEW_GATE_0_PASS**

Scientific semantics: **HYBRID_MESH_CAD_PREVIEW**.
WHOLE_MACHINE_VISUAL_COMPLETE=true
FULL_CAD_RECOVERY_COMPLETE=false
FULL_CAD_ASSEMBLY_COMPLETE=false
HYBRID_CAD_AREA_COVERAGE=0.084665608
HYBRID_MESH_AREA_COVERAGE=0.915334392

The full visual object contains the residual original High-Mesh plus fresh tessellations of the two frozen accepted CAD BReps in their previously verified global placements.
Source triangles were removed only by frozen source triangle IDs. No P3, PhysX, MAC, LLM, geometry fitting, analyzer, ICP, bbox crop, Boolean union, fake CAD, or manual selection was used.

Triangle accounting: 355020 residual + 30808 recovered provenance = 385828 original; pass=True.
Interactive GLB: `/data/home/cuiyuehan/project/mesh2cad/ours3/whole_machine_hybrid_preview_gate0/hybrid/REAL_03_hybrid_preview.glb` with independent nodes: CADPART_000_Q1, CADPART_004_Q2, Residual_HighMesh.
Remaining geometry type: MESH.

Tests: 44 passed, 0 failed

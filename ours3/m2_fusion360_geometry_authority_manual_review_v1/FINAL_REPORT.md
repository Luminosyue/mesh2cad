# M2 Fusion360 Geometry Authority Manual Review V1

CURRENT_GATE: M2_FUSION360_GEOMETRY_AUTHORITY_MANUAL_REVIEW_BLOCKED
GEOMETRY_AUTHORITY_RESOLVED: NO
COMMON_VALID_DENOMINATOR: 592
MANUAL_RECONSTRUCTION_CASES: 20

Determined lineage:
raw reconstruction JSON -> source.json -> program.dsl -> program_canonical.dsl
raw reconstruction OBJ -> model.obj -> trimesh/STL -> sampled xyz,normals,edge_score -> features.npy -> coordinate_transform.json
raw reconstruction STEP -> model.step -> OCC tessellation -> M2 surface tensor
raw reconstruction STEP -> model.step -> B-Rep edge extraction -> GT curve/C2 input

The historical canonical transform is computed from features.npy[:,0:3], not STEP and not normals or edge scores. The code therefore proves a split pipeline: OBJ-derived sampled XYZ controls the frozen transform, while Original M2 surface and curve branches consume the frozen STEP path. The reviewed code lacks the historical manifest/export record needed to prove one unified geometry authority or byte-level OBJ/STEP equivalence.

Dataset documentation declares cm units and describes OBJ as triangulated B-Rep. No explicit project unit conversion was found. Numeric bbox ratios were not used as unit evidence.

No Dora, training, decode, DSL, M2, C2, Sonata, or P1 changes were made.

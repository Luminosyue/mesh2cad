# Unified STEP Geometry Protocol V1

- **name**: UNIFIED_STEP_GEOMETRY_EVALUATOR_V1
- **loader**: cadquery.importers.importStep
- **cadquery_version**: 2.6.1
- **normalization**: NONE; absolute shared coordinate frame
- **surface_sample_n**: 10000
- **sampling_method**: area-weighted triangulated surface sampling
- **global_seed**: 20260915
- **case_seed**: SHA256(global_seed:case_id) first 8 bytes modulo 2^32
- **chamfer**: 0.5*(mean(P->G Euclidean NN)+mean(G->P Euclidean NN))
- **chamfer_squared**: False
- **chamfer_symmetric**: True
- **h95**: max(percentile95(P->G), percentile95(G->P))
- **h95_symmetric**: True
- **volume_error**: abs(Vpred-Vgt)/max(abs(Vgt),1e-12)
- **multi_solid**: total absolute volume; all tessellated valid faces
- **invalid_policy**: GEOMETRY_VALID=NO; no synthetic metric
- **method_specific_branch**: False

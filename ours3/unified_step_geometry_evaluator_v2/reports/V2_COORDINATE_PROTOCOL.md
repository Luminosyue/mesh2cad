# Unified STEP Geometry Protocol V2

- **name**: UNIFIED_STEP_GEOMETRY_EVALUATOR_V2
- **inherits_v1_metric_definitions**: True
- **loader**: cadquery.importers.importStep
- **cadquery_version**: 2.6.1
- **surface_sample_n**: 10000
- **sampling_method**: area-weighted triangulated surface sampling
- **global_seed**: 20260915
- **case_seed**: SHA256(global_seed:case_id) first 8 bytes modulo 2^32
- **chamfer**: symmetric non-squared Euclidean NN mean
- **h95**: max directional P95
- **volume_error**: abs(Vpred-Vgt)/max(abs(Vgt),1e-12)
- **multi_solid**: sum absolute solid volumes
- **source_frames**: {'GT': 'DATASET_CANONICAL', 'P1': 'DATASET_CANONICAL', 'CAD_RECODE': 'OFFICIAL_CENTERED_CUBE2'}
- **adapters**: {'GT': 'identity', 'P1': 'identity', 'CAD_RECODE': 'x/200 + [0.5,0.5,0.5]'}
- **adapter_policy**: load STEP then adapt in memory before tessellation/sampling; no source mutation
- **forbidden**: prediction-derived fitting, ICP, Procrustes, empirical scale, TEST1000, holdout958, inference, training, re-decoding

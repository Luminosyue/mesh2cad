{
  "case_id": "airplane",
  "part_id": "p3_parts__part_004",
  "source_path": "airplane/p3_parts/part_004.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x20 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 32892,
  "cad_brep_face_count": 458,
  "quality_level": "B_USABLE",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.9110512129380054,
  "iou128": 0.9087658675881266,
  "iou256": 0.9079608783465429,
  "cd": 0.00358591103584796,
  "ncd": 0.0031752231328023516,
  "hausdorff": 0.06577974496016666,
  "nhd": 0.05824610978335933,
  "normal_consistency": 0.942769926067467,
  "bbox_error": 0.04902889121734381,
  "centroid_error": 0.0038593851078160004,
  "surface_area_error": 0.04287490202387613,
  "volume_error": 0.2276924800432761,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      0.052043620625,
      -0.615235139375,
      -0.020986849374999998
    ],
    "pitch": 0.014719501250000001,
    "dimensions": [
      64,
      41,
      14
    ],
    "intersection": 4732,
    "union": 5194,
    "source_occupied": 5175,
    "cad_occupied": 4751
  },
  "grid128": {
    "origin": [
      0.0483637453125,
      -0.6189150146875,
      -0.0246667246875
    ],
    "pitch": 0.0073597506250000005,
    "dimensions": [
      128,
      81,
      27
    ],
    "intersection": 37871,
    "union": 41673,
    "source_occupied": 41534,
    "cad_occupied": 38010
  },
  "grid256": {
    "origin": [
      0.04652380765625,
      -0.62075495234375,
      -0.02650666234375
    ],
    "pitch": 0.0036798753125000003,
    "dimensions": [
      256,
      161,
      53
    ],
    "intersection": 302548,
    "union": 333217,
    "source_occupied": 332035,
    "cad_occupied": 303730
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
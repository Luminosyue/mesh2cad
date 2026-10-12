{
  "case_id": "airplane",
  "part_id": "p3_parts__part_005",
  "source_path": "airplane/p3_parts/part_005.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x4 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 36660,
  "cad_brep_face_count": 74,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.4069664902998236,
  "iou128": 0.4772765386550394,
  "iou256": 0.47025932376765917,
  "cd": 0.043635676452975274,
  "ncd": 0.02390739361269489,
  "hausdorff": 0.630749308132033,
  "nhd": 0.3455789667131262,
  "normal_consistency": 0.7732197767581819,
  "bbox_error": 0.3388668354374762,
  "centroid_error": 0.08049444801080563,
  "surface_area_error": 0.27747456584230024,
  "volume_error": 0.3738784689397185,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.115292607734375,
      -0.986191177734375,
      -0.177446057734375
    ],
    "pitch": 0.02761764453125,
    "dimensions": [
      10,
      64,
      14
    ],
    "intersection": 923,
    "union": 2268,
    "source_occupied": 2021,
    "cad_occupied": 1170
  },
  "grid128": {
    "origin": [
      -0.12219701886718749,
      -0.9930955888671875,
      -0.18435046886718748
    ],
    "pitch": 0.013808822265625,
    "dimensions": [
      20,
      128,
      27
    ],
    "intersection": 8538,
    "union": 17889,
    "source_occupied": 17026,
    "cad_occupied": 9401
  },
  "grid256": {
    "origin": [
      -0.12564922443359375,
      -0.9965477944335938,
      -0.18780267443359375
    ],
    "pitch": 0.0069044111328125,
    "dimensions": [
      40,
      256,
      53
    ],
    "intersection": 68039,
    "union": 144684,
    "source_occupied": 137468,
    "cad_occupied": 75255
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
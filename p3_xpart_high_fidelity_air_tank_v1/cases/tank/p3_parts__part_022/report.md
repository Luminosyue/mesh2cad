{
  "case_id": "tank",
  "part_id": "p3_parts__part_022",
  "source_path": "tank/p3_parts/part_022.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x4 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 2371,
  "cad_brep_face_count": 74,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.1629555477395092,
  "iou128": 0.17684364721626125,
  "iou256": 0.17675400061777355,
  "cd": 0.015705468881468728,
  "ncd": 0.053175428309578665,
  "hausdorff": 0.09680041097719211,
  "nhd": 0.3277459178776241,
  "normal_consistency": 0.7085147218229368,
  "bbox_error": 0.14554881460437455,
  "centroid_error": 0.07037523472119529,
  "surface_area_error": 0.4562544362250333,
  "volume_error": 0.6894677456694127,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.717681419140625,
      -0.661696929140625,
      -0.32790968914062496
    ],
    "pitch": 0.0031790417187499993,
    "dimensions": [
      62,
      64,
      29
    ],
    "intersection": 6023,
    "union": 36961,
    "source_occupied": 33942,
    "cad_occupied": 9042
  },
  "grid128": {
    "origin": [
      -0.7184761795703125,
      -0.6624916895703125,
      -0.3287044495703125
    ],
    "pitch": 0.0015895208593749996,
    "dimensions": [
      123,
      128,
      57
    ],
    "intersection": 51670,
    "union": 292179,
    "source_occupied": 271881,
    "cad_occupied": 71968
  },
  "grid256": {
    "origin": [
      -0.7188735597851563,
      -0.6628890697851563,
      -0.32910182978515623
    ],
    "pitch": 0.0007947604296874998,
    "dimensions": [
      245,
      256,
      113
    ],
    "intersection": 397127,
    "union": 2246778,
    "source_occupied": 2067700,
    "cad_occupied": 576205
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
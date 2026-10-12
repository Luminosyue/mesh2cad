{
  "case_id": "tank",
  "part_id": "p3_parts__part_016",
  "source_path": "tank/p3_parts/part_016.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x3 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 2537,
  "cad_brep_face_count": 50,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.3703027820192916,
  "iou128": 0.33993385620190486,
  "iou256": 0.339835872601802,
  "cd": 0.015061864154224119,
  "ncd": 0.04800759286899397,
  "hausdorff": 0.08039913801906476,
  "nhd": 0.2562610474716596,
  "normal_consistency": 0.7414762889294287,
  "bbox_error": 0.17594436717292972,
  "centroid_error": 0.0579759981778043,
  "surface_area_error": 0.25703766582734133,
  "volume_error": 0.3583948931962706,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.531173549140625,
      -0.689862989140625,
      -0.31954958914062503
    ],
    "pitch": 0.00362260171875,
    "dimensions": [
      54,
      64,
      23
    ],
    "intersection": 9943,
    "union": 26851,
    "source_occupied": 20825,
    "cad_occupied": 15969
  },
  "grid128": {
    "origin": [
      -0.5320791995703125,
      -0.6907686395703125,
      -0.3204552395703125
    ],
    "pitch": 0.001811300859375,
    "dimensions": [
      108,
      128,
      46
    ],
    "intersection": 73595,
    "union": 216498,
    "source_occupied": 162242,
    "cad_occupied": 127851
  },
  "grid256": {
    "origin": [
      -0.5325320247851562,
      -0.6912214647851562,
      -0.32090806478515627
    ],
    "pitch": 0.0009056504296875,
    "dimensions": [
      215,
      256,
      92
    ],
    "intersection": 587791,
    "union": 1729632,
    "source_occupied": 1289869,
    "cad_occupied": 1027554
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
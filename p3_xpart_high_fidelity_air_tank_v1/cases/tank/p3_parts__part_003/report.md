{
  "case_id": "tank",
  "part_id": "p3_parts__part_003",
  "source_path": "tank/p3_parts/part_003.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x20 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 2018,
  "cad_brep_face_count": 458,
  "quality_level": "C_NEAR_MISS",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.8482142857142857,
  "iou128": 0.8447136563876652,
  "iou256": 0.8443064182194617,
  "cd": 0.0016871496373975137,
  "ncd": 0.0020002437147115027,
  "hausdorff": 0.05324789555314697,
  "nhd": 0.06312941427417798,
  "normal_consistency": 0.9347195647560829,
  "bbox_error": 0.062367929903506314,
  "centroid_error": 0.02913238378805703,
  "surface_area_error": 0.09504372473730184,
  "volume_error": 0.37493299014899584,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.92094097890625,
      -0.13587892890624997,
      -0.25218606890625
    ],
    "pitch": 0.0131066221875,
    "dimensions": [
      6,
      64,
      4
    ],
    "intersection": 95,
    "union": 112,
    "source_occupied": 111,
    "cad_occupied": 96
  },
  "grid128": {
    "origin": [
      -0.9242176344531251,
      -0.13915558445312498,
      -0.255462724453125
    ],
    "pitch": 0.00655331109375,
    "dimensions": [
      12,
      128,
      7
    ],
    "intersection": 767,
    "union": 908,
    "source_occupied": 898,
    "cad_occupied": 777
  },
  "grid256": {
    "origin": [
      -0.9258559622265625,
      -0.14079391222656248,
      -0.25710105222656254
    ],
    "pitch": 0.003276655546875,
    "dimensions": [
      24,
      256,
      14
    ],
    "intersection": 6117,
    "union": 7245,
    "source_occupied": 7162,
    "cad_occupied": 6200
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
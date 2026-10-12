{
  "case_id": "airplane",
  "part_id": "p3_parts__part_002",
  "source_path": "airplane/p3_parts/part_002.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x17 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 2250,
  "cad_brep_face_count": 386,
  "quality_level": "C_NEAR_MISS",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.8161081953976584,
  "iou128": 0.8140140595761898,
  "iou256": 0.8156982322152879,
  "cd": 0.002504162984963742,
  "ncd": 0.007544791310185205,
  "hausdorff": 0.06221842667223912,
  "nhd": 0.18745786424796226,
  "normal_consistency": 0.9064702444307949,
  "bbox_error": 0.176159318467011,
  "centroid_error": 0.04225855664489761,
  "surface_area_error": 0.12884550378095802,
  "volume_error": 0.46678451039897767,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.34861107296875,
      -0.9458587629687499,
      -0.006190062968749999
    ],
    "pitch": 0.0046553940625,
    "dimensions": [
      64,
      20,
      25
    ],
    "intersection": 4043,
    "union": 4954,
    "source_occupied": 4942,
    "cad_occupied": 4055
  },
  "grid128": {
    "origin": [
      -0.349774921484375,
      -0.9470226114843749,
      -0.007353911484375
    ],
    "pitch": 0.00232769703125,
    "dimensions": [
      128,
      39,
      50
    ],
    "intersection": 32191,
    "union": 39546,
    "source_occupied": 39468,
    "cad_occupied": 32269
  },
  "grid256": {
    "origin": [
      -0.3503568457421875,
      -0.9476045357421875,
      -0.0079358357421875
    ],
    "pitch": 0.001163848515625,
    "dimensions": [
      256,
      77,
      100
    ],
    "intersection": 257613,
    "union": 315819,
    "source_occupied": 315113,
    "cad_occupied": 258319
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
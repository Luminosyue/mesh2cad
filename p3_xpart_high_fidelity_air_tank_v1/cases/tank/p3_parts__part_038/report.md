{
  "case_id": "tank",
  "part_id": "p3_parts__part_038",
  "source_path": "tank/p3_parts/part_038.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x6 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 12978,
  "cad_brep_face_count": 122,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.2782093969663337,
  "iou128": 0.3040029036606865,
  "iou256": 0.2937507384812472,
  "cd": 0.019375673322775233,
  "ncd": 0.018614896869355056,
  "hausdorff": 0.21112118862104923,
  "nhd": 0.2028316171338908,
  "normal_consistency": 0.7514569900146757,
  "bbox_error": 0.20304487708853194,
  "centroid_error": 0.01886204962357538,
  "surface_area_error": 0.26561170447879057,
  "volume_error": 0.634379731644853,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.36240359718750004,
      -0.6886345971875,
      -0.37461697718750003
    ],
    "pitch": 0.015513725625,
    "dimensions": [
      64,
      18,
      11
    ],
    "intersection": 752,
    "union": 2703,
    "source_occupied": 2462,
    "cad_occupied": 993
  },
  "grid128": {
    "origin": [
      -0.36628202859375003,
      -0.69251302859375,
      -0.37849540859375
    ],
    "pitch": 0.0077568628125,
    "dimensions": [
      128,
      35,
      21
    ],
    "intersection": 5863,
    "union": 19286,
    "source_occupied": 17950,
    "cad_occupied": 7199
  },
  "grid256": {
    "origin": [
      -0.368221244296875,
      -0.6944522442968749,
      -0.380434624296875
    ],
    "pitch": 0.00387843140625,
    "dimensions": [
      256,
      70,
      41
    ],
    "intersection": 47236,
    "union": 160803,
    "source_occupied": 150397,
    "cad_occupied": 57642
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
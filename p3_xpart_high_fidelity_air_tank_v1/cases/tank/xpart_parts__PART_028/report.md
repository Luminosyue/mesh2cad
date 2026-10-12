{
  "case_id": "tank",
  "part_id": "xpart_parts__PART_028",
  "source_path": "tank/xpart_parts/PART_028.stl",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x21 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 11324,
  "cad_brep_face_count": 482,
  "quality_level": "C_NEAR_MISS",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.8450501783835117,
  "iou128": 0.844065410093123,
  "iou256": 0.8446781269273702,
  "cd": 0.0020056344119540326,
  "ncd": 0.007089673024219996,
  "hausdorff": 0.017336609105640863,
  "nhd": 0.061282798687104796,
  "normal_consistency": 0.8726725253712548,
  "bbox_error": 0.01432447389932333,
  "centroid_error": 0.0031817124301132494,
  "surface_area_error": 0.05770528935338347,
  "volume_error": 0.06400443122751971,
  "IOU_VALID": true,
  "grid64": {
    "origin": [
      0.43745350115932524,
      -0.6088732553180307,
      -0.38352487212978303
    ],
    "pitch": 0.0029291962273418903,
    "dimensions": [
      64,
      64,
      36
    ],
    "intersection": 32924,
    "union": 38961,
    "source_occupied": 37124,
    "cad_occupied": 34761
  },
  "grid128": {
    "origin": [
      0.43672120210248977,
      -0.6096055543748662,
      -0.3842571711866185
    ],
    "pitch": 0.0014645981136709452,
    "dimensions": [
      127,
      128,
      71
    ],
    "intersection": 263762,
    "union": 312490,
    "source_occupied": 297734,
    "cad_occupied": 278518
  },
  "grid256": {
    "origin": [
      0.43635505257407203,
      -0.6099717039032839,
      -0.38462332071503624
    ],
    "pitch": 0.0007322990568354726,
    "dimensions": [
      254,
      256,
      141
    ],
    "intersection": 2110468,
    "union": 2498547,
    "source_occupied": 2380778,
    "cad_occupied": 2228237
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
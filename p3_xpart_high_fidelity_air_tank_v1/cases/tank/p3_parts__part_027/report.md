{
  "case_id": "tank",
  "part_id": "p3_parts__part_027",
  "source_path": "tank/p3_parts/part_027.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x5 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 2297,
  "cad_brep_face_count": 98,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.012616201859229747,
  "iou128": 0.010917386345119766,
  "iou256": 0.011545468741866639,
  "cd": 0.032644150728390685,
  "ncd": 0.05439134415327485,
  "hausdorff": 0.26168041309241574,
  "nhd": 0.436009180483967,
  "normal_consistency": 0.7329799249152198,
  "bbox_error": 0.3405138717404744,
  "centroid_error": 0.05918701246337664,
  "surface_area_error": 0.8056486999300236,
  "volume_error": 0.9970314661598005,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      0.41512642375,
      -0.27677859625,
      0.14653052375
    ],
    "pitch": 0.008011187500000001,
    "dimensions": [
      64,
      30,
      26
    ],
    "intersection": 19,
    "union": 1506,
    "source_occupied": 1500,
    "cad_occupied": 25
  },
  "grid128": {
    "origin": [
      0.413123626875,
      -0.278781393125,
      0.14452772687499998
    ],
    "pitch": 0.0040055937500000005,
    "dimensions": [
      128,
      59,
      52
    ],
    "intersection": 134,
    "union": 12274,
    "source_occupied": 12205,
    "cad_occupied": 203
  },
  "grid256": {
    "origin": [
      0.4121222284375,
      -0.27978279156249997,
      0.1435263284375
    ],
    "pitch": 0.0020027968750000002,
    "dimensions": [
      256,
      117,
      104
    ],
    "intersection": 1109,
    "union": 96055,
    "source_occupied": 95499,
    "cad_occupied": 1665
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
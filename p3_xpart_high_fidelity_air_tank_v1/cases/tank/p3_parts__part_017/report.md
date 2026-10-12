{
  "case_id": "tank",
  "part_id": "p3_parts__part_017",
  "source_path": "tank/p3_parts/part_017.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x16 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 4108,
  "cad_brep_face_count": 362,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.6536849889080601,
  "iou128": 0.6519782202958462,
  "iou256": 0.6508539206583935,
  "cd": 0.0073022551442533355,
  "ncd": 0.018676335474504053,
  "hausdorff": 0.07942273586938789,
  "nhd": 0.20313254331669703,
  "normal_consistency": 0.8411082120876872,
  "bbox_error": 0.10128059438137499,
  "centroid_error": 0.007036165632122724,
  "surface_area_error": 0.10010929949552486,
  "volume_error": 0.5780875769004344,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      0.43763404890624996,
      -0.07231463109375,
      -0.32740104109375
    ],
    "pitch": 0.004196337812500001,
    "dimensions": [
      64,
      28,
      63
    ],
    "intersection": 26520,
    "union": 40570,
    "source_occupied": 40435,
    "cad_occupied": 26655
  },
  "grid128": {
    "origin": [
      0.436584964453125,
      -0.073363715546875,
      -0.32845012554687497
    ],
    "pitch": 0.0020981689062500005,
    "dimensions": [
      128,
      55,
      125
    ],
    "intersection": 211342,
    "union": 324155,
    "source_occupied": 323024,
    "cad_occupied": 212473
  },
  "grid256": {
    "origin": [
      0.4360604222265625,
      -0.07388825777343751,
      -0.3289746677734375
    ],
    "pitch": 0.0010490844531250002,
    "dimensions": [
      256,
      109,
      249
    ],
    "intersection": 1688757,
    "union": 2594679,
    "source_occupied": 2585501,
    "cad_occupied": 1697935
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
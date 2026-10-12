{
  "case_id": "tank",
  "part_id": "p3_parts__part_036",
  "source_path": "tank/p3_parts/part_036.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x6 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 2887,
  "cad_brep_face_count": 122,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.08877928483353884,
  "iou128": 0.0918808278371617,
  "iou256": 0.08523995662830641,
  "cd": 0.01860871486428714,
  "ncd": 0.030097294619275683,
  "hausdorff": 0.09866503036254362,
  "nhd": 0.15957848293652238,
  "normal_consistency": 0.6760596342026861,
  "bbox_error": 0.1490932457681756,
  "centroid_error": 0.12842911438091067,
  "surface_area_error": 0.6567850943264233,
  "volume_error": 1.3709539139929652,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.73180829921875,
      -0.23551454921875,
      -0.39093165921875
    ],
    "pitch": 0.0091556415625,
    "dimensions": [
      64,
      15,
      16
    ],
    "intersection": 144,
    "union": 1622,
    "source_occupied": 1616,
    "cad_occupied": 150
  },
  "grid128": {
    "origin": [
      -0.7340972096093751,
      -0.237803459609375,
      -0.393220569609375
    ],
    "pitch": 0.00457782078125,
    "dimensions": [
      128,
      30,
      32
    ],
    "intersection": 1212,
    "union": 13191,
    "source_occupied": 13119,
    "cad_occupied": 1284
  },
  "grid256": {
    "origin": [
      -0.7352416648046876,
      -0.2389479148046875,
      -0.39436502480468755
    ],
    "pitch": 0.002288910390625,
    "dimensions": [
      256,
      60,
      63
    ],
    "intersection": 9355,
    "union": 109749,
    "source_occupied": 109109,
    "cad_occupied": 9995
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
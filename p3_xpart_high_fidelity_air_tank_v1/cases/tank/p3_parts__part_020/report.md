{
  "case_id": "tank",
  "part_id": "p3_parts__part_020",
  "source_path": "tank/p3_parts/part_020.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x9 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 2234,
  "cad_brep_face_count": 194,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.0991559733754203,
  "iou128": 0.1189090147198383,
  "iou256": 0.11207827361407241,
  "cd": 0.011999042666605602,
  "ncd": 0.03976967191617623,
  "hausdorff": 0.06005255278844044,
  "nhd": 0.19903840568647183,
  "normal_consistency": 0.7532112872625727,
  "bbox_error": 0.17780116171404778,
  "centroid_error": 0.030301858738116343,
  "surface_area_error": 0.15848901909048219,
  "volume_error": 0.7193195780179232,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.5383493084375001,
      -0.6779100084375,
      0.3069449615625
    ],
    "pitch": 0.0033062031250000005,
    "dimensions": [
      61,
      64,
      23
    ],
    "intersection": 2890,
    "union": 29146,
    "source_occupied": 26424,
    "cad_occupied": 5612
  },
  "grid128": {
    "origin": [
      -0.53917585921875,
      -0.67873655921875,
      0.30611841078125
    ],
    "pitch": 0.0016531015625000003,
    "dimensions": [
      122,
      128,
      46
    ],
    "intersection": 28944,
    "union": 243413,
    "source_occupied": 226292,
    "cad_occupied": 46065
  },
  "grid256": {
    "origin": [
      -0.5395891346093751,
      -0.6791498346093751,
      0.30570513539062505
    ],
    "pitch": 0.0008265507812500001,
    "dimensions": [
      244,
      256,
      92
    ],
    "intersection": 217256,
    "union": 1938431,
    "source_occupied": 1787255,
    "cad_occupied": 368432
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
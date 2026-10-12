{
  "case_id": "tank",
  "part_id": "p3_parts__part_005",
  "source_path": "tank/p3_parts/part_005.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x7 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 3946,
  "cad_brep_face_count": 146,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.1080320586793974,
  "iou128": 0.10172852058973056,
  "iou256": 0.10511467984110871,
  "cd": 0.01594889659316487,
  "ncd": 0.051568469753223545,
  "hausdorff": 0.082023313294737,
  "nhd": 0.26521061980623617,
  "normal_consistency": 0.6760033659795948,
  "bbox_error": 0.12143851961842285,
  "centroid_error": 0.029280283250055862,
  "surface_area_error": 0.4630424190893179,
  "volume_error": 0.888528899780676,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      0.042530773671875,
      -0.669868296328125,
      0.238905163671875
    ],
    "pitch": 0.00311314734375,
    "dimensions": [
      64,
      63,
      43
    ],
    "intersection": 6834,
    "union": 63259,
    "source_occupied": 60188,
    "cad_occupied": 9905
  },
  "grid128": {
    "origin": [
      0.041752486835937505,
      -0.6706465831640624,
      0.2381268768359375
    ],
    "pitch": 0.001556573671875,
    "dimensions": [
      128,
      126,
      86
    ],
    "intersection": 56028,
    "union": 550760,
    "source_occupied": 527920,
    "cad_occupied": 78868
  },
  "grid256": {
    "origin": [
      0.041363343417968754,
      -0.6710357265820313,
      0.23773773341796875
    ],
    "pitch": 0.0007782868359375,
    "dimensions": [
      256,
      251,
      172
    ],
    "intersection": 447870,
    "union": 4260775,
    "source_occupied": 4076725,
    "cad_occupied": 631920
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
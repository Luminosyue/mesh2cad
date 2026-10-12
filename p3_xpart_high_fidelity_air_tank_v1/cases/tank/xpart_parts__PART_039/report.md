{
  "case_id": "tank",
  "part_id": "xpart_parts__PART_039",
  "source_path": "tank/xpart_parts/PART_039.stl",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x21 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 49704,
  "cad_brep_face_count": 482,
  "quality_level": "C_NEAR_MISS",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.827033218785796,
  "iou128": 0.8121495327102803,
  "iou256": 0.8097690268837562,
  "cd": 0.004125187424720775,
  "ncd": 0.0031171608374222855,
  "hausdorff": 0.07342476416178265,
  "nhd": 0.05548276375771421,
  "normal_consistency": 0.8828520065157557,
  "bbox_error": 0.020109880870963617,
  "centroid_error": 0.015160573942678581,
  "surface_area_error": 0.10531665732934938,
  "volume_error": 0.06204711123458824,
  "IOU_VALID": true,
  "grid64": {
    "origin": [
      -0.6581525402143598,
      -0.6862510638311505,
      0.24571366142481565
    ],
    "pitch": 0.02011009119451046,
    "dimensions": [
      64,
      14,
      8
    ],
    "intersection": 722,
    "union": 873,
    "source_occupied": 820,
    "cad_occupied": 775
  },
  "grid128": {
    "origin": [
      -0.6631800630129874,
      -0.6912785866297781,
      0.24068613862618804
    ],
    "pitch": 0.01005504559725523,
    "dimensions": [
      128,
      27,
      15
    ],
    "intersection": 5214,
    "union": 6420,
    "source_occupied": 5994,
    "cad_occupied": 5640
  },
  "grid256": {
    "origin": [
      -0.6656938244123012,
      -0.693792348029092,
      0.23817237722687423
    ],
    "pitch": 0.005027522798627615,
    "dimensions": [
      256,
      54,
      30
    ],
    "intersection": 42772,
    "union": 52820,
    "source_occupied": 49466,
    "cad_occupied": 46126
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
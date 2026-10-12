{
  "case_id": "airplane",
  "part_id": "p3_parts__part_006",
  "source_path": "airplane/p3_parts/part_006.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x13 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 9874,
  "cad_brep_face_count": 290,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.6214829659318637,
  "iou128": 0.6225234095567255,
  "iou256": 0.6223578644013334,
  "cd": 0.01335074588805027,
  "ncd": 0.02202767742284578,
  "hausdorff": 0.21117339493813117,
  "nhd": 0.34841944135479996,
  "normal_consistency": 0.8025625758286101,
  "bbox_error": 0.16853955274010463,
  "centroid_error": 0.09518061836994547,
  "surface_area_error": 0.2855461813504812,
  "volume_error": 0.578022767707406,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      0.089009593046875,
      0.382225923046875,
      -0.145182606953125
    ],
    "pitch": 0.00725362609375,
    "dimensions": [
      64,
      52,
      15
    ],
    "intersection": 7753,
    "union": 12475,
    "source_occupied": 12469,
    "cad_occupied": 7759
  },
  "grid128": {
    "origin": [
      0.08719618652343751,
      0.3804125165234375,
      -0.1469960134765625
    ],
    "pitch": 0.003626813046875,
    "dimensions": [
      128,
      104,
      30
    ],
    "intersection": 61961,
    "union": 99532,
    "source_occupied": 99461,
    "cad_occupied": 62032
  },
  "grid256": {
    "origin": [
      0.08628948326171876,
      0.3795058132617188,
      -0.14790271673828126
    ],
    "pitch": 0.0018134065234375,
    "dimensions": [
      256,
      207,
      60
    ],
    "intersection": 495835,
    "union": 796704,
    "source_occupied": 796219,
    "cad_occupied": 496320
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
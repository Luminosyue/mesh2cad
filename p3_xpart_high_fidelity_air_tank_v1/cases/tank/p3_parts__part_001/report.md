{
  "case_id": "tank",
  "part_id": "p3_parts__part_001",
  "source_path": "tank/p3_parts/part_001.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x19 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 2751,
  "cad_brep_face_count": 434,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.4563758389261745,
  "iou128": 0.5568685376661743,
  "iou256": 0.526692770509025,
  "cd": 0.006559277297103213,
  "ncd": 0.007088503011377236,
  "hausdorff": 0.10246759722815096,
  "nhd": 0.11073504574065099,
  "normal_consistency": 0.8853299738287651,
  "bbox_error": 0.1285155031882062,
  "centroid_error": 0.0880904128322107,
  "surface_area_error": 0.22167356300960886,
  "volume_error": 0.5815285998649298,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.53391157953125,
      -0.21884667953125,
      0.29616925046875
    ],
    "pitch": 0.0143083409375,
    "dimensions": [
      6,
      64,
      8
    ],
    "intersection": 68,
    "union": 149,
    "source_occupied": 144,
    "cad_occupied": 73
  },
  "grid128": {
    "origin": [
      -0.537488664765625,
      -0.222423764765625,
      0.292592165234375
    ],
    "pitch": 0.00715417046875,
    "dimensions": [
      11,
      128,
      16
    ],
    "intersection": 754,
    "union": 1354,
    "source_occupied": 1319,
    "cad_occupied": 789
  },
  "grid256": {
    "origin": [
      -0.5392772073828125,
      -0.2242123073828125,
      0.2908036226171875
    ],
    "pitch": 0.003577085234375,
    "dimensions": [
      21,
      256,
      32
    ],
    "intersection": 5515,
    "union": 10471,
    "source_occupied": 10179,
    "cad_occupied": 5807
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
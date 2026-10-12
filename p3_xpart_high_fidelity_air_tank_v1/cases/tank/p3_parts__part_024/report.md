{
  "case_id": "tank",
  "part_id": "p3_parts__part_024",
  "source_path": "tank/p3_parts/part_024.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x8 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 2783,
  "cad_brep_face_count": 170,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.06439205071586296,
  "iou128": 0.055344540433026994,
  "iou256": 0.059063871042380894,
  "cd": 0.013105550078479732,
  "ncd": 0.043003911024360915,
  "hausdorff": 0.07826445973915377,
  "nhd": 0.2568131702093859,
  "normal_consistency": 0.7242421911562587,
  "bbox_error": 0.18474591726287795,
  "centroid_error": 0.062303852713907086,
  "surface_area_error": 0.43019752536310235,
  "volume_error": 0.8958056152304156,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      0.243627545,
      -0.662048905,
      -0.386345185
    ],
    "pitch": 0.0034409099999999993,
    "dimensions": [
      57,
      64,
      25
    ],
    "intersection": 1808,
    "union": 28078,
    "source_occupied": 26796,
    "cad_occupied": 3090
  },
  "grid128": {
    "origin": [
      0.2427673175,
      -0.6629091324999999,
      -0.3872054125
    ],
    "pitch": 0.0017204549999999996,
    "dimensions": [
      113,
      128,
      49
    ],
    "intersection": 13857,
    "union": 250377,
    "source_occupied": 239732,
    "cad_occupied": 24502
  },
  "grid256": {
    "origin": [
      0.24233720374999998,
      -0.66333924625,
      -0.38763552625
    ],
    "pitch": 0.0008602274999999998,
    "dimensions": [
      226,
      256,
      97
    ],
    "intersection": 112828,
    "union": 1910271,
    "source_occupied": 1827943,
    "cad_occupied": 195156
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
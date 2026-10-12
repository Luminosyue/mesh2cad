{
  "case_id": "tank",
  "part_id": "p3_parts__part_039",
  "source_path": "tank/p3_parts/part_039.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x6 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 14377,
  "cad_brep_face_count": 122,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.48043478260869565,
  "iou128": 0.3210837745250701,
  "iou256": 0.37979187049719826,
  "cd": 0.026016785763052358,
  "ncd": 0.01937421824743757,
  "hausdorff": 0.3388961266777843,
  "nhd": 0.25236966554074125,
  "normal_consistency": 0.75792551092808,
  "bbox_error": 0.25163535143911103,
  "centroid_error": 0.01329577163299663,
  "surface_area_error": 0.2349739737213964,
  "volume_error": 0.6592006744558322,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.661106434375,
      -0.686218644375,
      0.217804615625
    ],
    "pitch": 0.02034587125,
    "dimensions": [
      64,
      14,
      9
    ],
    "intersection": 442,
    "union": 920,
    "source_occupied": 873,
    "cad_occupied": 489
  },
  "grid128": {
    "origin": [
      -0.6661929021875,
      -0.6913051121875,
      0.2127181478125
    ],
    "pitch": 0.010172935625,
    "dimensions": [
      128,
      28,
      18
    ],
    "intersection": 3093,
    "union": 9633,
    "source_occupied": 8963,
    "cad_occupied": 3763
  },
  "grid256": {
    "origin": [
      -0.66873613609375,
      -0.69384834609375,
      0.21017491390625
    ],
    "pitch": 0.0050864678125,
    "dimensions": [
      256,
      55,
      35
    ],
    "intersection": 25620,
    "union": 67458,
    "source_occupied": 61900,
    "cad_occupied": 31178
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
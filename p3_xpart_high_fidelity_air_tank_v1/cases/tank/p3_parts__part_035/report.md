{
  "case_id": "tank",
  "part_id": "p3_parts__part_035",
  "source_path": "tank/p3_parts/part_035.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x4 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 8016,
  "cad_brep_face_count": 74,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.08340128993995106,
  "iou128": 0.07959934876477667,
  "iou256": 0.0815968102848333,
  "cd": 0.03701901338985232,
  "ncd": 0.07052771915319457,
  "hausdorff": 0.25827581788940257,
  "nhd": 0.49206077310419855,
  "normal_consistency": 0.6506022432469332,
  "bbox_error": 0.5078982333642715,
  "centroid_error": 0.06830906035114144,
  "surface_area_error": 0.7507006443960018,
  "volume_error": 0.9684767422696244,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.9120378885937499,
      -0.6903629085937499,
      0.22730015140624998
    ],
    "pitch": 0.006783642812499999,
    "dimensions": [
      64,
      37,
      24
    ],
    "intersection": 1125,
    "union": 13489,
    "source_occupied": 13311,
    "cad_occupied": 1303
  },
  "grid128": {
    "origin": [
      -0.9137337992968749,
      -0.692058819296875,
      0.225604240703125
    ],
    "pitch": 0.0033918214062499995,
    "dimensions": [
      128,
      74,
      47
    ],
    "intersection": 8996,
    "union": 113016,
    "source_occupied": 111539,
    "cad_occupied": 10473
  },
  "grid256": {
    "origin": [
      -0.9145817546484375,
      -0.6929067746484375,
      0.2247562853515625
    ],
    "pitch": 0.0016959107031249998,
    "dimensions": [
      256,
      148,
      93
    ],
    "intersection": 71873,
    "union": 880831,
    "source_occupied": 868982,
    "cad_occupied": 83722
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
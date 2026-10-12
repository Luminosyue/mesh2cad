{
  "case_id": "tank",
  "part_id": "p3_parts__part_029",
  "source_path": "tank/p3_parts/part_029.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x16 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 6750,
  "cad_brep_face_count": 362,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.13826530612244897,
  "iou128": 0.1410975776652525,
  "iou256": 0.1353909327635708,
  "cd": 0.014606944355229759,
  "ncd": 0.019509106768447432,
  "hausdorff": 0.08352734292770969,
  "nhd": 0.11155953029135635,
  "normal_consistency": 0.5732148946289772,
  "bbox_error": 0.06270924908863054,
  "centroid_error": 0.020855409690880657,
  "surface_area_error": 1.6284739905401002,
  "volume_error": 0.8715613139056662,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.8529297271875,
      -0.2577981171875,
      0.2434804528125
    ],
    "pitch": 0.011063065625,
    "dimensions": [
      64,
      16,
      16
    ],
    "intersection": 271,
    "union": 1960,
    "source_occupied": 1879,
    "cad_occupied": 352
  },
  "grid128": {
    "origin": [
      -0.85569549359375,
      -0.26056388359375005,
      0.24071468640625002
    ],
    "pitch": 0.0055315328125,
    "dimensions": [
      128,
      31,
      32
    ],
    "intersection": 2062,
    "union": 14614,
    "source_occupied": 13993,
    "cad_occupied": 2683
  },
  "grid256": {
    "origin": [
      -0.857078376796875,
      -0.261946766796875,
      0.239331803203125
    ],
    "pitch": 0.00276576640625,
    "dimensions": [
      256,
      61,
      64
    ],
    "intersection": 16222,
    "union": 119816,
    "source_occupied": 114650,
    "cad_occupied": 21388
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
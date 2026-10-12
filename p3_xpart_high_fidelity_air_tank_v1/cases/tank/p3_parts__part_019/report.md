{
  "case_id": "tank",
  "part_id": "p3_parts__part_019",
  "source_path": "tank/p3_parts/part_019.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x6 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 1637,
  "cad_brep_face_count": 122,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.3657887823459871,
  "iou128": 0.3674057640524035,
  "iou256": 0.3670601982328399,
  "cd": 0.01802456887754083,
  "ncd": 0.06208360414339111,
  "hausdorff": 0.1215889062705186,
  "nhd": 0.4187993386367564,
  "normal_consistency": 0.6575062215321652,
  "bbox_error": 0.33187387720135386,
  "centroid_error": 0.07685440464536832,
  "surface_area_error": 0.3658075462024895,
  "volume_error": 0.9837970286106619,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.930327101015625,
      -0.44217179101562504,
      -0.41515214101562503
    ],
    "pitch": 0.0027586579687500002,
    "dimensions": [
      62,
      57,
      64
    ],
    "intersection": 11139,
    "union": 30452,
    "source_occupied": 28857,
    "cad_occupied": 12734
  },
  "grid128": {
    "origin": [
      -0.9310167655078124,
      -0.44286145550781253,
      -0.4158418055078125
    ],
    "pitch": 0.0013793289843750001,
    "dimensions": [
      124,
      113,
      128
    ],
    "intersection": 89097,
    "union": 242503,
    "source_occupied": 229707,
    "cad_occupied": 101893
  },
  "grid256": {
    "origin": [
      -0.9313615977539063,
      -0.44320628775390625,
      -0.41618663775390624
    ],
    "pitch": 0.0006896644921875001,
    "dimensions": [
      248,
      225,
      256
    ],
    "intersection": 713075,
    "union": 1942665,
    "source_occupied": 1840583,
    "cad_occupied": 815157
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
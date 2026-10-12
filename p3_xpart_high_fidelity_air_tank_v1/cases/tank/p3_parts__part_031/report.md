{
  "case_id": "tank",
  "part_id": "p3_parts__part_031",
  "source_path": "tank/p3_parts/part_031.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x4 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 3867,
  "cad_brep_face_count": 74,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.002066768091397078,
  "iou128": 0.002223060178598975,
  "iou256": 0.002177212093407709,
  "cd": 0.03157895579465033,
  "ncd": 0.1002641026240823,
  "hausdorff": 0.11781967801277661,
  "nhd": 0.37408090261840055,
  "normal_consistency": 0.49282262198580273,
  "bbox_error": 0.16054411649049424,
  "centroid_error": 0.03912427521872596,
  "surface_area_error": 0.9207029422471288,
  "volume_error": 0.9970684446076372,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.718519879140625,
      -0.661696929140625,
      0.239407790859375
    ],
    "pitch": 0.0031790417187499993,
    "dimensions": [
      61,
      64,
      46
    ],
    "intersection": 144,
    "union": 69674,
    "source_occupied": 69623,
    "cad_occupied": 195
  },
  "grid128": {
    "origin": [
      -0.7193146395703125,
      -0.6624916895703125,
      0.2386130304296875
    ],
    "pitch": 0.0015895208593749996,
    "dimensions": [
      122,
      128,
      91
    ],
    "intersection": 1297,
    "union": 583430,
    "source_occupied": 583245,
    "cad_occupied": 1482
  },
  "grid256": {
    "origin": [
      -0.7197120197851563,
      -0.6628890697851563,
      0.23821565021484375
    ],
    "pitch": 0.0007947604296874998,
    "dimensions": [
      243,
      256,
      181
    ],
    "intersection": 10004,
    "union": 4594867,
    "source_occupied": 4593080,
    "cad_occupied": 11791
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
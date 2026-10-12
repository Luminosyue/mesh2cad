{
  "case_id": "tank",
  "part_id": "p3_parts__part_011",
  "source_path": "tank/p3_parts/part_011.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x4 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 2436,
  "cad_brep_face_count": 74,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.2402051282051282,
  "iou128": 0.2377021578674336,
  "iou256": 0.24022025843760056,
  "cd": 0.01982281307012668,
  "ncd": 0.06664223184286856,
  "hausdorff": 0.09164252934947623,
  "nhd": 0.3080926337734795,
  "normal_consistency": 0.6595737157192831,
  "bbox_error": 0.20943687795563165,
  "centroid_error": 0.11066917172299687,
  "surface_area_error": 0.4306283402654067,
  "volume_error": 0.800436946508447,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      0.046484780859375,
      -0.661696929140625,
      -0.33604807914062496
    ],
    "pitch": 0.0031790417187499993,
    "dimensions": [
      61,
      64,
      31
    ],
    "intersection": 7026,
    "union": 29250,
    "source_occupied": 26839,
    "cad_occupied": 9437
  },
  "grid128": {
    "origin": [
      0.0456900204296875,
      -0.6624916895703125,
      -0.33684283957031247
    ],
    "pitch": 0.0015895208593749996,
    "dimensions": [
      122,
      128,
      62
    ],
    "intersection": 52236,
    "union": 219754,
    "source_occupied": 196892,
    "cad_occupied": 75098
  },
  "grid256": {
    "origin": [
      0.04529264021484375,
      -0.6628890697851563,
      -0.3372402197851562
    ],
    "pitch": 0.0007947604296874998,
    "dimensions": [
      244,
      256,
      123
    ],
    "intersection": 433765,
    "union": 1805697,
    "source_occupied": 1639077,
    "cad_occupied": 600385
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
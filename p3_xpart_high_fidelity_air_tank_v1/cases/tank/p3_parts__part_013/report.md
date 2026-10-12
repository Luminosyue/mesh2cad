{
  "case_id": "tank",
  "part_id": "p3_parts__part_013",
  "source_path": "tank/p3_parts/part_013.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x4 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 2685,
  "cad_brep_face_count": 74,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.4121505233867762,
  "iou128": 0.4293042180313833,
  "iou256": 0.4323993777445053,
  "cd": 0.012580839608432232,
  "ncd": 0.04136504388520927,
  "hausdorff": 0.07491679799103723,
  "nhd": 0.24632192549069376,
  "normal_consistency": 0.7701157137888781,
  "bbox_error": 0.16718924487268194,
  "centroid_error": 0.06486983128088093,
  "surface_area_error": 0.2411198210527106,
  "volume_error": 0.4763705539726285,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      0.243617957734375,
      -0.668969652265625,
      -0.33592673226562497
    ],
    "pitch": 0.00342173546875,
    "dimensions": [
      55,
      64,
      29
    ],
    "intersection": 12442,
    "union": 30188,
    "source_occupied": 21432,
    "cad_occupied": 21198
  },
  "grid128": {
    "origin": [
      0.2427625238671875,
      -0.6698250861328126,
      -0.3367821661328125
    ],
    "pitch": 0.001710867734375,
    "dimensions": [
      110,
      128,
      58
    ],
    "intersection": 113320,
    "union": 263962,
    "source_occupied": 206331,
    "cad_occupied": 170951
  },
  "grid256": {
    "origin": [
      0.24233480693359374,
      -0.6702528030664062,
      -0.33720988306640626
    ],
    "pitch": 0.0008554338671875,
    "dimensions": [
      219,
      256,
      115
    ],
    "intersection": 881399,
    "union": 2038391,
    "source_occupied": 1552726,
    "cad_occupied": 1367064
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
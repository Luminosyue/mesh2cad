{
  "case_id": "tank",
  "part_id": "p3_parts__part_007",
  "source_path": "tank/p3_parts/part_007.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x7 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 1690,
  "cad_brep_face_count": 146,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.4441391201271586,
  "iou128": 0.4425253825829209,
  "iou256": 0.44303698710637834,
  "cd": 0.016044437671131846,
  "ncd": 0.058847214092430135,
  "hausdorff": 0.11783765920160119,
  "nhd": 0.43220074778091366,
  "normal_consistency": 0.6819899858959935,
  "bbox_error": 0.2908299425098778,
  "centroid_error": 0.07630972100351323,
  "surface_area_error": 0.23794384544210118,
  "volume_error": 0.9760901404236367,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.93297180546875,
      -0.43405705546875,
      0.24525744453124998
    ],
    "pitch": 0.0027113490625,
    "dimensions": [
      64,
      52,
      59
    ],
    "intersection": 16486,
    "union": 37119,
    "source_occupied": 34358,
    "cad_occupied": 19247
  },
  "grid128": {
    "origin": [
      -0.933649642734375,
      -0.43473489273437504,
      0.244579607265625
    ],
    "pitch": 0.00135567453125,
    "dimensions": [
      128,
      103,
      117
    ],
    "intersection": 131977,
    "union": 298236,
    "source_occupied": 276213,
    "cad_occupied": 154000
  },
  "grid256": {
    "origin": [
      -0.9339885613671874,
      -0.43507381136718754,
      0.24424068863281248
    ],
    "pitch": 0.000677837265625,
    "dimensions": [
      256,
      205,
      234
    ],
    "intersection": 1056221,
    "union": 2384047,
    "source_occupied": 2207651,
    "cad_occupied": 1232617
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
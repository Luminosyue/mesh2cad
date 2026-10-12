{
  "case_id": "tank",
  "part_id": "p3_parts__part_032",
  "source_path": "tank/p3_parts/part_032.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x4 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 2364,
  "cad_brep_face_count": 74,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.18456556934700485,
  "iou128": 0.19001915807039543,
  "iou256": 0.18010161172585057,
  "cd": 0.018065715166862128,
  "ncd": 0.059224003540015446,
  "hausdorff": 0.10828755785604624,
  "nhd": 0.3549941228770096,
  "normal_consistency": 0.7799422730923244,
  "bbox_error": 0.36038857865939655,
  "centroid_error": 0.10934926758229292,
  "surface_area_error": 0.4674765533292044,
  "volume_error": 0.8025721563820639,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.1406083759375,
      -0.6860231659374999,
      -0.3278208559375
    ],
    "pitch": 0.003356708124999999,
    "dimensions": [
      59,
      64,
      28
    ],
    "intersection": 4446,
    "union": 24089,
    "source_occupied": 21809,
    "cad_occupied": 6726
  },
  "grid128": {
    "origin": [
      -0.14144755296875,
      -0.6868623429687499,
      -0.32866003296874996
    ],
    "pitch": 0.0016783540624999995,
    "dimensions": [
      117,
      128,
      55
    ],
    "intersection": 40765,
    "union": 214531,
    "source_occupied": 198808,
    "cad_occupied": 56488
  },
  "grid256": {
    "origin": [
      -0.141867141484375,
      -0.687281931484375,
      -0.329079621484375
    ],
    "pitch": 0.0008391770312499997,
    "dimensions": [
      234,
      256,
      109
    ],
    "intersection": 308158,
    "union": 1711023,
    "source_occupied": 1574300,
    "cad_occupied": 444881
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
{
  "case_id": "tank",
  "part_id": "xpart_parts__PART_001",
  "source_path": "tank/xpart_parts/PART_001.stl",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x21 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 8536,
  "cad_brep_face_count": 482,
  "quality_level": "C_NEAR_MISS",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.9095022624434389,
  "iou128": 0.8697878566203365,
  "iou256": 0.8696358351855018,
  "cd": 0.0015427362750866306,
  "ncd": 0.0016204202993988647,
  "hausdorff": 0.013996490801509073,
  "nhd": 0.014701279915027088,
  "normal_consistency": 0.955687189109277,
  "bbox_error": 0.016684922065558515,
  "centroid_error": 0.00997623703814852,
  "surface_area_error": 0.062252720145055195,
  "volume_error": 0.09914958906412515,
  "IOU_VALID": true,
  "grid64": {
    "origin": [
      -0.5218888560775667,
      -0.24837914505042136,
      0.2957805653568357
    ],
    "pitch": 0.014756313990801573,
    "dimensions": [
      4,
      64,
      8
    ],
    "intersection": 201,
    "union": 221,
    "source_occupied": 219,
    "cad_occupied": 203
  },
  "grid128": {
    "origin": [
      -0.5255779345752671,
      -0.25206822354812175,
      0.29209148685913533
    ],
    "pitch": 0.007378156995400786,
    "dimensions": [
      7,
      128,
      16
    ],
    "intersection": 1189,
    "union": 1367,
    "source_occupied": 1350,
    "cad_occupied": 1206
  },
  "grid256": {
    "origin": [
      -0.5274224738241173,
      -0.25391276279697195,
      0.29024694761028513
    ],
    "pitch": 0.003689078497700393,
    "dimensions": [
      13,
      256,
      31
    ],
    "intersection": 10173,
    "union": 11698,
    "source_occupied": 11518,
    "cad_occupied": 10353
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
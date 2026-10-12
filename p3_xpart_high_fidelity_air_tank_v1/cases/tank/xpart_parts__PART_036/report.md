{
  "case_id": "tank",
  "part_id": "xpart_parts__PART_036",
  "source_path": "tank/xpart_parts/PART_036.stl",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x21 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 11724,
  "cad_brep_face_count": 482,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.47833935018050544,
  "iou128": 0.5303933253873659,
  "iou256": 0.5284323846040407,
  "cd": 0.004760122168688791,
  "ncd": 0.007946947178202476,
  "hausdorff": 0.06372322475511391,
  "nhd": 0.10638489585092047,
  "normal_consistency": 0.7654465356524895,
  "bbox_error": 0.013696775434086943,
  "centroid_error": 0.01214537312833371,
  "surface_area_error": 0.18350188174301682,
  "volume_error": 0.31309230027323803,
  "IOU_VALID": true,
  "grid64": {
    "origin": [
      -0.7303076672833413,
      -0.23568156245164573,
      -0.3919553745072335
    ],
    "pitch": 0.008845629636198282,
    "dimensions": [
      64,
      15,
      17
    ],
    "intersection": 530,
    "union": 1108,
    "source_occupied": 997,
    "cad_occupied": 641
  },
  "grid128": {
    "origin": [
      -0.7325190746923909,
      -0.2378929698606953,
      -0.39416678191628307
    ],
    "pitch": 0.004422814818099141,
    "dimensions": [
      128,
      30,
      33
    ],
    "intersection": 4450,
    "union": 8390,
    "source_occupied": 7567,
    "cad_occupied": 5273
  },
  "grid256": {
    "origin": [
      -0.7336247783969156,
      -0.2389986735652201,
      -0.39527248562080786
    ],
    "pitch": 0.0022114074090495706,
    "dimensions": [
      256,
      60,
      66
    ],
    "intersection": 35833,
    "union": 67810,
    "source_occupied": 61457,
    "cad_occupied": 42186
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
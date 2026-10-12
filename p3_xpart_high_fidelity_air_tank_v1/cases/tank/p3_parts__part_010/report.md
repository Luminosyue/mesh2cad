{
  "case_id": "tank",
  "part_id": "p3_parts__part_010",
  "source_path": "tank/p3_parts/part_010.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x12 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 5733,
  "cad_brep_face_count": 266,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.517147325162745,
  "iou128": 0.5146351633708466,
  "iou256": 0.5160396387464141,
  "cd": 0.012303520544228383,
  "ncd": 0.02840538283326222,
  "hausdorff": 0.09286472033864293,
  "nhd": 0.21439862870472562,
  "normal_consistency": 0.7412294259371899,
  "bbox_error": 0.15815015399243668,
  "centroid_error": 0.033190848706914744,
  "surface_area_error": 0.10483561016537256,
  "volume_error": 0.5637180254540249,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      0.1447807784375,
      -0.0751001015625,
      -0.4034874515625
    ],
    "pitch": 0.004450656875,
    "dimensions": [
      64,
      38,
      63
    ],
    "intersection": 28440,
    "union": 54994,
    "source_occupied": 54692,
    "cad_occupied": 28742
  },
  "grid128": {
    "origin": [
      0.14366811421875,
      -0.07621276578125,
      -0.40460011578125
    ],
    "pitch": 0.0022253284375,
    "dimensions": [
      128,
      76,
      126
    ],
    "intersection": 227091,
    "union": 441266,
    "source_occupied": 439060,
    "cad_occupied": 229297
  },
  "grid256": {
    "origin": [
      0.143111782109375,
      -0.076769097890625,
      -0.405156447890625
    ],
    "pitch": 0.00111266421875,
    "dimensions": [
      256,
      152,
      252
    ],
    "intersection": 1815413,
    "union": 3517972,
    "source_occupied": 3500022,
    "cad_occupied": 1833363
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
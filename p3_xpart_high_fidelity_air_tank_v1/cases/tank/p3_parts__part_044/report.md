{
  "case_id": "tank",
  "part_id": "p3_parts__part_044",
  "source_path": "tank/p3_parts/part_044.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x7 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 5639,
  "cad_brep_face_count": 146,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.015228426395939087,
  "iou128": 0.04210009009746908,
  "iou256": 0.04246273625979614,
  "cd": 0.0173275187222684,
  "ncd": 0.02563554857072241,
  "hausdorff": 0.11318923729272852,
  "nhd": 0.1674601099447492,
  "normal_consistency": 0.9034417976478837,
  "bbox_error": 0.1433328930516059,
  "centroid_error": 0.04730118467347214,
  "surface_area_error": 0.4423909626889285,
  "volume_error": 0.995743345554554,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      0.520855866875,
      -0.13849580312499998,
      -0.227409113125
    ],
    "pitch": 0.00787287375,
    "dimensions": [
      56,
      14,
      64
    ],
    "intersection": 24,
    "union": 1576,
    "source_occupied": 1524,
    "cad_occupied": 76
  },
  "grid128": {
    "origin": [
      0.5188876484374999,
      -0.14046402156249999,
      -0.2293773315625
    ],
    "pitch": 0.003936436875,
    "dimensions": [
      112,
      28,
      128
    ],
    "intersection": 514,
    "union": 12209,
    "source_occupied": 11782,
    "cad_occupied": 941
  },
  "grid256": {
    "origin": [
      0.51790353921875,
      -0.14144813078125,
      -0.23036144078125
    ],
    "pitch": 0.0019682184375,
    "dimensions": [
      223,
      55,
      256
    ],
    "intersection": 4145,
    "union": 97615,
    "source_occupied": 94077,
    "cad_occupied": 7683
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
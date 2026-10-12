{
  "case_id": "airplane",
  "part_id": "p3_parts__part_008",
  "source_path": "airplane/p3_parts/part_008.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x8 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 2330,
  "cad_brep_face_count": 170,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.2665056360708535,
  "iou128": 0.27519582245430807,
  "iou256": 0.2692287777979134,
  "cd": 0.010559610885772189,
  "ncd": 0.01821554416959561,
  "hausdorff": 0.10791595720129993,
  "nhd": 0.1861572274081688,
  "normal_consistency": 0.9332827944707358,
  "bbox_error": 0.1874807065811841,
  "centroid_error": 0.012005965806828882,
  "surface_area_error": 0.14606198391786518,
  "volume_error": 0.6904891423981397,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.07304822578124999,
      -0.7617818457812501,
      0.12253431421875001
    ],
    "pitch": 0.008729388437500001,
    "dimensions": [
      16,
      64,
      8
    ],
    "intersection": 331,
    "union": 1242,
    "source_occupied": 1242,
    "cad_occupied": 331
  },
  "grid128": {
    "origin": [
      -0.075230572890625,
      -0.763964192890625,
      0.120351967109375
    ],
    "pitch": 0.0043646942187500004,
    "dimensions": [
      32,
      128,
      16
    ],
    "intersection": 2635,
    "union": 9575,
    "source_occupied": 9572,
    "cad_occupied": 2638
  },
  "grid256": {
    "origin": [
      -0.07632174644531249,
      -0.7650553664453126,
      0.11926079355468751
    ],
    "pitch": 0.0021823471093750002,
    "dimensions": [
      64,
      256,
      32
    ],
    "intersection": 20799,
    "union": 77254,
    "source_occupied": 77240,
    "cad_occupied": 20813
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
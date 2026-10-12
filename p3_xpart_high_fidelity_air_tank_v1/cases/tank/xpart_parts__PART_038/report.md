{
  "case_id": "tank",
  "part_id": "xpart_parts__PART_038",
  "source_path": "tank/xpart_parts/PART_038.stl",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x21 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 41276,
  "cad_brep_face_count": 482,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.7933836331979106,
  "iou128": 0.7735210824417873,
  "iou256": 0.7770684877276326,
  "cd": 0.005717767604729706,
  "ncd": 0.005550771435808439,
  "hausdorff": 0.09730138303469531,
  "nhd": 0.09445954696844913,
  "normal_consistency": 0.8723826131247107,
  "bbox_error": 0.022051636857919613,
  "centroid_error": 0.03270423323190058,
  "surface_area_error": 0.1705693512519476,
  "volume_error": 0.13382759944625708,
  "IOU_VALID": true,
  "grid64": {
    "origin": [
      -0.3580106107983738,
      -0.687782576540485,
      -0.37541448161937296
    ],
    "pitch": 0.015381354372948408,
    "dimensions": [
      64,
      18,
      10
    ],
    "intersection": 1367,
    "union": 1723,
    "source_occupied": 1655,
    "cad_occupied": 1435
  },
  "grid128": {
    "origin": [
      -0.3618559493916109,
      -0.6916279151337221,
      -0.37925982021261007
    ],
    "pitch": 0.007690677186474204,
    "dimensions": [
      128,
      35,
      19
    ],
    "intersection": 9833,
    "union": 12712,
    "source_occupied": 12093,
    "cad_occupied": 10452
  },
  "grid256": {
    "origin": [
      -0.36377861868822947,
      -0.6935505844303407,
      -0.3811824895092286
    ],
    "pitch": 0.003845338593237102,
    "dimensions": [
      256,
      70,
      38
    ],
    "intersection": 78515,
    "union": 101040,
    "source_occupied": 96308,
    "cad_occupied": 83247
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
{
  "case_id": "tank",
  "part_id": "p3_parts__part_028",
  "source_path": "tank/p3_parts/part_028.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x5 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 2600,
  "cad_brep_face_count": 98,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.002315652362689051,
  "iou128": 0.002493948171638547,
  "iou256": 0.002449821490463054,
  "cd": 0.031238598848088103,
  "ncd": 0.10357918629539843,
  "hausdorff": 0.14536760222374517,
  "nhd": 0.48200170645522455,
  "normal_consistency": 0.6088571543699688,
  "bbox_error": 0.3782038184728523,
  "centroid_error": 0.15808504011214203,
  "surface_area_error": 0.9440728970983746,
  "volume_error": 1.0040722286871966,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      0.42898701265625,
      -0.61255396734375,
      -0.38647611734375
    ],
    "pitch": 0.003179045312500001,
    "dimensions": [
      64,
      62,
      34
    ],
    "intersection": 64,
    "union": 27638,
    "source_occupied": 27588,
    "cad_occupied": 114
  },
  "grid128": {
    "origin": [
      0.428192251328125,
      -0.6133487286718751,
      -0.387270878671875
    ],
    "pitch": 0.0015895226562500004,
    "dimensions": [
      128,
      123,
      68
    ],
    "intersection": 545,
    "union": 218529,
    "source_occupied": 218132,
    "cad_occupied": 942
  },
  "grid256": {
    "origin": [
      0.42779487066406247,
      -0.6137461093359375,
      -0.3876682593359375
    ],
    "pitch": 0.0007947613281250002,
    "dimensions": [
      256,
      246,
      136
    ],
    "intersection": 4347,
    "union": 1774415,
    "source_occupied": 1771272,
    "cad_occupied": 7490
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
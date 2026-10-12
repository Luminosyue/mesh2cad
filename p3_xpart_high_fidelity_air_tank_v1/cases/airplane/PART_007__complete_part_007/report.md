{
  "case_id": "airplane",
  "part_id": "PART_007__complete_part_007",
  "source_path": "airplane/xpart_parts/PART_007/complete_part_007.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x21 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 29800,
  "cad_brep_face_count": 482,
  "quality_level": "A_HIGH_CONFIDENCE",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.9642580244999225,
  "iou128": 0.965001745065343,
  "iou256": 0.9647886641050194,
  "cd": 0.0019036282786705915,
  "ncd": 0.002962407944755168,
  "hausdorff": 0.008603924958427994,
  "nhd": 0.013389344935936904,
  "normal_consistency": 0.9895109630351958,
  "bbox_error": 0.009675488979965435,
  "centroid_error": 0.02407749049818114,
  "surface_area_error": 0.2577772998400659,
  "volume_error": 0.01906336018564698,
  "IOU_VALID": true,
  "grid64": {
    "origin": [
      -0.381414896171875,
      0.395804183828125,
      -0.142432076171875
    ],
    "pitch": 0.0073775476562500004,
    "dimensions": [
      64,
      58,
      14
    ],
    "intersection": 12437,
    "union": 12898,
    "source_occupied": 12801,
    "cad_occupied": 12534
  },
  "grid128": {
    "origin": [
      -0.3832592830859375,
      0.3939597969140625,
      -0.1442764630859375
    ],
    "pitch": 0.0036887738281250002,
    "dimensions": [
      128,
      116,
      27
    ],
    "intersection": 99538,
    "union": 103148,
    "source_occupied": 102315,
    "cad_occupied": 100371
  },
  "grid256": {
    "origin": [
      -0.38418147654296875,
      0.39303760345703126,
      -0.14519865654296873
    ],
    "pitch": 0.0018443869140625001,
    "dimensions": [
      256,
      231,
      54
    ],
    "intersection": 795941,
    "union": 824990,
    "source_occupied": 818254,
    "cad_occupied": 802677
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
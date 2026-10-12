{
  "case_id": "airplane",
  "part_id": "p3_parts__part_007",
  "source_path": "airplane/p3_parts/part_007.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x13 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 9832,
  "cad_brep_face_count": 290,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.6185036623648413,
  "iou128": 0.6199015317286652,
  "iou256": 0.6199092919053212,
  "cd": 0.013867560844453885,
  "ncd": 0.021432942976824448,
  "hausdorff": 0.20936438166391108,
  "nhd": 0.3235821283867191,
  "normal_consistency": 0.7984010356906102,
  "bbox_error": 0.1533518076920581,
  "centroid_error": 0.0903899195096856,
  "surface_area_error": 0.2891203166190911,
  "volume_error": 0.28383245313769445,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.38223868796875,
      0.39732528203125,
      -0.14235520796875
    ],
    "pitch": 0.0074923040625,
    "dimensions": [
      64,
      57,
      14
    ],
    "intersection": 7093,
    "union": 11468,
    "source_occupied": 11464,
    "cad_occupied": 7097
  },
  "grid128": {
    "origin": [
      -0.384111763984375,
      0.395452206015625,
      -0.144228283984375
    ],
    "pitch": 0.00374615203125,
    "dimensions": [
      128,
      113,
      28
    ],
    "intersection": 56659,
    "union": 91400,
    "source_occupied": 91351,
    "cad_occupied": 56708
  },
  "grid256": {
    "origin": [
      -0.3850483019921875,
      0.3945156680078125,
      -0.14516482199218753
    ],
    "pitch": 0.001873076015625,
    "dimensions": [
      256,
      226,
      55
    ],
    "intersection": 453375,
    "union": 731357,
    "source_occupied": 730918,
    "cad_occupied": 453814
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
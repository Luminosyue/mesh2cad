{
  "case_id": "tank",
  "part_id": "p3_parts__part_021",
  "source_path": "tank/p3_parts/part_021.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x8 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 2617,
  "cad_brep_face_count": 170,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.19481529049920573,
  "iou128": 0.188981973732763,
  "iou256": 0.19515877855277253,
  "cd": 0.015163843123092543,
  "ncd": 0.05056738421881553,
  "hausdorff": 0.07911270316457182,
  "nhd": 0.2638198262167284,
  "normal_consistency": 0.6845558137376846,
  "bbox_error": 0.11604535994757605,
  "centroid_error": 0.052630335787764895,
  "surface_area_error": 0.4114869287873107,
  "volume_error": 0.7333264965384243,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      0.046548362265625,
      -0.669771767734375,
      -0.382509737734375
    ],
    "pitch": 0.003306204531249999,
    "dimensions": [
      59,
      64,
      27
    ],
    "intersection": 5764,
    "union": 29587,
    "source_occupied": 27391,
    "cad_occupied": 7960
  },
  "grid128": {
    "origin": [
      0.0457218111328125,
      -0.6705983188671875,
      -0.3833362888671875
    ],
    "pitch": 0.0016531022656249995,
    "dimensions": [
      118,
      128,
      53
    ],
    "intersection": 41484,
    "union": 219513,
    "source_occupied": 197231,
    "cad_occupied": 63766
  },
  "grid256": {
    "origin": [
      0.04530853556640625,
      -0.6710115944335937,
      -0.38374956443359376
    ],
    "pitch": 0.0008265511328124997,
    "dimensions": [
      235,
      256,
      106
    ],
    "intersection": 350141,
    "union": 1794134,
    "source_occupied": 1634564,
    "cad_occupied": 509711
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
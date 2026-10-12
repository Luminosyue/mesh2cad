{
  "case_id": "airplane",
  "part_id": "p3_parts__part_003",
  "source_path": "airplane/p3_parts/part_003.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x17 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 2491,
  "cad_brep_face_count": 386,
  "quality_level": "C_NEAR_MISS",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.8526222222222222,
  "iou128": 0.8528009269575293,
  "iou256": 0.8549195485009999,
  "cd": 0.0023153378247690293,
  "ncd": 0.007045807912819478,
  "hausdorff": 0.07073312027356184,
  "nhd": 0.21524806150981005,
  "normal_consistency": 0.9182490114341846,
  "bbox_error": 0.14700482993598044,
  "centroid_error": 0.03356381332309131,
  "surface_area_error": 0.10415655583986727,
  "volume_error": 0.08201498039401271,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.0525817190625,
      -0.9602957890625,
      -0.0465176490625
    ],
    "pitch": 0.0045242418749999996,
    "dimensions": [
      64,
      23,
      27
    ],
    "intersection": 4796,
    "union": 5625,
    "source_occupied": 5616,
    "cad_occupied": 4805
  },
  "grid128": {
    "origin": [
      -0.05371277953125,
      -0.96142684953125,
      -0.04764870953125
    ],
    "pitch": 0.0022621209374999998,
    "dimensions": [
      128,
      45,
      53
    ],
    "intersection": 38272,
    "union": 44878,
    "source_occupied": 44765,
    "cad_occupied": 38385
  },
  "grid256": {
    "origin": [
      -0.054278309765625,
      -0.961992379765625,
      -0.048214239765625
    ],
    "pitch": 0.0011310604687499999,
    "dimensions": [
      256,
      90,
      105
    ],
    "intersection": 306522,
    "union": 358539,
    "source_occupied": 357676,
    "cad_occupied": 307385
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
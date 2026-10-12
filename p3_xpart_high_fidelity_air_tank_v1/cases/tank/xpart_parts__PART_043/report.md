{
  "case_id": "tank",
  "part_id": "xpart_parts__PART_043",
  "source_path": "tank/xpart_parts/PART_043.stl",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x21 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 22776,
  "cad_brep_face_count": 482,
  "quality_level": "C_NEAR_MISS",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.8888202594193947,
  "iou128": 0.8900347537020248,
  "iou256": 0.8895889067661872,
  "cd": 0.0016798022225019004,
  "ncd": 0.0031641423357546754,
  "hausdorff": 0.013708031660271425,
  "nhd": 0.025820994123658625,
  "normal_consistency": 0.9620198050710262,
  "bbox_error": 0.004403836375717486,
  "centroid_error": 0.001860844811114763,
  "surface_area_error": 0.03873156963468229,
  "volume_error": 0.047851774969840694,
  "IOU_VALID": true,
  "grid64": {
    "origin": [
      0.5810858262702823,
      -0.4972507106140256,
      0.16704669129103422
    ],
    "pitch": 0.0060167815536260605,
    "dimensions": [
      64,
      47,
      40
    ],
    "intersection": 5756,
    "union": 6476,
    "source_occupied": 6262,
    "cad_occupied": 5970
  },
  "grid128": {
    "origin": [
      0.5795816308818758,
      -0.4987549060024321,
      0.1655424959026277
    ],
    "pitch": 0.0030083907768130302,
    "dimensions": [
      128,
      93,
      79
    ],
    "intersection": 47122,
    "union": 52944,
    "source_occupied": 51245,
    "cad_occupied": 48821
  },
  "grid256": {
    "origin": [
      0.5788295331876725,
      -0.49950700369663537,
      0.16479039820842445
    ],
    "pitch": 0.0015041953884065151,
    "dimensions": [
      256,
      185,
      158
    ],
    "intersection": 373759,
    "union": 420148,
    "source_occupied": 406636,
    "cad_occupied": 387271
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
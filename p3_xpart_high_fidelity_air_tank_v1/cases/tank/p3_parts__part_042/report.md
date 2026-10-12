{
  "case_id": "tank",
  "part_id": "p3_parts__part_042",
  "source_path": "tank/p3_parts/part_042.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x5 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 168880,
  "cad_brep_face_count": 98,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.0001658283124205406,
  "iou128": 0.00018414995067412036,
  "iou256": 0.0001775446934622581,
  "cd": 0.19792413809939852,
  "ncd": 0.09067778730299905,
  "hausdorff": 0.9798902337870995,
  "nhd": 0.44893098463316056,
  "normal_consistency": 0.5497904013258306,
  "bbox_error": 0.35179644521621306,
  "centroid_error": 0.28184844205202125,
  "surface_area_error": 0.969219898292539,
  "volume_error": 0.9955526586876577,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.963395745703125,
      -0.579170135703125,
      -0.40185534570312503
    ],
    "pitch": 0.03023284859375,
    "dimensions": [
      64,
      20,
      28
    ],
    "intersection": 3,
    "union": 18091,
    "source_occupied": 18058,
    "cad_occupied": 36
  },
  "grid128": {
    "origin": [
      -0.9709539578515625,
      -0.5867283478515625,
      -0.4094135578515625
    ],
    "pitch": 0.015116424296875,
    "dimensions": [
      128,
      40,
      55
    ],
    "intersection": 28,
    "union": 152050,
    "source_occupied": 151774,
    "cad_occupied": 304
  },
  "grid256": {
    "origin": [
      -0.9747330639257813,
      -0.5905074539257813,
      -0.41319266392578125
    ],
    "pitch": 0.0075582121484375,
    "dimensions": [
      256,
      79,
      109
    ],
    "intersection": 208,
    "union": 1171536,
    "source_occupied": 1169407,
    "cad_occupied": 2337
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
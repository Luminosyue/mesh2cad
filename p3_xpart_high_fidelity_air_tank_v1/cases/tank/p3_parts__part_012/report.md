{
  "case_id": "tank",
  "part_id": "p3_parts__part_012",
  "source_path": "tank/p3_parts/part_012.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x7 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 1750,
  "cad_brep_face_count": 146,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.07834692568496289,
  "iou128": 0.07874377281388462,
  "iou256": 0.07877230291498417,
  "cd": 0.008020094105145186,
  "ncd": 0.0337125856375583,
  "hausdorff": 0.04475679979924713,
  "nhd": 0.18813587799763806,
  "normal_consistency": 0.8044089417263787,
  "bbox_error": 0.1797941868514835,
  "centroid_error": 0.05563165468470315,
  "surface_area_error": 0.3958919781210666,
  "volume_error": 0.7899164409564627,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.012230433281250001,
      0.05423318671875,
      0.15888470671875
    ],
    "pitch": 0.0026901134375000003,
    "dimensions": [
      52,
      32,
      64
    ],
    "intersection": 1710,
    "union": 21826,
    "source_occupied": 21396,
    "cad_occupied": 2140
  },
  "grid128": {
    "origin": [
      -0.012902961640625,
      0.053560658359375,
      0.158212178359375
    ],
    "pitch": 0.0013450567187500001,
    "dimensions": [
      104,
      64,
      128
    ],
    "intersection": 13720,
    "union": 174236,
    "source_occupied": 170764,
    "cad_occupied": 17192
  },
  "grid256": {
    "origin": [
      -0.0132392258203125,
      0.053224394179687495,
      0.1578759141796875
    ],
    "pitch": 0.0006725283593750001,
    "dimensions": [
      208,
      128,
      256
    ],
    "intersection": 109790,
    "union": 1393764,
    "source_occupied": 1366741,
    "cad_occupied": 136813
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
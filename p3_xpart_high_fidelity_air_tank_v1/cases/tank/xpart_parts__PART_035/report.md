{
  "case_id": "tank",
  "part_id": "xpart_parts__PART_035",
  "source_path": "tank/xpart_parts/PART_035.stl",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x21 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 25628,
  "cad_brep_face_count": 482,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.7187081809260416,
  "iou128": 0.7151305351218809,
  "iou256": 0.715113709334423,
  "cd": 0.004714776233075552,
  "ncd": 0.00907400998381089,
  "hausdorff": 0.045703974171000306,
  "nhd": 0.0879613999532194,
  "normal_consistency": 0.8388105595056343,
  "bbox_error": 0.003677792493989374,
  "centroid_error": 0.011096342980009994,
  "surface_area_error": 0.07420802960926505,
  "volume_error": 0.17333862426694727,
  "IOU_VALID": true,
  "grid64": {
    "origin": [
      -0.9100327335763723,
      -0.6903361522126943,
      0.23913417826406658
    ],
    "pitch": 0.0067367865704,
    "dimensions": [
      64,
      38,
      22
    ],
    "intersection": 8056,
    "union": 11209,
    "source_occupied": 10556,
    "cad_occupied": 8709
  },
  "grid128": {
    "origin": [
      -0.9117169302189723,
      -0.6920203488552943,
      0.23744998162146658
    ],
    "pitch": 0.0033683932852,
    "dimensions": [
      128,
      75,
      44
    ],
    "intersection": 64454,
    "union": 90129,
    "source_occupied": 84638,
    "cad_occupied": 69945
  },
  "grid256": {
    "origin": [
      -0.9125590285402723,
      -0.6928624471765943,
      0.23660788330016658
    ],
    "pitch": 0.0016841966426,
    "dimensions": [
      256,
      149,
      87
    ],
    "intersection": 514500,
    "union": 719466,
    "source_occupied": 675612,
    "cad_occupied": 558354
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
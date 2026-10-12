{
  "case_id": "tank",
  "part_id": "p3_parts__part_015",
  "source_path": "tank/p3_parts/part_015.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x3 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 2170,
  "cad_brep_face_count": 50,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.3106630848205974,
  "iou128": 0.3050358880624781,
  "iou256": 0.30242601505648303,
  "cd": 0.01887945480572837,
  "ncd": 0.06237636131306388,
  "hausdorff": 0.07878683169305425,
  "nhd": 0.260306027423333,
  "normal_consistency": 0.703698805108938,
  "bbox_error": 0.2325663808836792,
  "centroid_error": 0.0606185425741751,
  "surface_area_error": 0.26163342649327,
  "volume_error": 0.6522499966725445,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.334090634765625,
      -0.679761134765625,
      -0.344148324765625
    ],
    "pitch": 0.0032552104687500003,
    "dimensions": [
      60,
      64,
      32
    ],
    "intersection": 11680,
    "union": 37597,
    "source_occupied": 32718,
    "cad_occupied": 16559
  },
  "grid128": {
    "origin": [
      -0.3349044373828125,
      -0.6805749373828125,
      -0.3449621273828125
    ],
    "pitch": 0.0016276052343750002,
    "dimensions": [
      119,
      128,
      64
    ],
    "intersection": 84444,
    "union": 276833,
    "source_occupied": 228928,
    "cad_occupied": 132349
  },
  "grid256": {
    "origin": [
      -0.3353113386914062,
      -0.6809818386914063,
      -0.34536902869140623
    ],
    "pitch": 0.0008138026171875001,
    "dimensions": [
      238,
      256,
      128
    ],
    "intersection": 676540,
    "union": 2237043,
    "source_occupied": 1854396,
    "cad_occupied": 1059187
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
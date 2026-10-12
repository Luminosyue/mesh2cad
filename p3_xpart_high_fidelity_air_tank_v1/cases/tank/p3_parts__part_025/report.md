{
  "case_id": "tank",
  "part_id": "p3_parts__part_025",
  "source_path": "tank/p3_parts/part_025.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x16 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 15540,
  "cad_brep_face_count": 362,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.5821803832073409,
  "iou128": 0.5858166504851477,
  "iou256": 0.5841494785855899,
  "cd": 0.012972349837992269,
  "ncd": 0.01793205334166939,
  "hausdorff": 0.12933853713565754,
  "nhd": 0.17878839038533495,
  "normal_consistency": 0.7129924088933703,
  "bbox_error": 0.04500063581877047,
  "centroid_error": 0.008438879474818233,
  "surface_area_error": 0.5836541012769045,
  "volume_error": 0.3273150860114379,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.011775548593749999,
      -0.07276423859375,
      0.05805887140625
    ],
    "pitch": 0.0091223828125,
    "dimensions": [
      64,
      25,
      40
    ],
    "intersection": 12245,
    "union": 21033,
    "source_occupied": 19256,
    "cad_occupied": 14022
  },
  "grid128": {
    "origin": [
      -0.014056144296875,
      -0.075044834296875,
      0.055778275703125
    ],
    "pitch": 0.00456119140625,
    "dimensions": [
      128,
      50,
      80
    ],
    "intersection": 98351,
    "union": 167887,
    "source_occupied": 153575,
    "cad_occupied": 112663
  },
  "grid256": {
    "origin": [
      -0.0151964421484375,
      -0.0761851321484375,
      0.0546379778515625
    ],
    "pitch": 0.002280595703125,
    "dimensions": [
      256,
      99,
      160
    ],
    "intersection": 784334,
    "union": 1342694,
    "source_occupied": 1225483,
    "cad_occupied": 901545
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
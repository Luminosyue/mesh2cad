{
  "case_id": "airplane",
  "part_id": "p3_parts__part_001",
  "source_path": "airplane/p3_parts/part_001.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x19 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 33414,
  "cad_brep_face_count": 434,
  "quality_level": "C_NEAR_MISS",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.8627812615271118,
  "iou128": 0.8648516806429882,
  "iou256": 0.8634234192498567,
  "cd": 0.004692478390726703,
  "ncd": 0.004178347971359328,
  "hausdorff": 0.10449958112918407,
  "nhd": 0.09305010624703293,
  "normal_consistency": 0.9231825436346104,
  "bbox_error": 0.08226952465575642,
  "centroid_error": 0.02113026866759113,
  "surface_area_error": 0.0870939379823082,
  "volume_error": 0.2607791911690519,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.979390673359375,
      -0.598974033359375,
      -0.021005323359375
    ],
    "pitch": 0.01468255328125,
    "dimensions": [
      64,
      40,
      13
    ],
    "intersection": 4678,
    "union": 5422,
    "source_occupied": 5409,
    "cad_occupied": 4691
  },
  "grid128": {
    "origin": [
      -0.9830613116796876,
      -0.6026446716796876,
      -0.0246759616796875
    ],
    "pitch": 0.007341276640625,
    "dimensions": [
      128,
      80,
      26
    ],
    "intersection": 37231,
    "union": 43049,
    "source_occupied": 42930,
    "cad_occupied": 37350
  },
  "grid256": {
    "origin": [
      -0.9848966308398438,
      -0.6044799908398438,
      -0.02651128083984375
    ],
    "pitch": 0.0036706383203125,
    "dimensions": [
      256,
      160,
      51
    ],
    "intersection": 298204,
    "union": 345374,
    "source_occupied": 344282,
    "cad_occupied": 299296
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
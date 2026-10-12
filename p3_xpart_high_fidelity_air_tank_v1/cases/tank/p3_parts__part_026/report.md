{
  "case_id": "tank",
  "part_id": "p3_parts__part_026",
  "source_path": "tank/p3_parts/part_026.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x5 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 2361,
  "cad_brep_face_count": 98,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.2474944064731664,
  "iou128": 0.23400520359863328,
  "iou256": 0.2312898563795504,
  "cd": 0.013306322415261737,
  "ncd": 0.04597095788413143,
  "hausdorff": 0.10408131855930529,
  "nhd": 0.3595822919882687,
  "normal_consistency": 0.6642815673919276,
  "bbox_error": 0.19839233711989412,
  "centroid_error": 0.08805289109412652,
  "surface_area_error": 0.3342564323477769,
  "volume_error": 0.5626160860500213,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.53134507875,
      -0.66170413875,
      -0.38079152875
    ],
    "pitch": 0.0031646224999999995,
    "dimensions": [
      62,
      64,
      23
    ],
    "intersection": 8075,
    "union": 32627,
    "source_occupied": 30381,
    "cad_occupied": 10321
  },
  "grid128": {
    "origin": [
      -0.532136234375,
      -0.662495294375,
      -0.38158268437500004
    ],
    "pitch": 0.0015823112499999997,
    "dimensions": [
      123,
      128,
      45
    ],
    "intersection": 67185,
    "union": 287109,
    "source_occupied": 271630,
    "cad_occupied": 82664
  },
  "grid256": {
    "origin": [
      -0.5325318121875,
      -0.6628908721875,
      -0.38197826218750003
    ],
    "pitch": 0.0007911556249999999,
    "dimensions": [
      246,
      256,
      90
    ],
    "intersection": 525723,
    "union": 2273005,
    "source_occupied": 2137971,
    "cad_occupied": 660757
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
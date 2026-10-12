{
  "case_id": "tank",
  "part_id": "p3_parts__part_006",
  "source_path": "tank/p3_parts/part_006.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x9 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 4258,
  "cad_brep_face_count": 194,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.23066302357352556,
  "iou128": 0.22948084531679624,
  "iou256": 0.22764846316198326,
  "cd": 0.014936506307031052,
  "ncd": 0.05057631809350726,
  "hausdorff": 0.08456382251988727,
  "nhd": 0.2863405068798074,
  "normal_consistency": 0.6794836735142322,
  "bbox_error": 0.13105413795524254,
  "centroid_error": 0.042728101301135184,
  "surface_area_error": 0.4149235631396252,
  "volume_error": 0.8369520671554069,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.33422702859375,
      -0.66179523859375,
      0.24981459140625
    ],
    "pitch": 0.0029824228124999998,
    "dimensions": [
      64,
      64,
      41
    ],
    "intersection": 15871,
    "union": 68806,
    "source_occupied": 66770,
    "cad_occupied": 17907
  },
  "grid128": {
    "origin": [
      -0.334972634296875,
      -0.662540844296875,
      0.24906898570312502
    ],
    "pitch": 0.0014912114062499999,
    "dimensions": [
      128,
      128,
      82
    ],
    "intersection": 127777,
    "union": 556809,
    "source_occupied": 541261,
    "cad_occupied": 143325
  },
  "grid256": {
    "origin": [
      -0.3353454371484375,
      -0.6629136471484375,
      0.2486961828515625
    ],
    "pitch": 0.0007456057031249999,
    "dimensions": [
      255,
      256,
      164
    ],
    "intersection": 1019823,
    "union": 4479815,
    "source_occupied": 4353235,
    "cad_occupied": 1146403
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
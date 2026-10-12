{
  "case_id": "tank",
  "part_id": "p3_parts__part_037",
  "source_path": "tank/p3_parts/part_037.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x7 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 7408,
  "cad_brep_face_count": 146,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.2135306553911205,
  "iou128": 0.14844379348224093,
  "iou256": 0.12508694896095993,
  "cd": 0.008917870120682233,
  "ncd": 0.011726238485349514,
  "hausdorff": 0.09740672409897304,
  "nhd": 0.12808153307953965,
  "normal_consistency": 0.8371455220086894,
  "bbox_error": 0.1316171332696721,
  "centroid_error": 0.015340842802780669,
  "surface_area_error": 0.1522712717196729,
  "volume_error": 0.7604631197774291,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.071457643984375,
      -0.527350673984375,
      0.294737356015625
    ],
    "pitch": 0.01144455203125,
    "dimensions": [
      64,
      15,
      11
    ],
    "intersection": 303,
    "union": 1419,
    "source_occupied": 1410,
    "cad_occupied": 312
  },
  "grid128": {
    "origin": [
      -0.0743187819921875,
      -0.5302118119921875,
      0.2918762180078125
    ],
    "pitch": 0.005722276015625,
    "dimensions": [
      128,
      29,
      22
    ],
    "intersection": 2027,
    "union": 13655,
    "source_occupied": 13594,
    "cad_occupied": 2088
  },
  "grid256": {
    "origin": [
      -0.07574935099609376,
      -0.5316423809960937,
      0.29044564900390624
    ],
    "pitch": 0.0028611380078125,
    "dimensions": [
      256,
      57,
      44
    ],
    "intersection": 11509,
    "union": 92008,
    "source_occupied": 91681,
    "cad_occupied": 11836
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
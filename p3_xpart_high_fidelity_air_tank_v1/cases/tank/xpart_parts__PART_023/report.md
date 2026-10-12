{
  "case_id": "tank",
  "part_id": "xpart_parts__PART_023",
  "source_path": "tank/xpart_parts/PART_023.stl",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x21 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 33736,
  "cad_brep_face_count": 482,
  "quality_level": "C_NEAR_MISS",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.8872214456048022,
  "iou128": 0.8884031647323215,
  "iou256": 0.885182180328645,
  "cd": 0.005786487221334737,
  "ncd": 0.009941242435207342,
  "hausdorff": 0.1328840525457516,
  "nhd": 0.22829612018488704,
  "normal_consistency": 0.905259960114922,
  "bbox_error": 0.1491618796354803,
  "centroid_error": 0.022425036150625,
  "surface_area_error": 0.13334086180219587,
  "volume_error": 0.08493835042873235,
  "IOU_VALID": true,
  "grid64": {
    "origin": [
      0.7438474054215476,
      -0.43498187710065395,
      -0.19198148895520717
    ],
    "pitch": 0.006038617109879851,
    "dimensions": [
      43,
      58,
      64
    ],
    "intersection": 21579,
    "union": 24322,
    "source_occupied": 23989,
    "cad_occupied": 21912
  },
  "grid128": {
    "origin": [
      0.7423377511440776,
      -0.4364915313781239,
      -0.19349114323267713
    ],
    "pitch": 0.0030193085549399257,
    "dimensions": [
      86,
      116,
      128
    ],
    "intersection": 173148,
    "union": 194898,
    "source_occupied": 192013,
    "cad_occupied": 176033
  },
  "grid256": {
    "origin": [
      0.7415829240053426,
      -0.4372463585168589,
      -0.1942459703714121
    ],
    "pitch": 0.0015096542774699628,
    "dimensions": [
      172,
      232,
      256
    ],
    "intersection": 1383453,
    "union": 1562902,
    "source_occupied": 1539608,
    "cad_occupied": 1406747
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
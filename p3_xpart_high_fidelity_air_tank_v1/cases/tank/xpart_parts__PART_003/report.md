{
  "case_id": "tank",
  "part_id": "xpart_parts__PART_003",
  "source_path": "tank/xpart_parts/PART_003.stl",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x21 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 6096,
  "cad_brep_face_count": 482,
  "quality_level": "C_NEAR_MISS",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.8934426229508197,
  "iou128": 0.8945812807881773,
  "iou256": 0.8961818413995658,
  "cd": 0.0009873280161630782,
  "ncd": 0.0011707811081083219,
  "hausdorff": 0.012704626462530096,
  "nhd": 0.015065243165799604,
  "normal_consistency": 0.9656302859415529,
  "bbox_error": 0.014585844728565183,
  "centroid_error": 0.004350054162245572,
  "surface_area_error": 0.03643482740296562,
  "volume_error": 0.05901261365146568,
  "IOU_VALID": true,
  "grid64": {
    "origin": [
      -0.9204711969941854,
      -0.13726127706468105,
      -0.2523007448762655
    ],
    "pitch": 0.013123739510774612,
    "dimensions": [
      5,
      64,
      4
    ],
    "intersection": 109,
    "union": 122,
    "source_occupied": 120,
    "cad_occupied": 111
  },
  "grid128": {
    "origin": [
      -0.9237521318718791,
      -0.1405422119423747,
      -0.2555816797539592
    ],
    "pitch": 0.006561869755387306,
    "dimensions": [
      10,
      128,
      7
    ],
    "intersection": 908,
    "union": 1015,
    "source_occupied": 993,
    "cad_occupied": 930
  },
  "grid256": {
    "origin": [
      -0.9253925993107259,
      -0.14218267938122153,
      -0.257222147192806
    ],
    "pitch": 0.003280934877693653,
    "dimensions": [
      20,
      256,
      13
    ],
    "intersection": 7018,
    "union": 7831,
    "source_occupied": 7676,
    "cad_occupied": 7173
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
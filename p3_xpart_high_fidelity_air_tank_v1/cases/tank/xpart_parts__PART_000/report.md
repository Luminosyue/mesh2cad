{
  "case_id": "tank",
  "part_id": "xpart_parts__PART_000",
  "source_path": "tank/xpart_parts/PART_000.stl",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x21 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 5832,
  "cad_brep_face_count": 482,
  "quality_level": "C_NEAR_MISS",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.8252427184466019,
  "iou128": 0.8924731182795699,
  "iou256": 0.8824513969357538,
  "cd": 0.0010796093728779829,
  "ncd": 0.0012558537566141185,
  "hausdorff": 0.01291698054354173,
  "nhd": 0.015025655526197203,
  "normal_consistency": 0.9606305160268365,
  "bbox_error": 0.014960251963917948,
  "centroid_error": 0.009515909842514369,
  "surface_area_error": 0.04698135490768275,
  "volume_error": 0.09310030343810352,
  "IOU_VALID": true,
  "grid64": {
    "origin": [
      -0.9003090762998909,
      -0.15540339588187635,
      0.2307078188750893
    ],
    "pitch": 0.013399977702647448,
    "dimensions": [
      4,
      64,
      3
    ],
    "intersection": 85,
    "union": 103,
    "source_occupied": 102,
    "cad_occupied": 86
  },
  "grid128": {
    "origin": [
      -0.9036590707255527,
      -0.1587533903075382,
      0.22735782444942743
    ],
    "pitch": 0.006699988851323724,
    "dimensions": [
      7,
      128,
      6
    ],
    "intersection": 913,
    "union": 1023,
    "source_occupied": 1018,
    "cad_occupied": 918
  },
  "grid256": {
    "origin": [
      -0.9053340679383837,
      -0.16042838752036914,
      0.2256828272365965
    ],
    "pitch": 0.003349994425661862,
    "dimensions": [
      14,
      256,
      12
    ],
    "intersection": 6854,
    "union": 7767,
    "source_occupied": 7727,
    "cad_occupied": 6894
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
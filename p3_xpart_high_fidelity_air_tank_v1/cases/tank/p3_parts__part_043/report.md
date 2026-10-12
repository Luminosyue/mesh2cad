{
  "case_id": "tank",
  "part_id": "p3_parts__part_043",
  "source_path": "tank/p3_parts/part_043.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x3 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 7373,
  "cad_brep_face_count": 50,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.037053505261597744,
  "iou128": 0.03741993685160126,
  "iou256": 0.0381887342550623,
  "cd": 0.02836344819314891,
  "ncd": 0.0530545980759665,
  "hausdorff": 0.23440798165816568,
  "nhd": 0.4384664786870477,
  "normal_consistency": 0.7949146958113814,
  "bbox_error": 0.4027345840408074,
  "centroid_error": 0.1529054958255272,
  "surface_area_error": 0.8156910711323525,
  "volume_error": 0.9892114621682079,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      0.57693976078125,
      -0.5056060492187501,
      0.18836063078124998
    ],
    "pitch": 0.006103761562499999,
    "dimensions": [
      64,
      49,
      36
    ],
    "intersection": 250,
    "union": 6747,
    "source_occupied": 6387,
    "cad_occupied": 610
  },
  "grid128": {
    "origin": [
      0.575413820390625,
      -0.507131989609375,
      0.186834690390625
    ],
    "pitch": 0.0030518807812499995,
    "dimensions": [
      128,
      97,
      72
    ],
    "intersection": 2074,
    "union": 55425,
    "source_occupied": 52707,
    "cad_occupied": 4792
  },
  "grid256": {
    "origin": [
      0.5746508501953125,
      -0.5078949598046876,
      0.18607172019531248
    ],
    "pitch": 0.0015259403906249997,
    "dimensions": [
      256,
      193,
      143
    ],
    "intersection": 16766,
    "union": 439030,
    "source_occupied": 417411,
    "cad_occupied": 38385
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
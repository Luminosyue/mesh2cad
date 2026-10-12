{
  "case_id": "tank",
  "part_id": "p3_parts__part_002",
  "source_path": "tank/p3_parts/part_002.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x15 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 3550,
  "cad_brep_face_count": 338,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.7633995408723425,
  "iou128": 0.7600802208549463,
  "iou256": 0.7589750209871944,
  "cd": 0.007938884070592123,
  "ncd": 0.021244983695895444,
  "hausdorff": 0.06637906159434621,
  "nhd": 0.17763479964956122,
  "normal_consistency": 0.7921169040586313,
  "bbox_error": 0.08832535639081966,
  "centroid_error": 0.012094261979891123,
  "surface_area_error": 0.20607537679933804,
  "volume_error": 2.5654998742103445,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.95376894921875,
      -0.10333319921875,
      -0.09113464921875
    ],
    "pitch": 0.0047049815625,
    "dimensions": [
      42,
      23,
      64
    ],
    "intersection": 15297,
    "union": 20038,
    "source_occupied": 19196,
    "cad_occupied": 16139
  },
  "grid128": {
    "origin": [
      -0.954945194609375,
      -0.104509444609375,
      -0.092310894609375
    ],
    "pitch": 0.00235249078125,
    "dimensions": [
      84,
      45,
      128
    ],
    "intersection": 122794,
    "union": 161554,
    "source_occupied": 155127,
    "cad_occupied": 129221
  },
  "grid256": {
    "origin": [
      -0.9555333173046875,
      -0.1050975673046875,
      -0.0928990173046875
    ],
    "pitch": 0.001176245390625,
    "dimensions": [
      167,
      89,
      256
    ],
    "intersection": 981845,
    "union": 1293646,
    "source_occupied": 1241602,
    "cad_occupied": 1033889
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
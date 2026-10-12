{
  "case_id": "tank",
  "part_id": "p3_parts__part_030",
  "source_path": "tank/p3_parts/part_030.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x8 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 2391,
  "cad_brep_face_count": 170,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.05413206400648167,
  "iou128": 0.05754911724165221,
  "iou256": 0.05731775090824225,
  "cd": 0.014151511464290792,
  "ncd": 0.04788729914902722,
  "hausdorff": 0.0646100910619309,
  "nhd": 0.21863408488455988,
  "normal_consistency": 0.6963100725192894,
  "bbox_error": 0.21736750780449773,
  "centroid_error": 0.019747606015674046,
  "surface_area_error": 0.40986697847045006,
  "volume_error": 0.9230292530959116,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      0.243445083828125,
      -0.6698868761718749,
      0.26613815382812495
    ],
    "pitch": 0.0030759876562499993,
    "dimensions": [
      61,
      64,
      38
    ],
    "intersection": 2138,
    "union": 39496,
    "source_occupied": 38530,
    "cad_occupied": 3104
  },
  "grid128": {
    "origin": [
      0.24267608691406248,
      -0.6706558730859374,
      0.2653691569140625
    ],
    "pitch": 0.0015379938281249996,
    "dimensions": [
      122,
      128,
      76
    ],
    "intersection": 17452,
    "union": 303254,
    "source_occupied": 295972,
    "cad_occupied": 24734
  },
  "grid256": {
    "origin": [
      0.24229158845703125,
      -0.6710403715429687,
      0.26498465845703123
    ],
    "pitch": 0.0007689969140624998,
    "dimensions": [
      244,
      256,
      152
    ],
    "intersection": 141710,
    "union": 2472358,
    "source_occupied": 2413828,
    "cad_occupied": 200240
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
{
  "case_id": "tank",
  "part_id": "p3_parts__part_000",
  "source_path": "tank/p3_parts/part_000.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x20 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 1902,
  "cad_brep_face_count": 458,
  "quality_level": "C_NEAR_MISS",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.8695652173913043,
  "iou128": 0.8432250839865622,
  "iou256": 0.8487771739130435,
  "cd": 0.0019999670985986003,
  "ncd": 0.002344140445254734,
  "hausdorff": 0.055849855739563886,
  "nhd": 0.06546102973018457,
  "normal_consistency": 0.9379417464454993,
  "bbox_error": 0.06735004817631612,
  "centroid_error": 0.03822769969617476,
  "surface_area_error": 0.10706586316211691,
  "volume_error": 0.1531035743543351,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.911806629296875,
      -0.14549819929687502,
      0.224320850703125
    ],
    "pitch": 0.01325730140625,
    "dimensions": [
      6,
      64,
      4
    ],
    "intersection": 120,
    "union": 138,
    "source_occupied": 138,
    "cad_occupied": 120
  },
  "grid128": {
    "origin": [
      -0.9151209546484375,
      -0.1488125246484375,
      0.2210065253515625
    ],
    "pitch": 0.006628650703125,
    "dimensions": [
      12,
      128,
      8
    ],
    "intersection": 753,
    "union": 893,
    "source_occupied": 882,
    "cad_occupied": 764
  },
  "grid256": {
    "origin": [
      -0.9167781173242188,
      -0.15046968732421875,
      0.21934936267578126
    ],
    "pitch": 0.0033143253515625,
    "dimensions": [
      24,
      256,
      15
    ],
    "intersection": 6247,
    "union": 7360,
    "source_occupied": 7305,
    "cad_occupied": 6302
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
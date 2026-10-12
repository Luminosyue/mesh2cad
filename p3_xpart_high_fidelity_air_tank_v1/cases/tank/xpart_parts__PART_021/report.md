{
  "case_id": "tank",
  "part_id": "xpart_parts__PART_021",
  "source_path": "tank/xpart_parts/PART_021.stl",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x21 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 10140,
  "cad_brep_face_count": 482,
  "quality_level": "C_NEAR_MISS",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.8907557717209361,
  "iou128": 0.8936691508973167,
  "iou256": 0.8940230334596442,
  "cd": 0.0015880374805702982,
  "ncd": 0.005591104170658468,
  "hausdorff": 0.008010948433330207,
  "nhd": 0.02820465369648415,
  "normal_consistency": 0.9375649616937256,
  "bbox_error": 0.007093823983872768,
  "centroid_error": 0.0022395963000147417,
  "surface_area_error": 0.04856955285486229,
  "volume_error": 0.037832611153239964,
  "IOU_VALID": true,
  "grid64": {
    "origin": [
      0.05370667180977762,
      -0.6610392818693072,
      -0.38288899161852896
    ],
    "pitch": 0.003171942662447691,
    "dimensions": [
      59,
      64,
      22
    ],
    "intersection": 28204,
    "union": 31663,
    "source_occupied": 30511,
    "cad_occupied": 29356
  },
  "grid128": {
    "origin": [
      0.052913686144165695,
      -0.6618322675349191,
      -0.3836819772841409
    ],
    "pitch": 0.0015859713312238455,
    "dimensions": [
      118,
      128,
      44
    ],
    "intersection": 226874,
    "union": 253868,
    "source_occupied": 245033,
    "cad_occupied": 235709
  },
  "grid256": {
    "origin": [
      0.05251719331135973,
      -0.662228760367725,
      -0.38407847011694685
    ],
    "pitch": 0.0007929856656119227,
    "dimensions": [
      235,
      256,
      88
    ],
    "intersection": 1815025,
    "union": 2030177,
    "source_occupied": 1959783,
    "cad_occupied": 1885419
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
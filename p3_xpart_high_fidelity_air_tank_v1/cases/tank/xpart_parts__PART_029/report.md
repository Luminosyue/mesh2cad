{
  "case_id": "tank",
  "part_id": "xpart_parts__PART_029",
  "source_path": "tank/xpart_parts/PART_029.stl",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x21 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 24896,
  "cad_brep_face_count": 482,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.7555040556199305,
  "iou128": 0.7695442938518955,
  "iou256": 0.7659272609921391,
  "cd": 0.0044805199367177586,
  "ncd": 0.006182610330276977,
  "hausdorff": 0.06581717349843716,
  "nhd": 0.0908202491068846,
  "normal_consistency": 0.8315855755308987,
  "bbox_error": 0.012561564218837971,
  "centroid_error": 0.011092646513206652,
  "surface_area_error": 0.12893808987045477,
  "volume_error": 0.10478208248462734,
  "IOU_VALID": true,
  "grid64": {
    "origin": [
      -0.8520512316608801,
      -0.25175670126918703,
      0.25250926276203245
    ],
    "pitch": 0.010722690029069781,
    "dimensions": [
      64,
      16,
      16
    ],
    "intersection": 1956,
    "union": 2589,
    "source_occupied": 2413,
    "cad_occupied": 2132
  },
  "grid128": {
    "origin": [
      -0.8547319041681476,
      -0.2544373737764545,
      0.249828590254765
    ],
    "pitch": 0.005361345014534891,
    "dimensions": [
      128,
      31,
      31
    ],
    "intersection": 15671,
    "union": 20364,
    "source_occupied": 18964,
    "cad_occupied": 17071
  },
  "grid256": {
    "origin": [
      -0.8560722404217813,
      -0.2557777100300882,
      0.24848825400113128
    ],
    "pitch": 0.0026806725072674453,
    "dimensions": [
      256,
      61,
      62
    ],
    "intersection": 125789,
    "union": 164231,
    "source_occupied": 153150,
    "cad_occupied": 136870
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
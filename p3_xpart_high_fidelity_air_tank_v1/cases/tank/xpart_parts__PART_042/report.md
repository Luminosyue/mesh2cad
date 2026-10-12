{
  "case_id": "tank",
  "part_id": "xpart_parts__PART_042",
  "source_path": "tank/xpart_parts/PART_042.stl",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x21 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 862320,
  "cad_brep_face_count": 482,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.2879505664263646,
  "iou128": 0.2581307269395235,
  "iou256": 0.2487911461549423,
  "cd": 0.03349969630115253,
  "ncd": 0.015360747513464978,
  "hausdorff": 0.23376750001851354,
  "nhd": 0.10719033129010086,
  "normal_consistency": 0.7404418505901675,
  "bbox_error": 0.01651385340043731,
  "centroid_error": 0.02321952579846016,
  "surface_area_error": 0.7640270555066327,
  "volume_error": 0.7247900552203554,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.9633776065893471,
      -0.5797841665335,
      -0.402173709589988
    ],
    "pitch": 0.030189967714250088,
    "dimensions": [
      64,
      20,
      28
    ],
    "intersection": 1398,
    "union": 4855,
    "source_occupied": 2871,
    "cad_occupied": 3382
  },
  "grid128": {
    "origin": [
      -0.9709250985179096,
      -0.5873316584620625,
      -0.4097212015185505
    ],
    "pitch": 0.015094983857125044,
    "dimensions": [
      128,
      40,
      55
    ],
    "intersection": 10564,
    "union": 40925,
    "source_occupied": 24229,
    "cad_occupied": 27260
  },
  "grid256": {
    "origin": [
      -0.9746988444821909,
      -0.5911054044263437,
      -0.4134949474828318
    ],
    "pitch": 0.007547491928562522,
    "dimensions": [
      256,
      79,
      109
    ],
    "intersection": 78567,
    "union": 315795,
    "source_occupied": 174597,
    "cad_occupied": 219765
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
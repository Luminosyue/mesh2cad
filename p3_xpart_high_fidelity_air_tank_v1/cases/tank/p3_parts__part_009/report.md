{
  "case_id": "tank",
  "part_id": "p3_parts__part_009",
  "source_path": "tank/p3_parts/part_009.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x6 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 4337,
  "cad_brep_face_count": 122,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.3028678638434736,
  "iou128": 0.29955281510134507,
  "iou256": 0.2989039846733217,
  "cd": 0.014059023233452943,
  "ncd": 0.0457484474996411,
  "hausdorff": 0.08476576175407576,
  "nhd": 0.2758301154340574,
  "normal_consistency": 0.6737162421891332,
  "bbox_error": 0.1358467274396847,
  "centroid_error": 0.02211610845698062,
  "surface_area_error": 0.30891062410040127,
  "volume_error": 0.659268941608158,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.13764293015625,
      -0.66985215015625,
      0.24989609984375
    ],
    "pitch": 0.0031454396874999995,
    "dimensions": [
      62,
      64,
      42
    ],
    "intersection": 21470,
    "union": 70889,
    "source_occupied": 66221,
    "cad_occupied": 26138
  },
  "grid128": {
    "origin": [
      -0.138429290078125,
      -0.6706385100781249,
      0.24910973992187502
    ],
    "pitch": 0.0015727198437499998,
    "dimensions": [
      123,
      128,
      83
    ],
    "intersection": 171686,
    "union": 573141,
    "source_occupied": 535736,
    "cad_occupied": 209091
  },
  "grid256": {
    "origin": [
      -0.1388224700390625,
      -0.6710316900390625,
      0.2487165599609375
    ],
    "pitch": 0.0007863599218749999,
    "dimensions": [
      245,
      256,
      166
    ],
    "intersection": 1363594,
    "union": 4561980,
    "source_occupied": 4252129,
    "cad_occupied": 1673445
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
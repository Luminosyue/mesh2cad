{
  "case_id": "tank",
  "part_id": "xpart_parts__PART_007",
  "source_path": "tank/xpart_parts/PART_007.stl",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x21 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 22476,
  "cad_brep_face_count": 482,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.7340366933604509,
  "iou128": 0.7396399944647286,
  "iou256": 0.7411576427915062,
  "cd": 0.0022199175039564513,
  "ncd": 0.006693075549770434,
  "hausdorff": 0.015912550462116107,
  "nhd": 0.04797651365091757,
  "normal_consistency": 0.9535403670849534,
  "bbox_error": 0.0036800844731964045,
  "centroid_error": 0.008030084061339971,
  "surface_area_error": 0.04561127001531795,
  "volume_error": 0.08948264889148368,
  "IOU_VALID": true,
  "grid64": {
    "origin": [
      -0.9202917887596413,
      -0.42144928115885705,
      0.2433399484725669
    ],
    "pitch": 0.0038393589202314615,
    "dimensions": [
      42,
      64,
      41
    ],
    "intersection": 17324,
    "union": 23601,
    "source_occupied": 21744,
    "cad_occupied": 19181
  },
  "grid128": {
    "origin": [
      -0.9212516284896992,
      -0.4224091208889149,
      0.24238010874250904
    ],
    "pitch": 0.0019196794601157308,
    "dimensions": [
      84,
      128,
      81
    ],
    "intersection": 138968,
    "union": 187886,
    "source_occupied": 171515,
    "cad_occupied": 155339
  },
  "grid256": {
    "origin": [
      -0.9217315483547281,
      -0.42288904075394385,
      0.2419001888774801
    ],
    "pitch": 0.0009598397300578654,
    "dimensions": [
      168,
      256,
      161
    ],
    "intersection": 1101759,
    "union": 1486538,
    "source_occupied": 1354668,
    "cad_occupied": 1233629
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
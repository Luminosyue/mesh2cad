{
  "case_id": "airplane",
  "part_id": "PART_006__complete_part_006",
  "source_path": "airplane/xpart_parts/PART_006/complete_part_006.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x21 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 30492,
  "cad_brep_face_count": 482,
  "quality_level": "A_HIGH_CONFIDENCE",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.9615777815641506,
  "iou128": 0.963626296398833,
  "iou256": 0.9638327052902091,
  "cd": 0.0018815716966225594,
  "ncd": 0.0030094734035973664,
  "hausdorff": 0.012681914049426202,
  "nhd": 0.02028404397608876,
  "normal_consistency": 0.987861835899916,
  "bbox_error": 0.008057149439517207,
  "centroid_error": 0.02271823867217979,
  "surface_area_error": 0.16428778928820711,
  "volume_error": 0.020596392596927717,
  "IOU_VALID": true,
  "grid64": {
    "origin": [
      0.061226875078125,
      0.37966641507812504,
      -0.144592444921875
    ],
    "pitch": 0.0076600701562500005,
    "dimensions": [
      64,
      49,
      14
    ],
    "intersection": 11287,
    "union": 11738,
    "source_occupied": 11642,
    "cad_occupied": 11383
  },
  "grid128": {
    "origin": [
      0.0593118575390625,
      0.3777513975390625,
      -0.1465074624609375
    ],
    "pitch": 0.0038300350781250003,
    "dimensions": [
      128,
      98,
      27
    ],
    "intersection": 90498,
    "union": 93914,
    "source_occupied": 93164,
    "cad_occupied": 91248
  },
  "grid256": {
    "origin": [
      0.058354348769531245,
      0.3767938887695313,
      -0.14746497123046876
    ],
    "pitch": 0.0019150175390625001,
    "dimensions": [
      256,
      196,
      54
    ],
    "intersection": 723848,
    "union": 751010,
    "source_occupied": 745128,
    "cad_occupied": 729730
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
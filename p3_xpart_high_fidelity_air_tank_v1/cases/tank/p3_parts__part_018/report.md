{
  "case_id": "tank",
  "part_id": "p3_parts__part_018",
  "source_path": "tank/p3_parts/part_018.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x8 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 2637,
  "cad_brep_face_count": 170,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.18046962069098035,
  "iou128": 0.17147459364475032,
  "iou256": 0.1747882732739121,
  "cd": 0.017118856096428565,
  "ncd": 0.05948378224638708,
  "hausdorff": 0.10559829625473917,
  "nhd": 0.3669279083032211,
  "normal_consistency": 0.6699499902559853,
  "bbox_error": 0.17112372195941028,
  "centroid_error": 0.08339042649527843,
  "surface_area_error": 0.5908285900036837,
  "volume_error": 0.8906784434406674,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.334154906796875,
      -0.669861536796875,
      -0.37676597679687496
    ],
    "pitch": 0.003126666406249999,
    "dimensions": [
      62,
      64,
      24
    ],
    "intersection": 4696,
    "union": 26021,
    "source_occupied": 25516,
    "cad_occupied": 5201
  },
  "grid128": {
    "origin": [
      -0.3349365733984375,
      -0.6706432033984374,
      -0.3775476433984375
    ],
    "pitch": 0.0015633332031249995,
    "dimensions": [
      124,
      128,
      47
    ],
    "intersection": 37472,
    "union": 218528,
    "source_occupied": 214240,
    "cad_occupied": 41760
  },
  "grid256": {
    "origin": [
      -0.33532740669921873,
      -0.6710340366992187,
      -0.3779384766992187
    ],
    "pitch": 0.0007816666015624998,
    "dimensions": [
      248,
      256,
      94
    ],
    "intersection": 299897,
    "union": 1715773,
    "source_occupied": 1682072,
    "cad_occupied": 333598
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
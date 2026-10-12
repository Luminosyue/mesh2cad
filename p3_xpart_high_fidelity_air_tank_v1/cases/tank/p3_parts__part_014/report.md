{
  "case_id": "tank",
  "part_id": "p3_parts__part_014",
  "source_path": "tank/p3_parts/part_014.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x10 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 2856,
  "cad_brep_face_count": 218,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.1409507923269391,
  "iou128": 0.1362932226832642,
  "iou256": 0.13074259238210667,
  "cd": 0.012584810253127268,
  "ncd": 0.04138372065454789,
  "hausdorff": 0.0701184650154186,
  "nhd": 0.23057661661626544,
  "normal_consistency": 0.7321740511413947,
  "bbox_error": 0.13801422118838017,
  "centroid_error": 0.0607301833463691,
  "surface_area_error": 0.294171860561608,
  "volume_error": 0.8367110964244875,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.1487719584375,
      -0.6616333484375,
      -0.3825097384375
    ],
    "pitch": 0.0033062031249999997,
    "dimensions": [
      62,
      64,
      24
    ],
    "intersection": 3718,
    "union": 26378,
    "source_occupied": 25500,
    "cad_occupied": 4596
  },
  "grid128": {
    "origin": [
      -0.14959850921875,
      -0.6624598992187499,
      -0.38333628921875
    ],
    "pitch": 0.0016531015624999998,
    "dimensions": [
      124,
      128,
      48
    ],
    "intersection": 29562,
    "union": 216900,
    "source_occupied": 210161,
    "cad_occupied": 36301
  },
  "grid256": {
    "origin": [
      -0.150011784609375,
      -0.662873174609375,
      -0.383749564609375
    ],
    "pitch": 0.0008265507812499999,
    "dimensions": [
      247,
      256,
      96
    ],
    "intersection": 228904,
    "union": 1750799,
    "source_occupied": 1690667,
    "cad_occupied": 289036
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
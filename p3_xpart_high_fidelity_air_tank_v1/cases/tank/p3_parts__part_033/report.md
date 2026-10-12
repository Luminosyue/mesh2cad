{
  "case_id": "tank",
  "part_id": "p3_parts__part_033",
  "source_path": "tank/p3_parts/part_033.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x3 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 2061,
  "cad_brep_face_count": 50,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.38747736377105857,
  "iou128": 0.41851243682121797,
  "iou256": 0.4132310861754899,
  "cd": 0.012107247760635556,
  "ncd": 0.04133177803622374,
  "hausdorff": 0.07135513906177832,
  "nhd": 0.24359250159513401,
  "normal_consistency": 0.6697243916030584,
  "bbox_error": 0.17433991249079075,
  "centroid_error": 0.03019025570691599,
  "surface_area_error": 0.06148527160592902,
  "volume_error": 0.14965313955299434,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.7176922255468751,
      -0.661707735546875,
      -0.38079128554687497
    ],
    "pitch": 0.00315742890625,
    "dimensions": [
      62,
      64,
      27
    ],
    "intersection": 14122,
    "union": 36446,
    "source_occupied": 29072,
    "cad_occupied": 21496
  },
  "grid128": {
    "origin": [
      -0.7184815827734375,
      -0.6624970927734375,
      -0.3815806427734375
    ],
    "pitch": 0.001578714453125,
    "dimensions": [
      124,
      128,
      54
    ],
    "intersection": 124122,
    "union": 296579,
    "source_occupied": 245662,
    "cad_occupied": 175039
  },
  "grid256": {
    "origin": [
      -0.7188762613867188,
      -0.6628917713867187,
      -0.38197532138671875
    ],
    "pitch": 0.0007893572265625,
    "dimensions": [
      247,
      256,
      108
    ],
    "intersection": 975239,
    "union": 2360033,
    "source_occupied": 1938403,
    "cad_occupied": 1396869
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
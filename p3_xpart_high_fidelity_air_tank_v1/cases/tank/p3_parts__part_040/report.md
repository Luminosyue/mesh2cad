{
  "case_id": "tank",
  "part_id": "p3_parts__part_040",
  "source_path": "tank/p3_parts/part_040.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x8 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 10111,
  "cad_brep_face_count": 170,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.25258942135064216,
  "iou128": 0.23499651364542964,
  "iou256": 0.2413305407479664,
  "cd": 0.02067295454126719,
  "ncd": 0.031730558856432264,
  "hausdorff": 0.16056266863835686,
  "nhd": 0.24644485127682772,
  "normal_consistency": 0.7099200242056951,
  "bbox_error": 0.26349537793698097,
  "centroid_error": 0.08822244440984887,
  "surface_area_error": 0.5084547182177863,
  "volume_error": 0.8817772077048694,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.9109154707812499,
      -0.6892404907812499,
      -0.37785960078125
    ],
    "pitch": 0.0090284784375,
    "dimensions": [
      64,
      29,
      18
    ],
    "intersection": 1829,
    "union": 7241,
    "source_occupied": 7016,
    "cad_occupied": 2054
  },
  "grid128": {
    "origin": [
      -0.9131725903906249,
      -0.691497610390625,
      -0.380116720390625
    ],
    "pitch": 0.00451423921875,
    "dimensions": [
      128,
      58,
      35
    ],
    "intersection": 14492,
    "union": 61669,
    "source_occupied": 59793,
    "cad_occupied": 16368
  },
  "grid256": {
    "origin": [
      -0.9143011501953124,
      -0.6926261701953125,
      -0.3812452801953125
    ],
    "pitch": 0.002257119609375,
    "dimensions": [
      256,
      115,
      69
    ],
    "intersection": 116031,
    "union": 480797,
    "source_occupied": 466448,
    "cad_occupied": 130380
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
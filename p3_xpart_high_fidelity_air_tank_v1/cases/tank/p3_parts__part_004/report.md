{
  "case_id": "tank",
  "part_id": "p3_parts__part_004",
  "source_path": "tank/p3_parts/part_004.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x9 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 4308,
  "cad_brep_face_count": 194,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.5945327646374564,
  "iou128": 0.599616509747044,
  "iou256": 0.6011129977219021,
  "cd": 0.009990735251695405,
  "ncd": 0.02961919216941194,
  "hausdorff": 0.06819429664763633,
  "nhd": 0.20217330620601315,
  "normal_consistency": 0.7321014373862569,
  "bbox_error": 0.0836838336980754,
  "centroid_error": 0.03836370335451081,
  "surface_area_error": 0.1812322316653504,
  "volume_error": 0.12111047423179676,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      0.038999326015624995,
      -0.075082973984375,
      -0.313172303984375
    ],
    "pitch": 0.004484912031250001,
    "dimensions": [
      31,
      25,
      64
    ],
    "intersection": 15333,
    "union": 25790,
    "source_occupied": 25677,
    "cad_occupied": 15446
  },
  "grid128": {
    "origin": [
      0.0378780980078125,
      -0.0762042019921875,
      -0.3142935319921875
    ],
    "pitch": 0.0022424560156250003,
    "dimensions": [
      62,
      50,
      128
    ],
    "intersection": 121959,
    "union": 203395,
    "source_occupied": 202399,
    "cad_occupied": 122955
  },
  "grid256": {
    "origin": [
      0.03731748400390625,
      -0.07676481599609375,
      -0.3148541459960938
    ],
    "pitch": 0.0011212280078125002,
    "dimensions": [
      124,
      99,
      256
    ],
    "intersection": 976041,
    "union": 1623723,
    "source_occupied": 1615572,
    "cad_occupied": 984192
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
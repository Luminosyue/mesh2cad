{
  "case_id": "tank",
  "part_id": "xpart_parts__PART_037",
  "source_path": "tank/xpart_parts/PART_037.stl",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x21 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 25832,
  "cad_brep_face_count": 482,
  "quality_level": "C_NEAR_MISS",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.8387230514096186,
  "iou128": 0.8205083260297984,
  "iou256": 0.8225711671638016,
  "cd": 0.0031426303905698815,
  "ncd": 0.0042164519795040495,
  "hausdorff": 0.03926012499008751,
  "nhd": 0.05267511961532718,
  "normal_consistency": 0.8723374396612584,
  "bbox_error": 0.013270406794893984,
  "centroid_error": 0.004734029810749409,
  "surface_area_error": 0.11957202876370997,
  "volume_error": 0.05302953217641981,
  "IOU_VALID": true,
  "grid64": {
    "origin": [
      -0.06407696584938094,
      -0.5163305086898617,
      0.298990847368259
    ],
    "pitch": 0.011297646560706198,
    "dimensions": [
      64,
      12,
      11
    ],
    "intersection": 2023,
    "union": 2412,
    "source_occupied": 2291,
    "cad_occupied": 2144
  },
  "grid128": {
    "origin": [
      -0.06690137748955749,
      -0.5191549203300383,
      0.29616643572808243
    ],
    "pitch": 0.005648823280353099,
    "dimensions": [
      128,
      24,
      22
    ],
    "intersection": 14043,
    "union": 17115,
    "source_occupied": 16064,
    "cad_occupied": 15094
  },
  "grid256": {
    "origin": [
      -0.06831358330964576,
      -0.5205671261501266,
      0.29475422990799416
    ],
    "pitch": 0.0028244116401765496,
    "dimensions": [
      256,
      48,
      43
    ],
    "intersection": 110584,
    "union": 134437,
    "source_occupied": 125814,
    "cad_occupied": 119207
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
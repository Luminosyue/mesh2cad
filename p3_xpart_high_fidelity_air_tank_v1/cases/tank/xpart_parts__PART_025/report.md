{
  "case_id": "tank",
  "part_id": "xpart_parts__PART_025",
  "source_path": "tank/xpart_parts/PART_025.stl",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x21 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 52640,
  "cad_brep_face_count": 482,
  "quality_level": "C_NEAR_MISS",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.889384342538637,
  "iou128": 0.8933972284038033,
  "iou256": 0.8925858839511763,
  "cd": 0.004487038737619518,
  "ncd": 0.0062367914236976674,
  "hausdorff": 0.049532334879132195,
  "nhd": 0.06884782134370061,
  "normal_consistency": 0.8581670508290249,
  "bbox_error": 0.011181980957993451,
  "centroid_error": 0.0015807354003119552,
  "surface_area_error": 0.12053033453142951,
  "volume_error": 0.03443911782904128,
  "IOU_VALID": true,
  "grid64": {
    "origin": [
      -0.011494926890009083,
      -0.06395178452658001,
      0.0591800717957085
    ],
    "pitch": 0.009115767170442268,
    "dimensions": [
      64,
      24,
      40
    ],
    "intersection": 17552,
    "union": 19735,
    "source_occupied": 19045,
    "cad_occupied": 18242
  },
  "grid128": {
    "origin": [
      -0.01377386868261965,
      -0.06623072631919058,
      0.05690113000309793
    ],
    "pitch": 0.004557883585221134,
    "dimensions": [
      128,
      48,
      80
    ],
    "intersection": 141314,
    "union": 158176,
    "source_occupied": 152298,
    "cad_occupied": 147192
  },
  "grid256": {
    "origin": [
      -0.014913339578924933,
      -0.06737019721549586,
      0.05576165910679265
    ],
    "pitch": 0.002278941792610567,
    "dimensions": [
      256,
      95,
      159
    ],
    "intersection": 1127477,
    "union": 1263158,
    "source_occupied": 1216312,
    "cad_occupied": 1174323
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
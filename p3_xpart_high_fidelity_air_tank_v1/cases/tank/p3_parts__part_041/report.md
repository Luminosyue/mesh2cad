{
  "case_id": "tank",
  "part_id": "p3_parts__part_041",
  "source_path": "tank/p3_parts/part_041.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x11 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 10803,
  "cad_brep_face_count": 242,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.21904162734612562,
  "iou128": 0.22734084401509272,
  "iou256": 0.22489399033739876,
  "cd": 0.01587779301916753,
  "ncd": 0.020896094946336832,
  "hausdorff": 0.20396916151419384,
  "nhd": 0.26843522648141754,
  "normal_consistency": 0.876266736002564,
  "bbox_error": 0.09765799969333476,
  "centroid_error": 0.05368685352428059,
  "surface_area_error": 0.3230582456359177,
  "volume_error": 0.992783898722871,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      -0.995612921875,
      -0.569377601875,
      -0.292558761875
    ],
    "pitch": 0.00877415625,
    "dimensions": [
      12,
      58,
      64
    ],
    "intersection": 2089,
    "union": 9537,
    "source_occupied": 9300,
    "cad_occupied": 2326
  },
  "grid128": {
    "origin": [
      -0.9978064609375,
      -0.5715711409375,
      -0.2947523009375
    ],
    "pitch": 0.004387078125,
    "dimensions": [
      24,
      115,
      128
    ],
    "intersection": 16991,
    "union": 74738,
    "source_occupied": 73037,
    "cad_occupied": 18692
  },
  "grid256": {
    "origin": [
      -0.99890323046875,
      -0.57266791046875,
      -0.29584907046875003
    ],
    "pitch": 0.0021935390625,
    "dimensions": [
      47,
      229,
      256
    ],
    "intersection": 136250,
    "union": 605841,
    "source_occupied": 592171,
    "cad_occupied": 149920
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
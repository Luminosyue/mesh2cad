{
  "case_id": "airplane",
  "part_id": "p3_parts__part_000",
  "source_path": "airplane/p3_parts/part_000.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x8 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 10421,
  "cad_brep_face_count": 170,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.3307729236677868,
  "iou128": 0.33006319590731265,
  "iou256": 0.3303480117908921,
  "cd": 0.06287950172345579,
  "ncd": 0.07126012591945809,
  "hausdorff": 0.5431225037453041,
  "nhd": 0.6155102528769633,
  "normal_consistency": 0.6460072336068594,
  "bbox_error": 0.5934879163109829,
  "centroid_error": 0.2103703902271059,
  "surface_area_error": 0.6127834914161249,
  "volume_error": 0.674146168564444,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      0.018569167578125,
      0.18154880757812503,
      -0.087964472421875
    ],
    "pitch": 0.01288899515625,
    "dimensions": [
      10,
      64,
      23
    ],
    "intersection": 689,
    "union": 2083,
    "source_occupied": 2080,
    "cad_occupied": 692
  },
  "grid128": {
    "origin": [
      0.0153469187890625,
      0.1783265587890625,
      -0.09118672121093749
    ],
    "pitch": 0.006444497578125,
    "dimensions": [
      20,
      128,
      45
    ],
    "intersection": 5484,
    "union": 16615,
    "source_occupied": 16605,
    "cad_occupied": 5494
  },
  "grid256": {
    "origin": [
      0.01373579439453125,
      0.17671543439453127,
      -0.09279784560546875
    ],
    "pitch": 0.0032222487890625,
    "dimensions": [
      40,
      256,
      89
    ],
    "intersection": 43931,
    "union": 132984,
    "source_occupied": 132911,
    "cad_occupied": 44004
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
{
  "case_id": "tank",
  "part_id": "xpart_parts__PART_041",
  "source_path": "tank/xpart_parts/PART_041.stl",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x21 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 55948,
  "cad_brep_face_count": 482,
  "quality_level": "B_USABLE",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.9098683401008982,
  "iou128": 0.9149961703016565,
  "iou256": 0.9150534597460783,
  "cd": 0.0032445922202563315,
  "ncd": 0.004307059274499486,
  "hausdorff": 0.04753717728051392,
  "nhd": 0.06310359712117793,
  "normal_consistency": 0.9329931255774867,
  "bbox_error": 0.04458203408864694,
  "centroid_error": 0.0019874893619322488,
  "surface_area_error": 0.06363758254637612,
  "volume_error": 0.048063600579787334,
  "IOU_VALID": true,
  "grid64": {
    "origin": [
      -0.9945901667233557,
      -0.5623133813496679,
      -0.29022580734454095
    ],
    "pitch": 0.008708470035344362,
    "dimensions": [
      15,
      57,
      64
    ],
    "intersection": 14789,
    "union": 16254,
    "source_occupied": 15944,
    "cad_occupied": 15099
  },
  "grid128": {
    "origin": [
      -0.9967672842321917,
      -0.564490498858504,
      -0.29240292485337704
    ],
    "pitch": 0.004354235017672181,
    "dimensions": [
      30,
      113,
      128
    ],
    "intersection": 118266,
    "union": 129253,
    "source_occupied": 126935,
    "cad_occupied": 120584
  },
  "grid256": {
    "origin": [
      -0.9978558429866098,
      -0.565579057612922,
      -0.2934914836077951
    ],
    "pitch": 0.0021771175088360906,
    "dimensions": [
      60,
      226,
      256
    ],
    "intersection": 946039,
    "union": 1033862,
    "source_occupied": 1014158,
    "cad_occupied": 965743
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
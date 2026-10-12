{
  "case_id": "tank",
  "part_id": "xpart_parts__PART_044",
  "source_path": "tank/xpart_parts/PART_044.stl",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x21 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 33916,
  "cad_brep_face_count": 482,
  "quality_level": "C_NEAR_MISS",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.8770685579196218,
  "iou128": 0.8780395136778115,
  "iou256": 0.8791720768220701,
  "cd": 0.0024500983460952978,
  "ncd": 0.0037191408070877765,
  "hausdorff": 0.03065547173630253,
  "nhd": 0.04653364877238857,
  "normal_consistency": 0.9486047486714058,
  "bbox_error": 0.03796936814814732,
  "centroid_error": 0.0036387770612856503,
  "surface_area_error": 0.050687993766143635,
  "volume_error": 0.051006976433448516,
  "IOU_VALID": true,
  "grid64": {
    "origin": [
      0.5220759941730648,
      -0.11278704716823995,
      -0.21472133859060705
    ],
    "pitch": 0.007626381237059832,
    "dimensions": [
      58,
      11,
      64
    ],
    "intersection": 7420,
    "union": 8460,
    "source_occupied": 8134,
    "cad_occupied": 7746
  },
  "grid128": {
    "origin": [
      0.5201693988637999,
      -0.11469364247750491,
      -0.216627933899872
    ],
    "pitch": 0.003813190618529916,
    "dimensions": [
      115,
      22,
      128
    ],
    "intersection": 60086,
    "union": 68432,
    "source_occupied": 66043,
    "cad_occupied": 62475
  },
  "grid256": {
    "origin": [
      0.5192161012091674,
      -0.11564694013213739,
      -0.21758123155450448
    ],
    "pitch": 0.001906595309264958,
    "dimensions": [
      229,
      43,
      256
    ],
    "intersection": 480064,
    "union": 546041,
    "source_occupied": 526512,
    "cad_occupied": 499593
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
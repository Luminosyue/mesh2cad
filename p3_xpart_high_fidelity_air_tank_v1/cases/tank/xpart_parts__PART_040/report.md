{
  "case_id": "tank",
  "part_id": "xpart_parts__PART_040",
  "source_path": "tank/xpart_parts/PART_040.stl",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x21 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 32972,
  "cad_brep_face_count": 482,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.6280193236714976,
  "iou128": 0.6317054990502297,
  "iou256": 0.6301754048092635,
  "cd": 0.005650901580389843,
  "ncd": 0.00857193267626712,
  "hausdorff": 0.04652162159106722,
  "nhd": 0.07056930696745423,
  "normal_consistency": 0.7826937509101477,
  "bbox_error": 0.0073307936786092326,
  "centroid_error": 0.005806702948315489,
  "surface_area_error": 0.1462448931930671,
  "volume_error": 0.17334282017020386,
  "IOU_VALID": true,
  "grid64": {
    "origin": [
      -0.9094981413800269,
      -0.6886190038640052,
      -0.3790654104668647
    ],
    "pitch": 0.009263066109269857,
    "dimensions": [
      64,
      27,
      16
    ],
    "intersection": 3250,
    "union": 5175,
    "source_occupied": 4622,
    "cad_occupied": 3803
  },
  "grid128": {
    "origin": [
      -0.9118139079073444,
      -0.6909347703913227,
      -0.38138117699418217
    ],
    "pitch": 0.004631533054634929,
    "dimensions": [
      128,
      54,
      32
    ],
    "intersection": 26272,
    "union": 41589,
    "source_occupied": 37155,
    "cad_occupied": 30706
  },
  "grid256": {
    "origin": [
      -0.9129717911710031,
      -0.6920926536549814,
      -0.3825390602578409
    ],
    "pitch": 0.0023157665273174644,
    "dimensions": [
      256,
      108,
      64
    ],
    "intersection": 209418,
    "union": 332317,
    "source_occupied": 296749,
    "cad_occupied": 244986
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
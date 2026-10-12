{
  "case_id": "tank",
  "part_id": "xpart_parts__PART_033",
  "source_path": "tank/xpart_parts/PART_033.stl",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x21 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 10222,
  "cad_brep_face_count": 482,
  "quality_level": "C_NEAR_MISS",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.852267224020595,
  "iou128": 0.8501241914783575,
  "iou256": 0.849619671840376,
  "cd": 0.0020239129583130653,
  "ncd": 0.007298048839173637,
  "hausdorff": 0.020932439449780325,
  "nhd": 0.07548050166884272,
  "normal_consistency": 0.8609346038479034,
  "bbox_error": 0.001839131077884412,
  "centroid_error": 0.0024552348284035126,
  "surface_area_error": 0.01637551751857392,
  "volume_error": 0.09934994999390795,
  "IOU_VALID": true,
  "grid64": {
    "origin": [
      -0.7177887435536832,
      -0.6566937442403287,
      -0.3685329135041684
    ],
    "pitch": 0.0030716904439032078,
    "dimensions": [
      61,
      64,
      19
    ],
    "intersection": 33437,
    "union": 39233,
    "source_occupied": 38191,
    "cad_occupied": 34479
  },
  "grid128": {
    "origin": [
      -0.718556666164659,
      -0.6574616668513045,
      -0.3693008361151442
    ],
    "pitch": 0.0015358452219516039,
    "dimensions": [
      122,
      128,
      37
    ],
    "intersection": 266281,
    "union": 313226,
    "source_occupied": 304979,
    "cad_occupied": 274528
  },
  "grid256": {
    "origin": [
      -0.7189406274701469,
      -0.6578456281567924,
      -0.3696847974206321
    ],
    "pitch": 0.0007679226109758019,
    "dimensions": [
      244,
      256,
      74
    ],
    "intersection": 2126796,
    "union": 2503233,
    "source_occupied": 2435951,
    "cad_occupied": 2194078
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
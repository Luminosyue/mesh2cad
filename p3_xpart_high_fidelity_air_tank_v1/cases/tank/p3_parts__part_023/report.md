{
  "case_id": "tank",
  "part_id": "p3_parts__part_023",
  "source_path": "tank/p3_parts/part_023.obj",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x11 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 7921,
  "cad_brep_face_count": 242,
  "quality_level": "D_REJECT",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.15487963437216815,
  "iou128": 0.15516384577158057,
  "iou256": 0.15516052442682995,
  "cd": 0.022156927502763143,
  "ncd": 0.035603312731786595,
  "hausdorff": 0.20689176535352777,
  "nhd": 0.3324482703025705,
  "normal_consistency": 0.759025361427927,
  "bbox_error": 0.12334866792172673,
  "centroid_error": 0.04895900882274005,
  "surface_area_error": 0.16698649063546062,
  "volume_error": 0.9838115594096593,
  "IOU_VALID": false,
  "grid64": {
    "origin": [
      0.734572070390625,
      -0.44016352960937505,
      -0.236589769609375
    ],
    "pitch": 0.00677518078125,
    "dimensions": [
      40,
      53,
      64
    ],
    "intersection": 3931,
    "union": 25381,
    "source_occupied": 25242,
    "cad_occupied": 4070
  },
  "grid128": {
    "origin": [
      0.7328782751953126,
      -0.44185732480468753,
      -0.23828356480468751
    ],
    "pitch": 0.003387590390625,
    "dimensions": [
      80,
      106,
      128
    ],
    "intersection": 31848,
    "union": 205254,
    "source_occupied": 204256,
    "cad_occupied": 32846
  },
  "grid256": {
    "origin": [
      0.7320313775976562,
      -0.44270422240234375,
      -0.23913046240234376
    ],
    "pitch": 0.0016937951953125,
    "dimensions": [
      159,
      211,
      256
    ],
    "intersection": 252907,
    "union": 1629970,
    "source_occupied": 1621028,
    "cad_occupied": 261849
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
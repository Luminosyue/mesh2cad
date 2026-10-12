{
  "case_id": "tank",
  "part_id": "xpart_parts__PART_027",
  "source_path": "tank/xpart_parts/PART_027.stl",
  "geometry_family": "MULTI_SECTION_LOFT",
  "feature_sequence": "SKETCH_SECTION x21 -> LOFT",
  "cad_program_exec": "PASS",
  "brep_valid": true,
  "step_reload": true,
  "mesh_import_used": false,
  "faceted_brep": false,
  "source_triangle_count": 7836,
  "cad_brep_face_count": 482,
  "quality_level": "C_NEAR_MISS",
  "valid_training_pair": false,
  "failure_reason": "IOU_TOO_LOW",
  "source_free_reexecution": true,
  "iou64": 0.7997658079625293,
  "iou128": 0.804845422116528,
  "iou256": 0.8070338494711601,
  "cd": 0.0016260012270612714,
  "ncd": 0.0028170445697967617,
  "hausdorff": 0.011899427207021663,
  "nhd": 0.020615738930170602,
  "normal_consistency": 0.9316738209218695,
  "bbox_error": 0.008292078051896678,
  "centroid_error": 0.00577914178137093,
  "surface_area_error": 0.022285196063740766,
  "volume_error": 0.04897905202358787,
  "IOU_VALID": true,
  "grid64": {
    "origin": [
      0.42201442434452474,
      -0.2668312101159245,
      0.18455914570949972
    ],
    "pitch": 0.007890659850090742,
    "dimensions": [
      64,
      29,
      22
    ],
    "intersection": 683,
    "union": 854,
    "source_occupied": 788,
    "cad_occupied": 749
  },
  "grid128": {
    "origin": [
      0.42004175938200206,
      -0.26880387507844716,
      0.18258648074697703
    ],
    "pitch": 0.003945329925045371,
    "dimensions": [
      128,
      57,
      43
    ],
    "intersection": 5415,
    "union": 6728,
    "source_occupied": 6235,
    "cad_occupied": 5908
  },
  "grid256": {
    "origin": [
      0.4190554269007407,
      -0.2697902075597085,
      0.1816001482657157
    ],
    "pitch": 0.0019726649625226855,
    "dimensions": [
      256,
      114,
      86
    ],
    "intersection": 43416,
    "union": 53797,
    "source_occupied": 49825,
    "cad_occupied": 47388
  },
  "surface_sample_count": 32768,
  "distance_protocol": "bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal",
  "coordinate_protocol": "original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment"
}
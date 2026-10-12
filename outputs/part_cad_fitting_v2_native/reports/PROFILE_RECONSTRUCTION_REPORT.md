# Profile reconstruction

V1 selected programs using polyline: 149. Final programs using polyline: 141.

[
  {
    "upgrade": "POLYLINE_TO_ARC",
    "selected_part_n": 0,
    "mean_delta_NCD": null,
    "mean_delta_IoU": null,
    "mean_delta_NCD_vs_preserved_baseline": null,
    "mean_delta_IoU_vs_preserved_baseline": null,
    "strict_rescue_n": 0,
    "additional_strict_vs_baseline_n": 0,
    "case_ids": [],
    "counts_can_overlap_for_mixed_profiles": true,
    "attribution": "curve reconstruction plus local optimization, not a profile-only causal ablation",
    "controlled_profile_strict_rescue_n": 0
  },
  {
    "upgrade": "POLYLINE_TO_CIRCLE",
    "selected_part_n": 1,
    "mean_delta_NCD": -0.0050203239998017485,
    "mean_delta_IoU": 0.18874684988175616,
    "mean_delta_NCD_vs_preserved_baseline": 0.002058477024645528,
    "mean_delta_IoU_vs_preserved_baseline": -0.055337878507495164,
    "strict_rescue_n": 0,
    "additional_strict_vs_baseline_n": 0,
    "case_ids": [
      "object_00006/part_000"
    ],
    "counts_can_overlap_for_mixed_profiles": true,
    "attribution": "curve reconstruction plus local optimization, not a profile-only causal ablation",
    "controlled_profile_strict_rescue_n": 0
  },
  {
    "upgrade": "POLYLINE_TO_ELLIPSE",
    "selected_part_n": 0,
    "mean_delta_NCD": null,
    "mean_delta_IoU": null,
    "mean_delta_NCD_vs_preserved_baseline": null,
    "mean_delta_IoU_vs_preserved_baseline": null,
    "strict_rescue_n": 0,
    "additional_strict_vs_baseline_n": 0,
    "case_ids": [],
    "counts_can_overlap_for_mixed_profiles": true,
    "attribution": "curve reconstruction plus local optimization, not a profile-only causal ablation",
    "controlled_profile_strict_rescue_n": 0
  },
  {
    "upgrade": "POLYLINE_TO_BSPLINE",
    "selected_part_n": 0,
    "mean_delta_NCD": null,
    "mean_delta_IoU": null,
    "mean_delta_NCD_vs_preserved_baseline": null,
    "mean_delta_IoU_vs_preserved_baseline": null,
    "strict_rescue_n": 0,
    "additional_strict_vs_baseline_n": 0,
    "case_ids": [],
    "counts_can_overlap_for_mixed_profiles": true,
    "attribution": "curve reconstruction plus local optimization, not a profile-only causal ablation",
    "controlled_profile_strict_rescue_n": 0
  },
  {
    "upgrade": "POLYLINE_TO_COMPOSITE",
    "selected_part_n": 23,
    "mean_delta_NCD": -0.007853175560242228,
    "mean_delta_IoU": 0.15478096577434092,
    "mean_delta_NCD_vs_preserved_baseline": -0.0010071125687391418,
    "mean_delta_IoU_vs_preserved_baseline": 0.036451030915504466,
    "strict_rescue_n": 5,
    "additional_strict_vs_baseline_n": 2,
    "case_ids": [
      "object_00001/part_003",
      "object_00001/part_005",
      "object_00002/part_009",
      "object_00002/part_013",
      "object_00003/part_005",
      "object_00004/part_000",
      "object_00010/part_002",
      "object_00010/part_003",
      "object_00011/part_018",
      "object_00013/part_001",
      "object_00013/part_005",
      "object_00013/part_010",
      "object_00014/part_000",
      "object_00014/part_003",
      "object_00014/part_004",
      "object_00015/part_000",
      "object_00015/part_001",
      "object_00015/part_002",
      "object_00015/part_003",
      "object_00015/part_004",
      "object_00015/part_007",
      "object_00018/part_000",
      "object_00018/part_001"
    ],
    "counts_can_overlap_for_mixed_profiles": true,
    "attribution": "curve reconstruction plus local optimization, not a profile-only causal ablation",
    "controlled_profile_strict_rescue_n": 1
  }
]

Counts describe selected new profile reconstructions, not every attempted curve or inherited historical improvement. Mixed profiles can belong to multiple rows. Each row includes mean V1 paired metric changes and a separate additional-strict count against the preserved baseline. New fitting attribution and full candidate evidence are available in all_candidates.csv and optimization logs.

Circle/ellipse/arc parameters are solved from numeric contours. Curves are not guessed by the assistant. Composite fitting logs angular coverage/residuals and tangent discontinuities; real corners are retained. Multi-section extraction preserves observed inner loops as cuts. Existing protrusions/boolean structures are retained in Near candidates. This bounded implementation does not claim reliable automatic blind-hole, fillet/chamfer or arbitrary CSG discovery; unconfirmed features remain diagnosis items. Unsupported open-section/freeform parts keep explicitly rejected baselines, rather than being relabeled successful.

Parameter fitting uses local coordinate descent over radial scale, extrusion depth when valid, center and small orientation changes. Revolved curves use similarity transforms to preserve circles/arcs. Proxy objective prioritizes NCD and IoU48 and includes centroid/bbox penalties. Final acceptance always uses unchanged IoU128, 20000-point NCD and original seeds after native code -> STEP -> reload. Display tessellation never enters evaluation.

Controlled profile contribution: 1 additional Strict cases have a selected profile reconstruction while both preserved baseline and same-round parameter-only refinement remain non-Strict. See profile_parameter_control_comparison.csv. This is an empirical matched-optimizer comparison, not a claim that all paired V1 improvement is caused by profile type alone.

## Visual review

The two additional Near-to-Strict cases were inspected with source/V1/new/overlay under identical cameras. Robot part_009 improves rounded profile agreement; kitchen-rack part_003 improves a long section profile. Fine end-boundary irregularities remain approximated. Numerical Strict means the fixed metrics passed; it does not claim exact recovery of every surface detail. Ten original Near-to-Strict views include inherited rescues and are labeled accordingly.

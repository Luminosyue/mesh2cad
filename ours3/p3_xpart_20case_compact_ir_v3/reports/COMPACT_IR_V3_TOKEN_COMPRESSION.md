# Compact IR V3 token compression

{
  "experiment": "P3_XPART_20CASE_COMPACT_IR_V3_AND_DEMO_OVERFIT",
  "v1_case_manifest_sha256": "8e9886566f1080c7cb11a4dda259a1c4b397d6e2e42928679d1269e2ee8de481",
  "case_n": 20,
  "v3_parse_pass": 20,
  "v3_q_exact_pass": 20,
  "v3_cad_pass": 20,
  "v3_step_readback_pass": 20,
  "geometry_equivalence_pass": 20,
  "v1_max_target": 30953,
  "v3_max_target": 12029,
  "v1_max_fullseq": 30992,
  "v3_max_fullseq": 12054,
  "v3_context": {
    "min_full_sequence": 166,
    "median_full_sequence": 4139.5,
    "p90_full_sequence": 11927.0,
    "p95_full_sequence": 12053.05,
    "max_full_sequence": 12054,
    "candidates": [
      8192,
      16384,
      24576,
      32768
    ],
    "recommended_context": 16384
  },
  "demo5_ids": [
    "case_018",
    "case_009",
    "case_014",
    "case_010",
    "case_005"
  ],
  "demo5_context": 8192,
  "v3_memory_gate": "PENDING_PROBE",
  "demo5_overfit": "PENDING",
  "twenty_case_overfit": "PENDING"
}

case_000: V1=29661 V3=10737 reduction=63.801% full=10762
case_001: V1=30464 V3=11540 reduction=62.119% full=11565
case_002: V1=30952 V3=12028 reduction=61.14% full=12053
case_003: V1=30187 V3=11263 reduction=62.689% full=11288
case_004: V1=6971 V3=2829 reduction=59.418% full=2854
case_005: V1=15434 V3=6196 reduction=59.855% full=6221
case_006: V1=1251 V3=548 reduction=56.195% full=573
case_007: V1=30535 V3=11611 reduction=61.975% full=11636
case_008: V1=6220 V3=2678 reduction=56.945% full=2703
case_009: V1=896 V3=394 reduction=56.027% full=419
case_010: V1=9270 V3=3744 reduction=59.612% full=3769
case_011: V1=6236 V3=2694 reduction=56.799% full=2719
case_012: V1=15412 V3=6174 reduction=59.94% full=6199
case_013: V1=30953 V3=12029 reduction=61.138% full=12054
case_014: V1=11278 V3=4485 reduction=60.232% full=4510
case_015: V1=30812 V3=11888 reduction=61.418% full=11913
case_016: V1=2513 V3=1064 reduction=57.66% full=1089
case_017: V1=3046 V3=1305 reduction=57.157% full=1330
case_018: V1=299 V3=141 reduction=52.843% full=166
case_019: V1=1233 V3=538 reduction=56.367% full=563

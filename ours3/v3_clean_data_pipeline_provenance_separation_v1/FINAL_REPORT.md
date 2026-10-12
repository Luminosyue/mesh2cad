# V3 Clean Data Pipeline Provenance Separation V1

{
  "audit": "V3_CLEAN_DATA_PIPELINE_PROVENANCE_SEPARATION_V1",
  "generated_utc": "2026-09-06T08:05:07.859203Z",
  "read_only": true,
  "training": false,
  "decode": false,
  "dora": false,
  "counts": {
    "v3_800": 800,
    "clean_688": 688,
    "removed_112": 112,
    "deepcad_clean": 594,
    "fusion360_clean": 94
  },
  "removal_reason_counts": {
    "step_failure": 70,
    "context_overflow": 59
  },
  "removal_manifest_top_level_counts": {
    "context_overflow": 59,
    "step_failure": 70,
    "overlap": 17
  },
  "all_clean_assets_exist": true,
  "independent_dev_available": false,
  "fusion360_yield160": 0.5875,
  "gate": "V3_CLEAN_PIPELINE_RECOVERED_BUT_10K_YIELD_RISK",
  "conclusions": [
    "Generic data pipeline is separated from V3 model-specific K=8 adapter.",
    "Clean 688 is a strict subset of frozen 800; removed 112 stay excluded.",
    "No independent dev is available from current split.",
    "Observed Fusion360 yield is insufficient to approve clean 10k expansion."
  ]
}

See the JSONL freeze files, asset matrix, removal audit, Fusion360 yield audit, and CLEAN10K_FEASIBILITY.json for details.

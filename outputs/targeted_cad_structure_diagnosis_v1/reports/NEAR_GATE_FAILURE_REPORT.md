# Near gate failures

76 original current Near cases, metadata-only gate decomposition.

Exclusive patterns: {'MULTI_GATE_FAIL': 29, 'IOU_NCD_CENTROID_FAIL': 8, 'IOU_NCD_FAIL': 10, 'IOU_ONLY_FAIL': 16, 'NCD_CENTROID_FAIL': 1, 'CENTROID_ONLY_FAIL': 2, 'BBOX_ONLY_FAIL': 8, 'IOU_CENTROID_FAIL': 1, 'NCD_ONLY_FAIL': 1}

Per-gate failures (overlap): {'IOU': 61, 'NCD': 35, 'CENTROID': 18, 'BBOX': 37}. Most frequent: IOU.

Selected 20 Near: half closest normalized gate distance, half deterministic uncovered family/failure/object/major-minor coverage. No centroid/NCD-only case is fabricated when a stratum is small. Frozen manifest records selection. Near pilot significant improvement: 1/20.

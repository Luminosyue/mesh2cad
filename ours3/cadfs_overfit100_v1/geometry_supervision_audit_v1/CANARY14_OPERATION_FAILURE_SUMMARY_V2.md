# Corrected Canary14 semantic audit

```json
{
  "FAILED_CASES": 14,
  "PREFIX_GEOMETRY_AUDIT_AVAILABLE": "NO",
  "classification_policy": "explicit FeatureScript semantic fields only; generic qCreatedBy/sketchPlane excluded",
  "PRIMARY_FAILURE_COUNTS": {
    "EXTRUDE_EXTENT": 2,
    "UNKNOWN": 10,
    "SYMMETRIC_EXTRUDE": 2
  },
  "TOP_5_FAILURE_MODES": [
    [
      "UNKNOWN",
      10
    ],
    [
      "EXTRUDE_EXTENT",
      2
    ],
    [
      "SYMMETRIC_EXTRUDE",
      2
    ]
  ],
  "MOST_COMMON_FIRST_DIVERGENCE_OPERATION": "UNAVAILABLE_SOURCE_INTERMEDIATE_BODIES",
  "cases": [
    {
      "cad_id": "cadfs__00039808",
      "source_id": "00039808",
      "prefix_geometry_available": "NO",
      "FIRST_DIVERGENCE_OP": null,
      "PRIMARY_FAILURE_MODE": "EXTRUDE_EXTENT",
      "SECONDARY_FAILURE_MODES": [],
      "explicit_semantic_evidence": {
        "extent": true,
        "symmetric_or_two_sided": false,
        "face_attached": false,
        "source_extrude_count": 5,
        "dsl_body_count": 5
      },
      "chamfer_rel": 0.10975751580275968,
      "coverage_02": 0.232666015625
    },
    {
      "cad_id": "cadfs__00563891",
      "source_id": "00563891",
      "prefix_geometry_available": "NO",
      "FIRST_DIVERGENCE_OP": null,
      "PRIMARY_FAILURE_MODE": "UNKNOWN",
      "SECONDARY_FAILURE_MODES": [],
      "explicit_semantic_evidence": {
        "extent": false,
        "symmetric_or_two_sided": false,
        "face_attached": false,
        "source_extrude_count": 10,
        "dsl_body_count": 10
      },
      "chamfer_rel": 0.007253370746461387,
      "coverage_02": 0.973876953125
    },
    {
      "cad_id": "cadfs__00001411",
      "source_id": "00001411",
      "prefix_geometry_available": "NO",
      "FIRST_DIVERGENCE_OP": null,
      "PRIMARY_FAILURE_MODE": "SYMMETRIC_EXTRUDE",
      "SECONDARY_FAILURE_MODES": [],
      "explicit_semantic_evidence": {
        "extent": true,
        "symmetric_or_two_sided": true,
        "face_attached": false,
        "source_extrude_count": 1,
        "dsl_body_count": 1
      },
      "chamfer_rel": 0.12942643847620353,
      "coverage_02": 0.510986328125
    },
    {
      "cad_id": "cadfs__00005418",
      "source_id": "00005418",
      "prefix_geometry_available": "NO",
      "FIRST_DIVERGENCE_OP": null,
      "PRIMARY_FAILURE_MODE": "UNKNOWN",
      "SECONDARY_FAILURE_MODES": [],
      "explicit_semantic_evidence": {
        "extent": false,
        "symmetric_or_two_sided": false,
        "face_attached": false,
        "source_extrude_count": 1,
        "dsl_body_count": 1
      },
      "chamfer_rel": 0.096784395752769,
      "coverage_02": 0.107666015625
    },
    {
      "cad_id": "cadfs__00009369",
      "source_id": "00009369",
      "prefix_geometry_available": "NO",
      "FIRST_DIVERGENCE_OP": null,
      "PRIMARY_FAILURE_MODE": "UNKNOWN",
      "SECONDARY_FAILURE_MODES": [],
      "explicit_semantic_evidence": {
        "extent": false,
        "symmetric_or_two_sided": false,
        "face_attached": false,
        "source_extrude_count": 1,
        "dsl_body_count": 1
      },
      "chamfer_rel": 0.045071950181778044,
      "coverage_02": 0.23284912109375
    },
    {
      "cad_id": "cadfs__00020017",
      "source_id": "00020017",
      "prefix_geometry_available": "NO",
      "FIRST_DIVERGENCE_OP": null,
      "PRIMARY_FAILURE_MODE": "UNKNOWN",
      "SECONDARY_FAILURE_MODES": [],
      "explicit_semantic_evidence": {
        "extent": false,
        "symmetric_or_two_sided": false,
        "face_attached": false,
        "source_extrude_count": 1,
        "dsl_body_count": 1
      },
      "chamfer_rel": 0.3136122750449483,
      "coverage_02": 0.109130859375
    },
    {
      "cad_id": "cadfs__00020861",
      "source_id": "00020861",
      "prefix_geometry_available": "NO",
      "FIRST_DIVERGENCE_OP": null,
      "PRIMARY_FAILURE_MODE": "SYMMETRIC_EXTRUDE",
      "SECONDARY_FAILURE_MODES": [],
      "explicit_semantic_evidence": {
        "extent": true,
        "symmetric_or_two_sided": true,
        "face_attached": false,
        "source_extrude_count": 1,
        "dsl_body_count": 1
      },
      "chamfer_rel": 0.12977825461090756,
      "coverage_02": 0.51922607421875
    },
    {
      "cad_id": "cadfs__00041143",
      "source_id": "00041143",
      "prefix_geometry_available": "NO",
      "FIRST_DIVERGENCE_OP": null,
      "PRIMARY_FAILURE_MODE": "UNKNOWN",
      "SECONDARY_FAILURE_MODES": [],
      "explicit_semantic_evidence": {
        "extent": false,
        "symmetric_or_two_sided": false,
        "face_attached": false,
        "source_extrude_count": 1,
        "dsl_body_count": 1
      },
      "chamfer_rel": 0.49576345176018993,
      "coverage_02": 0.0401611328125
    },
    {
      "cad_id": "cadfs__00048277",
      "source_id": "00048277",
      "prefix_geometry_available": "NO",
      "FIRST_DIVERGENCE_OP": null,
      "PRIMARY_FAILURE_MODE": "UNKNOWN",
      "SECONDARY_FAILURE_MODES": [],
      "explicit_semantic_evidence": {
        "extent": false,
        "symmetric_or_two_sided": false,
        "face_attached": false,
        "source_extrude_count": 1,
        "dsl_body_count": 1
      },
      "chamfer_rel": 0.34983297771025595,
      "coverage_02": 0.01611328125
    },
    {
      "cad_id": "cadfs__00057052",
      "source_id": "00057052",
      "prefix_geometry_available": "NO",
      "FIRST_DIVERGENCE_OP": null,
      "PRIMARY_FAILURE_MODE": "EXTRUDE_EXTENT",
      "SECONDARY_FAILURE_MODES": [],
      "explicit_semantic_evidence": {
        "extent": true,
        "symmetric_or_two_sided": false,
        "face_attached": false,
        "source_extrude_count": 1,
        "dsl_body_count": 1
      },
      "chamfer_rel": 0.32002593454849937,
      "coverage_02": 0.17034912109375
    },
    {
      "cad_id": "cadfs__00059940",
      "source_id": "00059940",
      "prefix_geometry_available": "NO",
      "FIRST_DIVERGENCE_OP": null,
      "PRIMARY_FAILURE_MODE": "UNKNOWN",
      "SECONDARY_FAILURE_MODES": [],
      "explicit_semantic_evidence": {
        "extent": false,
        "symmetric_or_two_sided": false,
        "face_attached": false,
        "source_extrude_count": 1,
        "dsl_body_count": 1
      },
      "chamfer_rel": 0.47580486712637055,
      "coverage_02": 0.07208251953125
    },
    {
      "cad_id": "cadfs__00061569",
      "source_id": "00061569",
      "prefix_geometry_available": "NO",
      "FIRST_DIVERGENCE_OP": null,
      "PRIMARY_FAILURE_MODE": "UNKNOWN",
      "SECONDARY_FAILURE_MODES": [],
      "explicit_semantic_evidence": {
        "extent": false,
        "symmetric_or_two_sided": false,
        "face_attached": false,
        "source_extrude_count": 1,
        "dsl_body_count": 1
      },
      "chamfer_rel": 0.2898740816750907,
      "coverage_02": 0.18353271484375
    },
    {
      "cad_id": "cadfs__00063321",
      "source_id": "00063321",
      "prefix_geometry_available": "NO",
      "FIRST_DIVERGENCE_OP": null,
      "PRIMARY_FAILURE_MODE": "UNKNOWN",
      "SECONDARY_FAILURE_MODES": [],
      "explicit_semantic_evidence": {
        "extent": false,
        "symmetric_or_two_sided": false,
        "face_attached": false,
        "source_extrude_count": 1,
        "dsl_body_count": 1
      },
      "chamfer_rel": 0.02335577876226696,
      "coverage_02": 0.48968505859375
    },
    {
      "cad_id": "cadfs__00063621",
      "source_id": "00063621",
      "prefix_geometry_available": "NO",
      "FIRST_DIVERGENCE_OP": null,
      "PRIMARY_FAILURE_MODE": "UNKNOWN",
      "SECONDARY_FAILURE_MODES": [],
      "explicit_semantic_evidence": {
        "extent": false,
        "symmetric_or_two_sided": false,
        "face_attached": false,
        "source_extrude_count": 1,
        "dsl_body_count": 1
      },
      "chamfer_rel": 0.5069362688152615,
      "coverage_02": 0.01068115234375
    }
  ]
}
```

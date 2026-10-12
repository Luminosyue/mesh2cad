# CADFS301 source-semantic operation and complexity aggregation

```json
{
  "source_operation_definition": "direct FeatureScript lexical operation-semantic flags; a CAD may be counted in multiple buckets",
  "BY_OPERATION": {
    "EXTRUDE": {
      "count": 301,
      "geometry_pass": 129,
      "pass_rate": 0.42857142857142855
    },
    "BOOLEAN": {
      "count": 0,
      "geometry_pass": 0,
      "pass_rate": null
    },
    "PROFILE_HOLE": {
      "count": 8,
      "geometry_pass": 2,
      "pass_rate": 0.25
    },
    "FACE_ATTACHED_SKETCH": {
      "count": 0,
      "geometry_pass": 0,
      "pass_rate": null
    },
    "SYMMETRIC_EXTRUDE": {
      "count": 40,
      "geometry_pass": 1,
      "pass_rate": 0.025
    },
    "EXTRUDE_EXTENT": {
      "count": 59,
      "geometry_pass": 4,
      "pass_rate": 0.06779661016949153
    },
    "REVOLVE": {
      "count": 0,
      "geometry_pass": 0,
      "pass_rate": null
    },
    "FILLET": {
      "count": 0,
      "geometry_pass": 0,
      "pass_rate": null
    },
    "CHAMFER": {
      "count": 0,
      "geometry_pass": 0,
      "pass_rate": null
    },
    "PATTERN": {
      "count": 0,
      "geometry_pass": 0,
      "pass_rate": null
    }
  },
  "BY_COMPLEXITY_TERCILES": {
    "SIMPLE": {
      "count": 281,
      "geometry_pass": 124,
      "pass_rate": 0.4412811387900356
    },
    "MEDIUM": {
      "count": 0,
      "geometry_pass": 0,
      "pass_rate": null
    },
    "HARD": {
      "count": 20,
      "geometry_pass": 5,
      "pass_rate": 0.25
    }
  },
  "complexity_basis": {
    "metric": "FeatureScript feature-call count",
    "q1": 2.0,
    "q2": 2.0,
    "counts": {
      "SIMPLE": 281,
      "HARD": 20
    }
  }
}
```

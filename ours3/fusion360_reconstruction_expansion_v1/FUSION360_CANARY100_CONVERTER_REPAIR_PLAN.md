# FUSION360_CANARY100_CONVERTER_REPAIR_PLAN

Scope: frozen Canary100 audit only. No converter patch was applied.

## TOP1: origin_axis_placement (21 cases)
SOURCE_SEMANTICS: Sketch transforms and face-attached sketches define local profile coordinates in a 3D frame.
CURRENT_CONVERTER_BEHAVIOR: _sketch_frame emits origin, z_axis, x_axis but ignores y_axis and any transform composition beyond direct frame fields.
EXPECTED_CANONICAL_DSL: Profile placement should match Fusion world frame and preserve axis orientation for all attached sketch planes.
MISSING_INFORMATION: Full transform matrix composition and parent component occurrence transform.
MINIMAL_PATCH_LOCATION: scripts/fusion360/fusion360_to_dsl.py::_sketch_frame and profile point projection logic
REGRESSION_RISK: High; frame fixes can rotate/translate many previously passing cases.

## TOP2: missing_body_or_boolean (20 cases)
SOURCE_SEMANTICS: Source appears within intended feature family but converter/QA result is inconsistent.
CURRENT_CONVERTER_BEHAVIOR: Fails without a precise semantic subtype.
EXPECTED_CANONICAL_DSL: Same canonical DSL, with corrected ingestion/parser behavior only.
MISSING_INFORMATION: Traceback-level converter failure and minimal reproducer.
MINIMAL_PATCH_LOCATION: scripts/fusion360/fusion360_to_dsl.py plus one regression fixture per case.
REGRESSION_RISK: Unknown until root-cause isolated.

## TOP3: unit_conversion (8 cases)
SOURCE_SEMANTICS: Source appears within intended feature family but converter/QA result is inconsistent.
CURRENT_CONVERTER_BEHAVIOR: Fails without a precise semantic subtype.
EXPECTED_CANONICAL_DSL: Same canonical DSL, with corrected ingestion/parser behavior only.
MISSING_INFORMATION: Traceback-level converter failure and minimal reproducer.
MINIMAL_PATCH_LOCATION: scripts/fusion360/fusion360_to_dsl.py plus one regression fixture per case.
REGRESSION_RISK: Unknown until root-cause isolated.

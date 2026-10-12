# EXACT10K target schema audit

## Determined format

TARGET_FORMAT=Canonical CAD DSL v1 text assignment program.

The original training target is the gpt conversation value read from cad_target.dsl (or targeted program_canonical.dsl). It is plain text containing assignments and a final result = ...; it is not JSON and not Python source.

EXACT10K_TARGET_IS_FUSION360_API=NO. It is a project canonical intermediate representation inspired by CAD operations. The executor lowers this DSL to CadQuery/OCP through scripts/deepcad/dsl_to_occ.py and edge_aware_cad_planner_v1.cad_dsl.execute_dsl. It is distinct from Fusion 360 adsk.fusion Python API code and from a native Fusion 360 feature-history export.

## Evidence from frozen train split

Prompt advertises: Sketch, Circle, Rectangle, Extrude, Cut, Union.

Observed serialized call vocabulary in all 8,000 train targets:
- Box: 5,801
- Circle: 3,279
- Extrude: 3,279
- ExtrudePolygon: 11,607
- Cut: 6,924
- Union: 5,762

Examples are stored verbatim in exact10k_audit/sample_dump/.

## Parameter and runtime behavior

- Assignments bind intermediate bodies (body_0, body_1, ...); boolean calls reference prior bindings.
- Continuous values are decimal physical values in the canonical CAD frame.
- Coordinates use explicit origin, axis, x_axis and named dimensions such as width, depth, height, radius, points.
- This is not a flattened numeric stream. A conversion must use operation, section, parameter role, point index and coordinate axis as semantic keys.
- Compact IR uses 14-bit q. Convert with metadata dequantization, then reserialize through the old serializer. Directly copying q integers is invalid.
- Feature order is assignment order and the final assignment must be result = ....
- Official template uses BOS, Llama headers, point marker, and eot after turns. EOS is included in supervised assistant target.
- Official collator masks source with -100 and supervises target including EOS. cutoff_len=8192; old frozen train has zero truncation.

## Runtime chain

Dataset adapter: exact10k_manifest_adapter.py -> official Dataset alignment (SharegptDatasetConverter).
Collator: spatiallm.tuner.data.collator.SFTDataCollatorWith4DAttentionMask.
Tokenizer: frozen Llama tokenizer at provenance path.
Executor: scripts/deepcad/dsl_to_occ.py.
Evaluator: scripts/deepcad/eval_cad_dsl.py.

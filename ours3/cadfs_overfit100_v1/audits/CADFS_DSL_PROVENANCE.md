# CADFS canonical DSL provenance

- **CADFS_TARGET_SOURCE:** FeatureScript (`CADFS/featurescript_rp/<bucket>/<id>.txt`)
- **CANONICAL_DSL_CONVERTER:** `/data/home/cuiyuehan/project/mesh2cad/scripts/canonical_cad_data_v4/converters/cadfs_to_dsl.py`
- **FUNCTION:** `cadfs_to_dsl(text) -> (dsl_text, report)`
- **TARGET:** `cad_target.dsl`; this experiment does not train on raw FeatureScript.
- **Supported lossless subset:** line/circle/rectangle/polygon sketches; extrude; New/Add/Remove body operations; canonical result expression.
- **Unsupported:** revolve, loft, sweep, fillet, chamfer, shell, mirror, pattern, arc, ellipse, bspline, unsupported sketch planes/profile forms.
- The converter must reject unsupported operations; it never approximates them as an Extrude.

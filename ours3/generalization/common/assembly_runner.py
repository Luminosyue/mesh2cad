from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
XCAF_ROOT = ROOT / "v13_transform_restore_and_xcaf_assembly"


def build(entries: list[dict[str, Any]], output: Path) -> dict[str, Any]:
    """Build and independently reload a generic XCAF assembly.

    Entries are deliberately passed to the category-independent V13 assembly
    builder. No historical manifest or CASE09 assembly runner is consulted.
    """
    sys.path.insert(0, str(XCAF_ROOT))
    from assembly.xcaf_assembly_builder import build_xcaf_assembly, export_xcaf_step
    from assembly.assembly_reload_validator import reload_xcaf, validate_reloaded_components

    built = build_xcaf_assembly("BUILDING_CROSS_CASE_GENERALIZATION_V1", entries)
    export_xcaf_step(built.doc, output, "BUILDING_CROSS_CASE_GENERALIZATION_V1")
    doc, shapes, info = reload_xcaf(output)
    metrics = validate_reloaded_components(doc)
    return {
        "info": {**info, **metrics},
        "component_count": len(built.components),
        "shape_count": len(shapes),
    }

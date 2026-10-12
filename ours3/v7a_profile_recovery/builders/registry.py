from .loft_builder import LoftBuilder
from .extrusion_builder import ExtrusionBuilder
from .bspline_skin_builder import BSplineSkinBuilder


BUILDERS = {"LOFT": LoftBuilder(), "EXTRUSION": ExtrusionBuilder(),
            "BSPLINE_SKIN": BSplineSkinBuilder()}


def get_builder(hypothesis):
    if hypothesis not in BUILDERS:
        raise ValueError(f"UNSUPPORTED_HYPOTHESIS {hypothesis}")
    return BUILDERS[hypothesis]

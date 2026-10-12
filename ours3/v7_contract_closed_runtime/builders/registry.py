from .extrusion_builder import ExtrusionBuilder
from .revolution_builder import RevolutionBuilder
from .loft_builder import LoftBuilder
from .ruled_builder import RuledBuilder
from .bspline_skin_builder import BSplineSkinBuilder
REGISTRY={"EXTRUSION":ExtrusionBuilder,"REVOLUTION":RevolutionBuilder,"LOFT":LoftBuilder,"RULED":RuledBuilder,"BSPLINE_SKIN":BSplineSkinBuilder}
def get_builder(name):
    if name not in REGISTRY:raise ValueError(f"CONTRACT_VIOLATION unknown builder hypothesis {name}")
    return REGISTRY[name]()

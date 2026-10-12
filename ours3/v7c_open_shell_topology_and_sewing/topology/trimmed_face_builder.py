"""Create only genuine wire-trimmed faces; no untrimmed fallback."""

from OCP.BRep import BRep_Tool
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCP.BRepCheck import BRepCheck_Analyzer


def build_trimmed_face(source_face, wire):
    surface = BRep_Tool.Surface_s(source_face)
    maker = BRepBuilderAPI_MakeFace(surface, wire, True)
    if not maker.IsDone():
        raise RuntimeError("TRIMMED_FACE_BUILD_FAILED")
    face = maker.Face()
    if face.IsNull() or not BRepCheck_Analyzer(face).IsValid():
        raise RuntimeError("TRIMMED_FACE_INVALID")
    return face


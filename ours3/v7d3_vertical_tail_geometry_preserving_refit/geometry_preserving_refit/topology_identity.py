"""Build one edge and two endpoint vertices shared by both trimmed faces."""

from __future__ import annotations

from OCP.BRep import BRep_Builder, BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Curve2d
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepTools import BRepTools_ReShape
from OCP.ShapeAnalysis import ShapeAnalysis_Edge
from OCP.TopAbs import TopAbs_VERTEX
from OCP.TopExp import TopExp_Explorer
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS

from boundary_control_net.topology_preview import _pcurve_error, _side_edge


def _vertices(edge):
    out=[]; explorer=TopExp_Explorer(edge,TopAbs_VERTEX)
    while explorer.More(): out.append(TopoDS.Vertex_s(explorer.Current())); explorer.Next()
    return out


def build(surface_a, face_a, surface_b, face_b, side_a, side_b, precision):
    _,_,v0,v1=surface_a.Bounds(); curve=surface_a.VIso(v0 if side_a=="V_MIN" else v1)
    old_a=_side_edge(face_a,surface_a,side_a); old_b=_side_edge(face_b,surface_b,side_b)
    vertices_a=_vertices(old_a)
    # Use A's endpoint TShapes to keep its wire closed; B's two endpoint
    # TShapes are explicitly consolidated to them below.
    edge=BRepBuilderAPI_MakeEdge(curve,vertices_a[0],vertices_a[1]).Edge()
    aa=BRepAdaptor_Curve2d(old_a,face_a); ab=BRepAdaptor_Curve2d(old_b,face_b)
    builder=BRep_Builder(); loc=TopLoc_Location()
    builder.UpdateEdge(edge,aa.Curve(),surface_a,loc,float(precision)); builder.UpdateEdge(edge,ab.Curve(),surface_b,loc,float(precision))
    builder.Range(edge,surface_a,loc,aa.FirstParameter(),aa.LastParameter()); builder.Range(edge,surface_b,loc,ab.FirstParameter(),ab.LastParameter())
    ra=BRepTools_ReShape(); ra.Replace(old_a,edge.Oriented(old_a.Orientation())); ta=TopoDS.Face_s(ra.Apply(face_a))
    rb=BRepTools_ReShape(); vb=_vertices(old_b); shared=_vertices(edge)
    for source in vb:
        point=BRep_Tool.Pnt_s(source); target=min(shared,key=lambda vertex:point.Distance(BRep_Tool.Pnt_s(vertex)))
        rb.Replace(source,target.Oriented(source.Orientation()))
    rb.Replace(old_b,edge.Oriented(old_b.Orientation())); tb=TopoDS.Face_s(rb.Apply(face_b))
    ea,eb=_pcurve_error(edge,ta),_pcurve_error(edge,tb)
    return {"edge":edge,"trimmed_face_a":ta,"trimmed_face_b":tb,"EDGE_OCC_VALID":bool(BRepCheck_Analyzer(edge).IsValid()),"TRIMMED_FACE_A_VALID":bool(BRepCheck_Analyzer(ta).IsValid()),"TRIMMED_FACE_B_VALID":bool(BRepCheck_Analyzer(tb).IsValid()),"PCURVE_A_SUCCESS":bool(ShapeAnalysis_Edge().HasPCurve(edge,ta)),"PCURVE_B_SUCCESS":bool(ShapeAnalysis_Edge().HasPCurve(edge,tb)),"PCURVE_A_ERROR":ea,"PCURVE_B_ERROR":eb}

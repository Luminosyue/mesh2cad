import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(4,0,0))
r=w0.sketch().segment((-42,-3),(96,-3)).segment((96,-2)).segment((100,1)).segment((96,6)).segment((96,3)).segment((4,3)).arc((-18,-2),(-42,4)).close().assemble().finalize().extrude(-8).union(w0.sketch().segment((-100,0),(-93,0)).segment((-93,1)).close().assemble().reset().face(w0.sketch().segment((-48,0),(-40,0)).segment((-40,1)).close().assemble()).finalize().extrude(-1))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0066_00663005.step')

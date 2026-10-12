import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,0))
r=w0.sketch().push([(-80,0)]).circle(8).reset().face(w0.sketch().segment((-52,-7),(-32,-7)).segment((-32,-1)).segment((-29,-1)).segment((-29,-7)).segment((100,-7)).segment((100,7)).segment((54,7)).arc((42,7),(30,7)).segment((-52,7)).close().assemble()).finalize().extrude(-1)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0017_00172415.step')

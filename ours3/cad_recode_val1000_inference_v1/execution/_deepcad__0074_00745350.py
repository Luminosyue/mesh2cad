import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-2))
r=w0.sketch().segment((-100,-5),(-61,-5)).arc((-66,0),(-67,5)).segment((-100,5)).close().assemble().reset().face(w0.sketch().segment((-57,-5),(-1,-5)).arc((-2,-1),(-2,5)).segment((-50,5)).arc((-49,0),(-57,-5)).assemble()).reset().face(w0.sketch().segment((2,-5),(100,-5)).segment((100,5)).segment((14,5)).arc((8,0),(2,-5)).assemble()).finalize().extrude(4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0074_00745350.step')

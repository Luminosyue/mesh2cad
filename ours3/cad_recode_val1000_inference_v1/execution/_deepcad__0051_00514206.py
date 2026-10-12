import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,5))
r=w0.sketch().segment((-100,-39),(-52,-39)).arc((-56,-33),(-57,-26)).segment((-78,-26)).segment((-78,-14)).segment((-57,-14)).arc((-56,-7),(-52,-1)).segment((-100,39)).close().assemble().reset().face(w0.sketch().segment((-49,39),(-29,14)).segment((-50,14)).arc((-47,7),(-45,-1)).segment((-24,-1)).segment((-24,-14)).segment((-45,-14)).arc((-47,-23),(-54,-29)).segment((-34,-39)).segment((-15,-39)).segment((-15,-15)).arc((27,-12),(50,21)).segment((67,-39)).segment((100,-39)).segment((100,39)).segment((23,39)).segment((23,28)).segment((-6,39)).segment((-34,39)).segment((-34,30)).segment((-39,39)).close().assemble()).finalize().extrude(-10)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0051_00514206.step')

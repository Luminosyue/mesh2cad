import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
w1=cq.Workplane('XY',origin=(0,0,72))
r=w0.workplane(offset=-190/2).cylinder(190,20).union(w0.sketch().segment((-10,-34),(10,-34)).segment((10,-17)).arc((17,0),(10,17)).segment((10,34)).segment((-10,34)).segment((-10,17)).arc((-17,0),(-10,-17)).close().assemble().finalize().extrude(-44)).union(w1.sketch().segment((-2,-44),(2,-44)).segment((2,-39)).arc((19,0),(2,39)).segment((2,44)).segment((-2,44)).segment((-2,39)).arc((-20,0),(-2,-39)).close().assemble().finalize().extrude(-165))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0065_00656188.step')

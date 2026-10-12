import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,7))
r=w0.sketch().segment((-100,-11),(-81,-31)).segment((-61,-4)).segment((-77,6)).segment((-78,4)).arc((-70,-13),(-84,3)).close().assemble().reset().face(w0.sketch().segment((-56,1),(95,1)).segment((95,11)).segment((100,15)).segment((95,22)).segment((95,31)).segment((89,31)).segment((88,31)).segment((-56,31)).close().assemble()).finalize().extrude(-14)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0076_00765293.step')

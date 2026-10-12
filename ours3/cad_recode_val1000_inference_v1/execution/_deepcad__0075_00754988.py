import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,6,0))
r=w0.sketch().segment((-100,-10),(-96,-10)).segment((-96,-12)).segment((100,-12)).segment((100,12)).segment((27,12)).segment((27,9)).segment((2,9)).segment((2,12)).segment((-96,12)).segment((-96,7)).segment((-100,7)).close().assemble().push([(-69,-5)]).circle(5,mode='s').push([(69,-4)]).circle(5,mode='s').finalize().extrude(-12)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0075_00754988.step')

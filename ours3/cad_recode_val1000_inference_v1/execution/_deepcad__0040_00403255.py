import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-7,0))
r=w0.sketch().segment((-15,-100),(15,-100)).segment((15,-23)).segment((1,-33)).segment((-15,-28)).close().assemble().reset().face(w0.sketch().segment((-15,-15),(15,-1)).segment((15,32)).arc((10,35),(15,38)).segment((15,100)).segment((-15,100)).close().assemble()).finalize().extrude(14)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0040_00403255.step')

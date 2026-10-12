import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,4,0))
r=w0.sketch().segment((-9,-100),(8,-100)).segment((8,-24)).segment((9,-24)).segment((9,32)).segment((8,32)).segment((8,100)).segment((-9,100)).segment((-9,74)).segment((-8,74)).segment((-8,56)).segment((-9,56)).close().assemble().push([(0,-46)]).circle(15,mode='s').finalize().extrude(-8)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0058_00587279.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,12,0))
r=w0.sketch().segment((-25,-100),(25,-100)).segment((25,-23)).segment((15,-23)).segment((15,-32)).segment((-15,-32)).segment((-15,-23)).segment((-25,-23)).close().assemble().reset().face(w0.sketch().segment((-25,-8),(-15,-8)).segment((-15,-1)).segment((15,-1)).segment((15,-8)).segment((25,-8)).segment((25,100)).segment((-25,100)).close().assemble()).finalize().extrude(-25)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0058_00585259.step')

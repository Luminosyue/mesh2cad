import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,3))
r=w0.sketch().segment((-50,-99),(-10,-91)).segment((-10,-89)).segment((-10,-69)).segment((-10,-68)).segment((-40,-68)).segment((-40,-69)).segment((-50,-69)).close().assemble().reset().face(w0.sketch().segment((-50,-33),(-40,-33)).segment((-40,-34)).segment((-39,-34)).segment((-39,-41)).segment((-38,-41)).segment((-38,-50)).segment((-39,-50)).segment((-39,-57)).segment((-16,-57)).segment((-16,-33)).segment((-5,-33)).segment((-5,-25)).segment((43,-25)).segment((43,-57)).segment((33,-57)).segment((33,-78)).segment((43,-78)).segment((43,-82)).segment((10,-82)).segment((10,-92)).segment((42,-98)).segment((50,-61)).segment((50,93)).segment((35,100)).segment((26,100)).segment((40,77)).segment((-16,51)).segment((-16,83)).segment((15,97)).segment((15,100)).segment((-50,100)).segment((-50,34)).segment((-16,51)).segment((-16,49)).segment((-50,35)).segment((-50,15)).arc((-10,-12),(-50,-38)).close().assemble()).finalize().extrude(-6)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0036_00364340.step')

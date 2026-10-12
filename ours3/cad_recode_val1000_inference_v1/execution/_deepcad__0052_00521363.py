import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-16,0))
r=w0.sketch().segment((-100,-100),(100,-100)).segment((100,94)).segment((73,94)).segment((73,100)).segment((-100,100)).segment((-100,12)).segment((-14,12)).segment((-14,5)).segment((-100,5)).close().assemble().reset().face(w0.sketch().segment((-88,-56),(-6,-56)).segment((-6,-92)).segment((6,-92)).segment((6,-56)).segment((88,-56)).segment((88,-26)).segment((6,-26)).segment((6,10)).segment((100,10)).segment((100,26)).segment((6,26)).segment((6,52)).segment((-6,52)).segment((-6,26)).segment((-88,26)).segment((-88,10)).segment((-6,10)).segment((-6,-26)).segment((-88,-26)).close().assemble(),mode='s').push([(32,55)]).circle(23,mode='s').finalize().extrude(32)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0052_00521363.step')

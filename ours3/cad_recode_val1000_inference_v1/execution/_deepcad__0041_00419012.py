import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.sketch().arc((-100,-70),(-5,0),(-100,70)).close().assemble().finalize().extrude(153).union(w0.sketch().segment((-100,-100),(100,-100)).segment((100,0)).segment((2,0)).segment((-36,36)).arc((-71,-1),(-100,-42)).close().assemble().finalize().extrude(200))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0041_00419012.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-56,0))
r=w0.sketch().segment((-65,-100),(-35,-100)).segment((-35,-65)).segment((-65,-54)).close().assemble().reset().face(w0.sketch().segment((-65,-35),(-35,-46)).segment((-35,64)).segment((65,64)).segment((65,100)).segment((-65,100)).close().assemble()).reset().face(w0.sketch().segment((-10,-100),(65,-100)).segment((65,-65)).segment((-10,-76)).close().assemble()).finalize().extrude(112)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0061_00615301.step')

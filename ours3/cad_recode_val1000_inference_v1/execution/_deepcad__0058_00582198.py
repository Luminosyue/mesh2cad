import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-51,0))
r=w0.sketch().segment((-100,-100),(-80,-100)).segment((-80,-80)).segment((100,-100)).segment((100,-80)).segment((46,-80)).segment((46,-82)).segment((43,-82)).segment((43,-80)).segment((-80,-80)).segment((-80,100)).segment((-100,100)).segment((-100,-37)).segment((-98,-37)).segment((-98,-39)).segment((-100,-39)).close().assemble().reset().face(w0.sketch().segment((-100,-69),(-98,-69)).segment((-98,-66)).segment((-100,-65)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-100,-5),(-98,-6)).segment((-98,-3)).segment((-100,-3)).close().assemble(),mode='s').push([(-89,61)]).circle(12,mode='s').finalize().extrude(102)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0058_00582198.step')

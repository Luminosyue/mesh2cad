import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-8))
w1=cq.Workplane('ZX',origin=(0,-27,0))
r=w0.sketch().segment((62,-18),(80,-18)).segment((80,-15)).segment((62,-11)).close().assemble().reset().face(w0.sketch().segment((80,20),(100,20)).segment((100,27)).segment((80,27)).close().assemble()).finalize().extrude(8).union(w1.sketch().segment((-4,-100),(7,-100)).segment((7,-97)).segment((8,-97)).segment((8,-11)).segment((7,-11)).segment((7,81)).segment((-4,81)).segment((-4,-11)).segment((-4,-97)).close().assemble().push([(1,-48)]).circle(3,mode='s').push([(1,-10)]).circle(4,mode='s').finalize().extrude(32))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0060_00605012.step')

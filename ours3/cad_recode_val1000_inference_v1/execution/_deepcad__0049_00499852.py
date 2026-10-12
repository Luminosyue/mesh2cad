import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-62,0))
r=w0.sketch().segment((-94,-13),(-68,-13)).arc((0,-63),(68,-13)).segment((94,-13)).segment((94,13)).segment((68,13)).arc((0,63),(-68,13)).segment((-94,13)).close().assemble().finalize().extrude(3).union(w0.sketch().segment((-100,-58),(-80,-58)).segment((-80,-62)).segment((80,-62)).segment((80,-58)).segment((100,-58)).segment((100,58)).segment((80,58)).segment((80,62)).segment((-80,62)).segment((-80,58)).segment((-100,58)).close().assemble().reset().face(w0.sketch().segment((-100,-35),(-98,-35)).arc((-99,-29),(-98,-23)).segment((-100,-23)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-80,-58),(-78,-58)).segment((-78,-56)).segment((-80,-55)).close().assemble(),mode='s').push([(-45,48)]).circle(15,mode='s').push([(0,0)]).rect(20,44,mode='s').push([(45,48)]).rect(20,44,mode='s').finalize().extrude(125))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0049_00499852.step')

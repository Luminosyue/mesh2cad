import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-44,0))
r=w0.sketch().segment((-33,-34),(-15,-34)).segment((-15,-100)).segment((25,-100)).segment((25,-34)).segment((33,-34)).segment((33,100)).segment((-33,100)).close().assemble().reset().face(w0.sketch().segment((-15,-29),(-15,29)).arc((-32,0),(-15,-29)).assemble(),mode='s').reset().face(w0.sketch().arc((-10,-34),(0,-35),(10,-34)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-10,34),(10,34)).arc((0,35),(-10,34)).assemble(),mode='s').reset().face(w0.sketch().arc((25,-29),(42,0),(25,29)).close().assemble(),mode='s').finalize().extrude(89).union(w0.sketch().segment((-34,-90),(-31,-90)).segment((-31,-96)).segment((31,-96)).segment((31,-90)).segment((34,-90)).segment((34,90)).segment((31,90)).segment((31,96)).segment((-31,96)).segment((-31,90)).segment((-34,90)).close().assemble().finalize().extrude(89))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0071_00717344.step')

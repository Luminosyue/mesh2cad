import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-19))
w1=cq.Workplane('XY',origin=(0,0,-42))
r=w0.sketch().segment((-100,-55),(-33,-55)).arc((-34,-46),(-33,-37)).segment((-51,-37)).segment((-51,15)).segment((-30,15)).segment((-30,55)).segment((-100,55)).close().assemble().reset().face(w0.sketch().segment((-24,-18),(-12,-18)).arc((-12,-20),(-11,-22)).segment((-11,-55)).segment((100,-55)).segment((100,55)).segment((-24,55)).segment((-24,38)).segment((12,38)).segment((12,15)).segment((-7,15)).arc((-10,-10),(-24,-18)).assemble()).reset().face(w0.sketch().arc((17,-22),(39,-27),(58,-18)).segment((58,15)).segment((58,38)).segment((17,38)).close().assemble(),mode='s').finalize().extrude(-38).union(w0.workplane(offset=76/2).moveTo(-14,-19).box(32,30,76)).union(w1.sketch().arc((-51,-18),(-35,-22),(-20,-18)).close().assemble().finalize().extrude(22))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0004_00041577.step')

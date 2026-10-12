import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
w1=cq.Workplane('XY',origin=(0,0,14))
r=w0.sketch().segment((-96,-24),(-84,-26)).arc((-85,-24),(-85,-21)).arc((-91,10),(-72,38)).arc((-69,55),(-59,69)).segment((-69,72)).segment((-73,49)).segment((-92,40)).segment((-83,32)).close().assemble().reset().face(w0.sketch().segment((-60,-78),(-50,-85)).segment((-46,-77)).arc((-53,-76),(-60,-78)).assemble()).reset().face(w0.sketch().arc((-38,82),(-31,81),(-24,80)).arc((65,62),(85,-20)).segment((95,-28)).arc((91,41),(40,89)).segment((40,92)).segment((32,94)).arc((20,96),(8,98)).segment((0,100)).segment((-1,98)).arc((-22,96),(-42,89)).segment((-43,89)).close().assemble()).reset().face(w0.sketch().arc((-23,-85),(-13,-97),(1,-100)).close().assemble()).finalize().extrude(-200).union(w0.sketch().arc((-97,16),(-92,-39),(-51,-79)).segment((-51,-85)).segment((-41,-85)).arc((0,-93),(41,-85)).segment((51,-85)).segment((51,-79)).arc((72,-51),(83,-18)).arc((-10,-88),(-97,16)).assemble().finalize().extrude(-33)).union(w1.sketch().arc((84,-28),(90,-31),(94,-35)).arc((96,-19),(100,-2)).arc((93,-15),(84,-28)).assemble().finalize().extrude(-61))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0087_00879927.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,8,0))
r=w0.sketch().segment((-98,12),(-87,-10)).arc((-94,-33),(-83,-52)).arc((-74,-67),(-60,-79)).segment((-59,-79)).arc((-48,-75),(-40,-67)).arc((-35,-61),(-31,-54)).arc((-28,-45),(-28,-35)).arc((-35,-14),(-52,-1)).segment((-25,32)).segment((-37,32)).segment((-37,72)).segment((-51,84)).segment((-98,14)).close().assemble().reset().face(w0.sketch().segment((-87,21),(-74,18)).segment((-74,20)).segment((-86,23)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-63,-13),(-51,-16)).segment((-51,-14)).segment((-39,-17)).segment((-34,-17)).segment((-34,-22)).segment((15,-37)).segment((66,68)).segment((12,99)).close().assemble()).reset().face(w0.sketch().arc((-37,-93),(30,-95),(80,-48)).segment((60,-48)).segment((60,-28)).segment((83,-28)).segment((83,-40)).arc((93,-10),(94,21)).close().assemble()).finalize().extrude(-15)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0039_00390278.step')

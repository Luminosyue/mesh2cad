import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-19))
r=w0.sketch().segment((-87,-96),(-72,-96)).segment((-72,-100)).segment((81,-100)).segment((81,-96)).segment((87,-96)).segment((87,96)).segment((81,96)).segment((81,100)).segment((58,100)).segment((80,30)).segment((-54,-22)).segment((-72,27)).segment((33,63)).segment((-60,100)).segment((-72,100)).segment((-72,96)).segment((-87,96)).close().assemble().reset().face(w0.sketch().segment((-82,-53),(-59,-79)).segment((-59,-96)).segment((-46,-96)).segment((-45,-97)).segment((-44,-96)).segment((-36,-96)).segment((-36,-92)).segment((-13,-72)).segment((-36,-46)).segment((-36,-29)).segment((-49,-29)).segment((-50,-28)).segment((-51,-29)).segment((-59,-29)).segment((-59,-33)).close().assemble(),mode='s').finalize().extrude(38)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0082_00823776.step')

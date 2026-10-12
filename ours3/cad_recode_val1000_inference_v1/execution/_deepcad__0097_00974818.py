import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,90,0))
w1=cq.Workplane('YZ',origin=(-23,0,0))
r=w0.sketch().arc((-80,-44),(-44,-55),(-7,-53)).arc((1,-27),(23,-42)).arc((29,-46),(34,-51)).arc((47,-55),(60,-53)).segment((80,-57)).segment((80,57)).segment((60,58)).arc((33,41),(3,58)).segment((-23,58)).segment((-23,52)).arc((-33,52),(-43,50)).arc((-59,21),(-80,-6)).close().assemble().push([(66,36)]).circle(6,mode='s').finalize().extrude(10).union(w1.sketch().segment((-90,-80),(-63,-80)).segment((-63,-69)).arc((-29,-79),(5,-69)).segment((5,-70)).segment((25,-70)).segment((25,-66)).arc((86,0),(25,66)).segment((25,80)).segment((-63,80)).segment((-63,66)).arc((-99,55),(-83,22)).arc((-82,16),(-80,11)).arc((-82,-10),(-75,-30)).arc((-84,-45),(-90,-62)).close().assemble().push([(-50,48)]).circle(32,mode='s').push([(25,0)]).circle(6,mode='s').finalize().extrude(11))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0097_00974818.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-1))
w1=cq.Workplane('YZ',origin=(-34,0,0))
r=w0.sketch().segment((-83,-78),(-51,-78)).segment((-51,-60)).arc((-67,-62),(-83,-60)).close().assemble().finalize().extrude(-35).union(w0.sketch().segment((-29,-15),(-15,-15)).segment((-15,-33)).segment((43,-34)).segment((43,-29)).segment((76,-29)).segment((76,-15)).segment((100,-15)).segment((100,13)).segment((59,13)).segment((59,10)).segment((37,10)).segment((37,13)).segment((-29,13)).close().assemble().reset().face(w0.sketch().segment((76,-21),(84,-21)).segment((84,10)).segment((76,10)).segment((76,9)).arc((82,-5),(76,-19)).close().assemble(),mode='s').finalize().extrude(32)).union(w1.sketch().arc((-84,-19),(-54,-6),(-24,-11)).segment((-24,11)).segment((13,11)).segment((13,35)).segment((-84,35)).close().assemble().push([(61,0)]).rect(46,72).finalize().extrude(-66))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0012_00126901.step')

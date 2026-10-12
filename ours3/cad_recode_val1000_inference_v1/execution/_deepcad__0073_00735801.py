import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-67,0))
w1=cq.Workplane('XY',origin=(0,0,-17))
r=w0.sketch().segment((-83,-100),(83,-100)).segment((83,-33)).segment((-17,-33)).segment((-17,82)).arc((-14,87),(-17,92)).segment((-17,100)).segment((-83,100)).segment((-83,60)).arc((-80,59),(-83,58)).segment((-83,-42)).segment((-81,-42)).segment((-81,-44)).segment((-83,-44)).close().assemble().push([(-49,-76)]).circle(4,mode='s').push([(66,-67)]).circle(2,mode='s').finalize().extrude(114).union(w0.sketch().arc((-38,-33),(-22,-35),(-5,-33)).close().assemble().reset().face(w0.sketch().segment((-38,52),(-5,52)).arc((-22,54),(-38,52)).assemble()).reset().face(w0.sketch().arc((24,-33),(51,-51),(78,-33)).close().assemble()).finalize().extrude(124)).union(w1.sketch().arc((-14,-28),(40,-40),(73,-67)).segment((100,-67)).segment((100,67)).segment((-14,67)).close().assemble().finalize().extrude(-66))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0073_00735801.step')

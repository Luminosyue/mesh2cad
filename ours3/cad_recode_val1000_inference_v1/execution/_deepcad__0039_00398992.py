import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-35))
w1=cq.Workplane('XY',origin=(0,0,-15))
r=w0.sketch().segment((-100,-2),(-42,-87)).segment((50,-87)).segment((100,2)).segment((42,65)).segment((32,28)).arc((54,0),(34,-28)).arc((-14,-40),(-34,6)).segment((-43,6)).segment((-43,12)).segment((-34,12)).arc((-13,40),(19,38)).segment((19,42)).segment((-50,42)).segment((-50,12)).segment((-43,12)).segment((-43,6)).segment((-50,6)).segment((-50,1)).segment((-65,60)).segment((-50,63)).segment((-50,87)).segment((21,87)).segment((21,86)).segment((-31,86)).segment((-31,87)).segment((-42,87)).segment((-42,86)).segment((-50,86)).segment((-50,83)).close().assemble().finalize().extrude(70).union(w0.sketch().arc((-88,21),(-75,32),(-60,40)).segment((-60,63)).arc((-79,39),(-88,21)).assemble().reset().face(w0.sketch().arc((32,-28),(37,-29),(42,-30)).segment((42,28)).arc((37,26),(32,24)).close().assemble()).reset().face(w0.sketch().arc((51,5),(61,32),(55,61)).close().assemble()).finalize().extrude(70)).union(w1.sketch().arc((-42,-10),(59,-72),(65,46)).arc((31,-29),(-42,-10)).assemble().finalize().extrude(27))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0039_00398992.step')

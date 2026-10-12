import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-28,0))
r=w0.sketch().push([(0,-51)]).circle(15).push([(0,-50.5)]).rect(26,9,mode='s').reset().face(w0.sketch().segment((-13,79),(-13,80)).arc((1,58),(12,81)).segment((12,66)).segment((6,66)).segment((6,59)).segment((-1,59)).segment((3,44)).segment((10,46)).segment((5,66)).segment((12,66)).segment((12,79)).arc((1,100),(-13,79)).assemble()).finalize().extrude(56).union(w0.sketch().arc((-35,-44),(-35,-78),(-10,-98)).segment((-10,-99)).segment((-7,-98)).arc((5,-99),(16,-96)).segment((19,-95)).segment((19,-94)).arc((28,-88),(35,-78)).segment((37,-77)).segment((37,-76)).arc((37,-51),(21,-29)).arc((1,-22),(-19,-27)).segment((-22,-27)).segment((-22,-28)).arc((-29,-35),(-35,-44)).assemble().push([(0,-51)]).circle(14,mode='s').push([(0,72)]).circle(18).circle(16,mode='s').finalize().extrude(56))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0066_00660529.step')

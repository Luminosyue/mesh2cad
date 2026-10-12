import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,10))
r=w0.sketch().segment((-100,-40),(-61,-40)).segment((-61,-39)).segment((-59,-39)).segment((-59,-40)).segment((93,-40)).segment((93,-27)).segment((100,-27)).segment((100,40)).segment((2,40)).segment((2,39)).segment((13,39)).segment((13,27)).segment((-6,27)).segment((-6,39)).segment((-31,39)).segment((-31,40)).segment((-100,40)).close().assemble().push([(-38,0)]).circle(17,mode='s').reset().face(w0.sketch().segment((-15,-40),(13,-40)).segment((13,-27)).segment((2,-27)).segment((2,-40)).close().assemble(),mode='s').finalize().extrude(-20)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0039_00398966.step')

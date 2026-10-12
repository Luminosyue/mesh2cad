import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,1))
r=w0.sketch().segment((-100,6),(-89,6)).segment((-93,-1)).segment((-82,-10)).segment((-98,-38)).segment((-68,-47)).segment((-58,-20)).segment((-51,-20)).segment((-51,-17)).segment((-29,-17)).segment((-29,-42)).segment((-12,-45)).segment((-10,-37)).segment((-10,-38)).segment((100,-39)).segment((100,43)).segment((28,45)).segment((27,20)).segment((10,20)).segment((10,42)).segment((-10,43)).segment((-10,40)).segment((-29,40)).segment((-29,37)).segment((-51,37)).segment((-51,45)).segment((-92,45)).segment((-92,24)).segment((-100,24)).close().assemble().push([(-49,0)]).circle(15,mode='s').push([(61,11)]).circle(17,mode='s').finalize().extrude(-2)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0082_00820772.step')

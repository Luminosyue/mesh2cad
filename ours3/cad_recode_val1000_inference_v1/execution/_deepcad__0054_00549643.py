import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,1))
r=w0.sketch().segment((-100,-4),(-97,-11)).segment((-77,-11)).segment((-77,-24)).segment((-90,-24)).segment((-89,-36)).segment((-80,-35)).segment((-72,-49)).segment((-51,-40)).segment((-56,-40)).segment((-56,-24)).segment((-43,-24)).segment((-43,-11)).segment((-56,-11)).segment((-56,2)).segment((-43,2)).segment((-43,11)).segment((-25,11)).segment((-25,4)).segment((1,14)).segment((1,10)).segment((11,10)).segment((11,-11)).segment((22,-11)).segment((22,-24)).segment((11,-24)).segment((11,-34)).segment((100,49)).segment((83,59)).segment((83,55)).segment((22,55)).segment((22,38)).segment((11,38)).segment((11,22)).segment((1,22)).segment((1,38)).segment((-1,38)).segment((-1,47)).segment((-11,47)).segment((-14,57)).segment((-58,47)).segment((-56,57)).segment((-88,40)).segment((-80,27)).segment((-83,27)).segment((-83,11)).segment((-77,11)).segment((-77,2)).close().assemble().finalize().extrude(-2)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0054_00549643.step')

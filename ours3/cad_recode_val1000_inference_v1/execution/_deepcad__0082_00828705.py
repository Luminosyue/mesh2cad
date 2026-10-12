import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-9))
r=w0.sketch().segment((-44,91),(-43,91)).segment((-43,-100)).segment((43,-100)).segment((43,-94)).segment((-40,-40)).segment((-4,14)).arc((-10,41),(18,48)).segment((20,50)).segment((43,13)).segment((43,100)).segment((-4,100)).segment((-4,73)).segment((-31,73)).segment((-31,100)).segment((-44,100)).close().assemble().finalize().extrude(18)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0082_00828705.step')

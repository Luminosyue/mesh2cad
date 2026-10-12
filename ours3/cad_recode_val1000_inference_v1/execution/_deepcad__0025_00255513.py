import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,24))
w1=cq.Workplane('XY',origin=(0,0,25))
r=w0.sketch().segment((10,1),(100,-1)).segment((100,61)).segment((10,61)).close().assemble().finalize().extrude(-36).union(w1.sketch().segment((-100,-61),(-47,-61)).arc((-29,-40),(-10,-61)).segment((100,-61)).segment((100,61)).segment((-100,61)).close().assemble().push([(-54,0)]).circle(12,mode='s').push([(26,36)]).circle(17,mode='s').finalize().extrude(-49))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0025_00255513.step')

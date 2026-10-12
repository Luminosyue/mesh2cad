import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-33))
r=w0.sketch().segment((-100,-45),(-87,-45)).segment((-87,-50)).segment((92,-50)).segment((92,-45)).segment((100,-45)).segment((100,45)).segment((92,45)).segment((92,50)).segment((-87,50)).segment((-87,45)).segment((-100,45)).close().assemble().push([(16,0)]).circle(32,mode='s').finalize().extrude(33).union(w0.sketch().segment((-100,-17),(-33,-17)).arc((-23,-16),(-13,-17)).segment((38,-17)).arc((33,-10),(28,-4)).segment((100,-4)).segment((100,50)).segment((-100,50)).close().assemble().finalize().extrude(66))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0026_00267232.step')

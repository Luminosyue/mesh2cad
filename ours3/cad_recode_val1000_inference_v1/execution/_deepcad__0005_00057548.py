import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-15))
r=w0.sketch().segment((-74,-100),(-1,-100)).segment((-1,-72)).segment((28,-72)).segment((28,-100)).segment((62,-100)).segment((62,56)).segment((-19,56)).segment((-19,25)).segment((-74,25)).close().assemble().push([(-46,-37)]).circle(17,mode='s').push([(21,-7)]).circle(21,mode='s').reset().face(w0.sketch().segment((-74,43),(-60,43)).segment((-60,56)).segment((-74,56)).segment((-74,50)).segment((-72,50)).segment((-72,48)).segment((-74,48)).close().assemble()).finalize().extrude(-30).union(w0.sketch().segment((-11,53),(-10,53)).arc((27,24),(65,53)).segment((66,53)).segment((66,65)).segment((65,65)).arc((27,100),(-10,65)).segment((-11,65)).close().assemble().finalize().extrude(30)).union(w0.workplane(offset=60/2).moveTo(60,64).cylinder(60,14))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0005_00057548.step')

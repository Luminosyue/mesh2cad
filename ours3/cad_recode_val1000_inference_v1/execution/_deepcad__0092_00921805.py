import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,37,0))
r=w0.workplane(offset=-83/2).moveTo(-82,-8).cylinder(83,12).union(w0.sketch().segment((-100,-12),(-98,-12)).arc((-82,-19),(-66,-12)).segment((32,-12)).segment((32,-10)).arc((60,-10),(74,12)).segment((74,-10)).segment((92,-10)).segment((92,-5)).segment((100,-5)).segment((100,20)).segment((74,20)).segment((74,11)).arc((56,21),(37,12)).segment((37,21)).segment((-100,20)).close().assemble().push([(85,5)]).circle(11,mode='s').finalize().extrude(9))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0092_00921805.step')

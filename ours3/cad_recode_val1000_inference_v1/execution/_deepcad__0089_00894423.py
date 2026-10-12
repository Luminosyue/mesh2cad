import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-4,0))
w1=cq.Workplane('XY',origin=(0,0,15))
r=w0.sketch().segment((-19,-93),(5,-95)).segment((7,-50)).segment((-16,-48)).close().assemble().reset().face(w0.sketch().segment((-19,-38),(6,-39)).segment((7,-13)).segment((-18,-11)).close().assemble()).reset().face(w0.sketch().segment((-14,24),(-13,11)).segment((6,11)).segment((6,25)).close().assemble()).finalize().extrude(3).union(w0.sketch().segment((-7,19),(-6,19)).segment((-6,-38)).segment((5,-38)).segment((5,-29)).segment((19,-29)).segment((19,-14)).arc((1,-10),(13,1)).arc((14,1),(15,2)).arc((16,10),(19,14)).segment((19,37)).segment((17,37)).segment((17,56)).segment((15,56)).segment((15,69)).segment((17,69)).segment((17,86)).segment((15,86)).segment((15,100)).segment((14,100)).segment((14,86)).segment((-6,86)).segment((-6,69)).segment((-7,69)).segment((-7,56)).segment((-6,56)).segment((-6,37)).segment((-7,37)).close().assemble().finalize().extrude(31)).union(w1.sketch().arc((-49,-23),(-38,-24),(-28,-27)).arc((-33,-14),(-28,-1)).arc((-42,-2),(-49,-15)).close().assemble().push([(63,-13)]).circle(13).finalize().extrude(3))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0089_00894423.step')

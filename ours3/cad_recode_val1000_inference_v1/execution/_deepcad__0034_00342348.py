import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-31,0))
r=w0.sketch().segment((-69,-68),(-33,-68)).segment((-33,-88)).segment((33,-88)).segment((33,-68)).segment((69,-68)).segment((69,-26)).segment((-20,-45)).segment((-28,-10)).segment((69,11)).segment((69,62)).segment((33,62)).segment((33,82)).segment((-33,82)).segment((-33,62)).segment((-69,62)).segment((-69,10)).segment((28,28)).segment((36,-10)).segment((-69,-28)).close().assemble().finalize().extrude(1).union(w0.sketch().segment((-70,-100),(69,-100)).segment((69,100)).segment((-69,100)).segment((-69,74)).segment((-70,74)).close().assemble().push([(20,-60)]).circle(3,mode='s').finalize().extrude(62))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0034_00342348.step')

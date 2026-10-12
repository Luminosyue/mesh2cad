import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-26,0))
w1=cq.Workplane('YZ',origin=(-20,0,0))
r=w0.sketch().push([(0,-21)]).circle(4).circle(2,mode='s').finalize().extrude(-72).union(w0.sketch().segment((-4,-19),(-2,-23)).segment((4,-21)).segment((2,-16)).close().assemble().finalize().extrude(126)).union(w1.workplane(offset=39/2).moveTo(-98,0).cylinder(39,2))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0027_00271500.step')

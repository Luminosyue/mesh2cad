import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,80,0))
r=w0.sketch().segment((-100,-100),(100,-100)).segment((100,100)).segment((70,100)).segment((70,97)).segment((67,97)).segment((67,100)).segment((-100,100)).close().assemble().push([(-95,-61)]).circle(5,mode='s').finalize().extrude(-160).union(w0.sketch().segment((-92,-50),(-38,-72)).segment((-38,-32)).segment((18,-32)).segment((18,-80)).segment((92,-80)).segment((92,14)).segment((28,14)).segment((38,40)).segment((-48,72)).close().assemble().finalize().extrude(-10))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0074_00749120.step')

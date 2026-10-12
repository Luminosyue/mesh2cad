import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-43,0))
w1=cq.Workplane('ZX',origin=(0,-36,0))
r=w0.sketch().segment((-72,-100),(-37,-100)).segment((-37,-90)).segment((-71,-90)).segment((-71,-43)).segment((-37,-43)).segment((-37,-40)).segment((14,-40)).segment((14,-43)).segment((48,-43)).segment((48,-90)).segment((14,-90)).segment((14,-100)).segment((15,-100)).segment((15,-43)).segment((69,-43)).segment((69,43)).segment((15,43)).segment((15,100)).segment((-72,100)).close().assemble().finalize().extrude(86).union(w1.sketch().segment((14,-29),(71,-29)).segment((71,43)).segment((14,43)).segment((14,39)).arc((-50,16),(14,-7)).close().assemble().push([(42,7)]).circle(20,mode='s').finalize().extrude(69))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0030_00307845.step')

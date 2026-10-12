import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(25,0,0))
w1=cq.Workplane('ZX',origin=(0,41,0))
r=w0.sketch().segment((-41,-64),(-35,-64)).segment((-35,-100)).segment((41,-100)).segment((41,-44)).segment((25,-44)).segment((25,-34)).segment((-41,-34)).close().assemble().reset().face(w0.sketch().segment((-41,0),(-15,0)).segment((-15,-1)).segment((-36,-1)).arc((-30,-11),(-21,-19)).arc((1,-35),(25,-23)).segment((25,-19)).arc((34,-11),(41,0)).segment((32,0)).segment((32,15)).segment((38,15)).arc((34,54),(3,77)).segment((3,82)).segment((-33,82)).segment((-33,77)).segment((-3,77)).arc((-32,64),(-41,35)).close().assemble()).push([(8,29)]).circle(16,mode='s').finalize().extrude(4).union(w0.workplane(offset=-7/2).moveTo(-0.5,96.5).box(69,7,7)).union(w1.sketch().segment((78,-29),(82,-29)).segment((82,-4)).segment((87,-4)).segment((87,6)).segment((82,6)).segment((82,24)).segment((78,24)).close().assemble().finalize().extrude(-82))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0006_00060356.step')

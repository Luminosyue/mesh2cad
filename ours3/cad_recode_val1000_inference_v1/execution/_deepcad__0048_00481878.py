import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-2))
r=w0.sketch().segment((-100,-19),(-73,-19)).segment((-73,-22)).segment((-99,-47)).segment((-68,-67)).segment((-45,-31)).segment((-50,-31)).segment((-50,-22)).segment((-32,-22)).segment((-32,-26)).segment((-29,-22)).segment((-29,-57)).segment((-7,-57)).segment((-7,-31)).segment((12,-31)).segment((12,-40)).segment((14,-40)).segment((14,-43)).segment((22,-43)).segment((22,-40)).segment((49,-40)).segment((49,-54)).segment((62,-54)).segment((62,-31)).segment((73,-31)).segment((73,-19)).segment((75,-19)).segment((75,-50)).segment((100,-50)).segment((100,42)).segment((93,42)).arc((64,55),(34,42)).segment((27,42)).segment((10,53)).segment((10,16)).segment((-6,16)).segment((-6,57)).segment((-100,57)).close().assemble().push([(-53,18)]).circle(8,mode='s').push([(64,11)]).circle(19,mode='s').finalize().extrude(4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0048_00481878.step')

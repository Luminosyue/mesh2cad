import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,12))
r=w0.sketch().segment((-74,47),(-60,47)).segment((-60,19)).segment((-22,19)).segment((-22,47)).segment((22,47)).segment((22,19)).segment((60,19)).segment((60,-19)).segment((22,-19)).segment((22,-47)).segment((-22,-47)).segment((-22,-19)).segment((-60,-19)).segment((-60,-47)).segment((-73,-47)).arc((10,-99),(85,-53)).segment((66,-53)).segment((66,-34)).segment((92,-34)).segment((92,-40)).arc((99,13),(80,60)).segment((80,62)).segment((78,62)).arc((66,75),(52,85)).segment((52,86)).segment((50,86)).arc((0,100),(-50,86)).segment((-52,86)).segment((-52,85)).arc((-70,53),(-74,13)).close().assemble().finalize().extrude(-46).union(w0.sketch().arc((-94,35),(-100,-2),(-93,-38)).segment((-93,-40)).segment((-92,-40)).arc((2,-100),(93,-35)).segment((94,-35)).segment((93,-34)).arc((100,2),(93,38)).segment((93,40)).segment((92,40)).arc((-2,100),(-93,35)).close().assemble().push([(-17,43)]).circle(29,mode='s').finalize().extrude(22))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0045_00455970.step')

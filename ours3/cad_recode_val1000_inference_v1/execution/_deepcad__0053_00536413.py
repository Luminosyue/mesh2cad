import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,4,0))
r=w0.sketch().segment((-100,23),(-93,23)).segment((-93,12)).segment((-73,12)).segment((-73,-1)).segment((-93,-1)).segment((-93,-100)).segment((-49,-100)).segment((-49,-51)).segment((-25,-51)).arc((-20,-44),(-13,-38)).segment((-13,-100)).segment((94,-100)).segment((94,-51)).segment((100,-51)).segment((100,44)).segment((94,44)).segment((94,53)).segment((69,53)).segment((84,72)).segment((69,86)).segment((69,53)).segment((34,53)).segment((34,93)).segment((77,93)).segment((69,100)).segment((54,100)).segment((54,93)).segment((34,93)).segment((34,82)).segment((0,82)).segment((0,100)).segment((-98,100)).segment((-98,53)).segment((-100,53)).close().assemble().push([(-52,31)]).circle(18,mode='s').reset().face(w0.sketch().arc((-13,12),(19,-28),(69,-14)).segment((69,34)).arc((28,3),(0,44)).segment((-13,44)).close().assemble(),mode='s').push([(-52,31)]).circle(15).finalize().extrude(-8)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0053_00536413.step')

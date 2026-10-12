import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-9))
r=w0.sketch().segment((-97,-17),(-97,17)).arc((-100,0),(-97,-17)).assemble().reset().face(w0.sketch().arc((-97,-19),(-86,-46),(-70,-71)).segment((-70,-72)).segment((-69,-72)).arc((-60,-78),(-51,-84)).segment((-51,-85)).segment((-50,-84)).arc((-27,-94),(-3,-96)).segment((-3,-91)).arc((-89,14),(33,84)).segment((33,94)).arc((20,96),(7,99)).segment((6,98)).arc((-66,64),(-96,-18)).close().assemble()).reset().face(w0.sketch().arc((-3,-96),(36,-93),(69,-68)).segment((72,-68)).segment((72,-65)).arc((98,-11),(80,51)).segment((80,52)).segment((79,52)).arc((75,58),(72,65)).segment((72,69)).segment((70,69)).arc((59,79),(46,87)).segment((46,77)).arc((89,-12),(33,-84)).segment((33,-86)).segment((29,-86)).arc((14,-90),(-3,-91)).close().assemble()).finalize().extrude(18)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0054_00540823.step')

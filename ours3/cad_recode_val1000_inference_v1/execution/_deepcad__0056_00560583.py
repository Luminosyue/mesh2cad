import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,15))
r=w0.sketch().arc((-99,-12),(-91,-41),(-71,-69)).segment((-71,-71)).segment((-69,-71)).arc((0,-100),(69,-71)).segment((71,-71)).segment((71,-69)).arc((86,-50),(95,-31)).segment((56,-31)).arc((54,-35),(51,-38)).segment((51,-41)).segment((49,-41)).arc((0,-69),(-49,-41)).segment((-51,-41)).segment((-51,-38)).arc((-54,-35),(-56,-31)).segment((-94,-31)).arc((-89,-23),(-81,-17)).arc((-29,-4),(22,-24)).arc((23,-23),(23,-21)).segment((23,-18)).segment((25,-18)).arc((44,21),(71,-14)).segment((95,-14)).arc((86,12),(71,31)).segment((71,33)).segment((69,33)).arc((67,35),(65,37)).arc((72,54),(75,71)).arc((65,67),(56,63)).arc((-1,100),(-69,63)).arc((-94,34),(-99,-4)).arc((-100,-8),(-99,-12)).assemble().reset().face(w0.sketch().arc((-71,59),(-62,67),(-51,71)).segment((-51,73)).segment((-71,73)).close().assemble()).finalize().extrude(-30)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0056_00560583.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,2,0))
r=w0.sketch().segment((-100,31),(-89,-10)).segment((-95,-10)).segment((-95,-21)).segment((-92,-21)).segment((-89,-43)).segment((-33,-38)).segment((-33,-31)).segment((-31,-31)).segment((-31,-14)).segment((-24,-14)).segment((-24,-10)).segment((-31,-10)).segment((-31,10)).segment((-33,10)).segment((-33,16)).segment((-44,16)).segment((-44,31)).segment((-33,31)).segment((-33,40)).segment((-87,43)).segment((-88,34)).close().assemble().reset().face(w0.sketch().segment((-24,1),(-12,1)).segment((-12,-31)).segment((-11,-31)).segment((-11,-34)).segment((-12,-34)).segment((-12,-36)).segment((15,-43)).segment((15,-34)).segment((17,-34)).arc((57,-43),(92,-24)).segment((100,-25)).segment((100,30)).segment((93,31)).segment((94,40)).segment((75,43)).segment((74,35)).arc((50,40),(28,33)).segment((16,34)).segment((16,43)).segment((-24,43)).close().assemble()).push([(57,-7)]).circle(22,mode='s').finalize().extrude(-4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0032_00322057.step')

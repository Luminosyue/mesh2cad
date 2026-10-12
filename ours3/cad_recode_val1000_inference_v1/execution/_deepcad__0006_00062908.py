import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,94,0))
w1=cq.Workplane('ZX',origin=(0,100,0))
r=w0.sketch().arc((-16,-18),(-10,-22),(-5,-26)).arc((-1,-25),(2,-24)).arc((-10,-22),(-16,-14)).close().assemble().reset().face(w0.sketch().arc((-2,24),(10,22),(16,14)).segment((16,22)).arc((1,26),(-2,4)).close().assemble()).finalize().extrude(-194).union(w0.sketch().push([(0,-1)]).circle(26).circle(24,mode='s').finalize().extrude(-161)).union(w1.sketch().arc((-23,-14),(-22,-15),(-22,-16)).arc((-20,-17),(-19,-18)).arc((-18,-16),(-17,-14)).arc((-20,-13),(-23,-14)).assemble().reset().face(w1.sketch().arc((-23,14),(-20,15),(-17,14)).arc((-20,18),(-23,14)).assemble()).reset().face(w1.sketch().arc((17,-14),(20,-10),(23,-7)).arc((23,-5),(24,-4)).arc((25,1),(26,6)).arc((22,5),(17,5)).close().assemble()).finalize().extrude(-196))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0006_00062908.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(4,0,0))
r=w0.sketch().segment((-100,-4),(-97,-4)).segment((-97,-18)).segment((-88,-18)).segment((-88,-27)).segment((-29,-27)).segment((-29,-18)).segment((-20,-18)).segment((-20,-27)).segment((17,-27)).segment((17,-18)).segment((26,-18)).segment((26,-25)).segment((38,-25)).segment((38,-27)).segment((57,-27)).segment((57,-25)).segment((70,-25)).segment((70,-18)).segment((73,-18)).segment((73,-27)).segment((100,-27)).segment((100,24)).segment((92,24)).segment((92,27)).segment((70,27)).segment((70,24)).segment((57,24)).segment((57,25)).segment((38,25)).segment((38,24)).segment((26,24)).segment((26,19)).segment((17,19)).segment((17,24)).segment((-20,24)).segment((-20,19)).segment((-29,19)).segment((-29,27)).segment((-39,27)).arc((-40,22),(-41,19)).segment((-50,19)).arc((-53,22),(-54,27)).segment((-88,27)).segment((-88,19)).segment((-100,19)).close().assemble().push([(-67,-10)]).rect(32,16,mode='s').push([(49,-10)]).rect(32,16,mode='s').finalize().extrude(-8)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0065_00655793.step')

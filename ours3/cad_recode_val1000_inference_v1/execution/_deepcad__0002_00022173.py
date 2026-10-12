import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,20,0))
r=w0.sketch().segment((-100,-13),(-99,-13)).arc((-83,-59),(-41,-85)).segment((-41,-90)).segment((-26,-90)).segment((-26,-99)).segment((21,-99)).segment((21,-97)).arc((69,-70),(99,-18)).segment((100,-18)).segment((100,-13)).segment((99,-13)).arc((96,25),(79,60)).segment((79,61)).segment((78,61)).arc((31,94),(-26,94)).segment((-26,95)).segment((-51,95)).segment((-51,86)).arc((-78,64),(-97,33)).segment((-98,33)).segment((-98,28)).arc((-100,8),(-100,-12)).close().assemble().reset().face(w0.sketch().arc((-51,-31),(49,-25),(-18,46)).segment((-18,61)).segment((-51,61)).segment((-51,44)).arc((-55,16),(-51,-12)).close().assemble(),mode='s').finalize().extrude(-40).union(w0.sketch().segment((-91,-42),(-45,-93)).segment((-13,-63)).arc((-49,-49),(-64,-14)).close().assemble().finalize().extrude(-30))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0002_00022173.step')

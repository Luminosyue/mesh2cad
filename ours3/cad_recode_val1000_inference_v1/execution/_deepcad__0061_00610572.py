import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,2,0))
r=w0.sketch().segment((-47,23),(-41,23)).segment((-41,12)).segment((-38,12)).segment((-46,-12)).segment((-41,-14)).segment((-41,-69)).segment((-43,-69)).segment((-43,-97)).segment((-41,-97)).segment((-41,-100)).segment((13,-100)).segment((13,-97)).segment((47,-97)).segment((47,-69)).segment((44,-69)).segment((44,-42)).segment((47,-46)).segment((47,-39)).segment((44,-39)).segment((44,-27)).segment((27,-27)).segment((27,-14)).segment((35,-14)).segment((35,12)).segment((47,12)).segment((47,39)).segment((44,39)).segment((44,50)).segment((47,50)).segment((47,74)).segment((44,74)).segment((44,94)).segment((35,94)).segment((35,100)).segment((-16,100)).segment((-16,94)).segment((-41,94)).segment((-41,74)).segment((-47,74)).segment((-47,40)).arc((-48,32),(-47,24)).close().assemble().push([(-5,56)]).circle(17,mode='s').push([(-16,-14)]).circle(18,mode='s').push([(18,-43)]).circle(24,mode='s').finalize().extrude(-3)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0061_00610572.step')

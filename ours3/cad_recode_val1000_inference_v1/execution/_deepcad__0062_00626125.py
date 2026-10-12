import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.sketch().arc((-95,-31),(79,61),(-73,-68)).segment((19,-68)).segment((19,5)).segment((-95,5)).close().assemble().finalize().extrude(195).union(w0.sketch().arc((-72,-69),(-10,100),(72,-60)).segment((72,13)).segment((-72,13)).close().assemble().finalize().extrude(200))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0062_00626125.step')

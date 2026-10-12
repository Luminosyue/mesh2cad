import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,25,0))
r=w0.sketch().segment((-50,-100),(15,-100)).segment((15,-93)).arc((-29,-50),(15,-7)).segment((15,3)).segment((44,3)).segment((44,100)).segment((-44,100)).segment((-44,92)).segment((-50,92)).close().assemble().push([(0,49)]).circle(20,mode='s').finalize().extrude(-50).union(w0.sketch().segment((-50,-68),(-40,-68)).segment((-50,-53)).close().assemble().reset().face(w0.sketch().segment((-50,-35),(15,72)).segment((50,51)).segment((50,85)).segment((-50,85)).close().assemble()).reset().face(w0.sketch().segment((-15,-100),(50,-100)).segment((50,-73)).close().assemble()).reset().face(w0.sketch().segment((50,-57),(50,-12)).arc((43,-34),(50,-57)).assemble()).finalize().extrude(-33))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0065_00659711.step')

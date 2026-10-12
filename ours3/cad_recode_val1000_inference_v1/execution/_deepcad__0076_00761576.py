import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-29,0))
w1=cq.Workplane('ZX',origin=(0,-26,0))
r=w0.sketch().segment((-74,-9),(-69,-9)).segment((-69,-2)).segment((24,-2)).segment((24,-9)).segment((31,-9)).segment((31,-2)).segment((61,-2)).segment((61,-9)).segment((69,-9)).segment((69,2)).segment((31,2)).segment((31,18)).segment((24,18)).segment((24,11)).segment((-69,11)).segment((-69,2)).segment((-74,2)).close().assemble().finalize().extrude(54).union(w1.sketch().segment((-72,-100),(74,-100)).segment((74,-96)).segment((-29,-96)).segment((-29,-53)).segment((74,-53)).segment((74,-49)).segment((64,-49)).segment((64,-36)).arc((49,-42),(33,-43)).arc((38,-37),(42,-31)).arc((52,-42),(64,-49)).segment((64,-41)).arc((19,38),(64,97)).segment((64,100)).segment((19,100)).segment((19,96)).segment((-11,96)).segment((-11,77)).arc((-29,61),(-39,40)).arc((-55,52),(-72,60)).segment((-72,49)).segment((19,49)).segment((19,2)).segment((-72,2)).close().assemble().push([(-15,-25.5)]).rect(100,47,mode='s').finalize().extrude(56))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0076_00761576.step')

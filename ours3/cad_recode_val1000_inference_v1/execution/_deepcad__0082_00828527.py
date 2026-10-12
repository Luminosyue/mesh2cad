import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-83,0))
r=w0.sketch().arc((-87,-68),(-72,-32),(-87,4)).close().assemble().reset().face(w0.sketch().segment((-87,38),(-57,38)).arc((0,91),(57,38)).segment((87,38)).segment((87,100)).segment((-87,100)).close().assemble()).reset().face(w0.sketch().segment((-61,-100),(87,-100)).segment((87,-88)).arc((13,-93),(-61,-68)).close().assemble()).finalize().extrude(166)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0082_00828527.step')

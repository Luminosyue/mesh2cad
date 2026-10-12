import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,52))
r=w0.sketch().segment((-100,-100),(-61,-100)).segment((-100,-58)).close().assemble().reset().face(w0.sketch().segment((-100,-39),(-24,100)).segment((-100,100)).close().assemble()).reset().face(w0.sketch().segment((-34,-100),(100,-100)).segment((100,100)).segment((61,100)).segment((100,58)).close().assemble()).reset().face(w0.sketch().segment((10,100),(100,58)).segment((100,100)).close().assemble()).finalize().extrude(-104)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0049_00491773.step')

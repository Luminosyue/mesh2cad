import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-13))
w1=cq.Workplane('ZX',origin=(0,52,0))
r=w0.sketch().segment((-88,-52),(-43,-52)).segment((-43,-53)).segment((-41,-52)).segment((88,-52)).segment((88,36)).segment((43,36)).segment((43,37)).segment((41,36)).segment((-88,36)).close().assemble().push([(0,-10)]).circle(22,mode='s').finalize().extrude(26).union(w0.sketch().arc((-96,52),(-63,37),(-30,52)).segment((-49,52)).arc((-63,47),(-77,52)).close().assemble().reset().face(w0.sketch().segment((-26,35),(88,35)).arc((31,52),(-26,35)).assemble()).finalize().extrude(26)).union(w1.sketch().arc((-10,-5),(1,-23),(13,-4)).arc((1,-10),(-10,-5)).assemble().finalize().extrude(-104))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0010_00104630.step')

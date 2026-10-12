import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,23))
r=w0.sketch().segment((-100,-50),(-52,-50)).segment((-100,-1)).close().assemble().reset().face(w0.sketch().segment((-100,1),(-50,50)).segment((-100,50)).close().assemble()).reset().face(w0.sketch().segment((-49,-50),(100,-50)).segment((100,50)).segment((52,50)).segment((10,50)).segment((10,40)).segment((-4,40)).segment((-4,50)).segment((-49,50)).segment((-49,40)).segment((-4,40)).segment((-4,30)).segment((10,30)).segment((10,13)).segment((36,13)).segment((36,-13)).segment((10,-13)).segment((10,-30)).segment((-4,-30)).segment((-4,-47)).segment((-49,-47)).close().assemble()).reset().face(w0.sketch().segment((73,-50),(100,-50)).segment((100,-30)).segment((100,30)).segment((100,50)).segment((73,50)).close().assemble()).finalize().extrude(-46)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0012_00128119.step')

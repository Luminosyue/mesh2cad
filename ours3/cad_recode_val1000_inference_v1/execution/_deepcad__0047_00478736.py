import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,64,0))
r=w0.sketch().segment((-100,-64),(100,-64)).segment((100,64)).segment((59,64)).arc((1,-18),(-57,64)).segment((-100,64)).close().assemble().finalize().extrude(-128).union(w0.sketch().segment((-92,-30),(-40,-30)).segment((-40,-45)).segment((-27,-45)).segment((-27,-30)).segment((27,-30)).segment((27,-64)).segment((92,-64)).segment((92,64)).segment((-27,64)).segment((-27,65)).segment((-40,65)).segment((-40,64)).segment((-92,64)).close().assemble().finalize().extrude(-12))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0047_00478736.step')

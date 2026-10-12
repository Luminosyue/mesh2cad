import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,24,0))
r=w0.sketch().segment((-24,-100),(24,-100)).segment((24,29)).segment((-24,-30)).close().assemble().reset().face(w0.sketch().segment((-24,-29),(24,30)).segment((24,100)).segment((-24,100)).close().assemble()).finalize().extrude(-48)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0055_00552855.step')

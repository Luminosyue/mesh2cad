import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-67,0))
r=w0.sketch().arc((-100,-100),(-52,-75),(-6,-100)).segment((78,-100)).segment((78,-55)).segment((100,-55)).segment((100,100)).segment((-100,100)).close().assemble().finalize().extrude(134).union(w0.sketch().segment((-92,-46),(-33,-46)).arc((0,-55),(33,-46)).segment((92,-46)).segment((92,46)).segment((33,46)).arc((0,55),(-33,46)).segment((-92,46)).close().assemble().circle(37,mode='s').finalize().extrude(134))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0077_00771853.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-3))
r=w0.workplane(offset=4/2).box(18,80,4).union(w0.sketch().segment((-9,-96),(5,-100)).segment((9,-85)).segment((9,-62)).arc((-4,-34),(8,-6)).segment((9,10)).segment((1,10)).segment((1,81)).segment((9,81)).segment((9,95)).segment((-1,98)).segment((-5,100)).segment((-9,94)).segment((-9,81)).segment((-1,81)).segment((-1,83)).segment((1,83)).segment((1,10)).segment((-7,10)).segment((-7,-6)).arc((-4,-79),(-9,-62)).close().assemble().finalize().extrude(6))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0091_00910094.step')

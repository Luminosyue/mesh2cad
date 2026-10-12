import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,30))
w1=cq.Workplane('ZX',origin=(0,-55,0))
r=w0.sketch().push([(-96.5,18)]).rect(7,90).push([(-96,18)]).circle(2,mode='s').reset().face(w0.sketch().segment((-93,-57),(-78,-57)).segment((-78,-62)).segment((-45,-62)).segment((-45,-57)).segment((-29,-57)).segment((-29,-55)).segment((-93,-55)).close().assemble()).reset().face(w0.sketch().segment((-93,55),(-29,55)).segment((-29,57)).segment((-45,57)).segment((-45,62)).segment((-78,62)).segment((-78,57)).segment((-93,57)).close().assemble()).reset().face(w0.sketch().segment((-45,55),(93,55)).segment((93,-55)).segment((29,-55)).segment((29,-57)).segment((100,-57)).segment((100,57)).segment((93,57)).segment((93,62)).segment((75,62)).segment((75,57)).segment((30,57)).segment((30,62)).segment((-45,62)).close().assemble()).finalize().extrude(-60).union(w1.sketch().arc((-31,-16),(31,32),(-31,81)).close().assemble().finalize().extrude(-7))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0024_00241848.step')

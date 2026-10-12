import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
w1=cq.Workplane('ZX',origin=(0,58,0))
r=w0.sketch().segment((-100,-1),(-86,-39)).segment((-19,-17)).segment((-19,-78)).segment((19,-78)).segment((19,-10)).segment((100,1)).segment((86,39)).segment((19,17)).segment((19,78)).segment((-19,78)).segment((-19,10)).close().assemble().finalize().extrude(30).union(w0.sketch().segment((-60,-80),(-11,-80)).arc((-39,0),(-11,80)).segment((-60,80)).close().assemble().reset().face(w0.sketch().segment((11,-80),(100,-80)).segment((100,80)).segment((11,80)).arc((39,0),(11,-80)).assemble()).finalize().extrude(200)).union(w1.sketch().arc((-60,-61),(-27,-2),(10,45)).arc((-1,55),(-13,67)).arc((-34,71),(-55,68)).arc((-53,44),(-60,21)).close().assemble().finalize().extrude(-96))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0091_00912917.step')

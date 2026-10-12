import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,27,0))
w1=cq.Workplane('ZX',origin=(0,16,0))
r=w0.sketch().segment((-24,100),(-23,20)).segment((-23,-87)).segment((24,-87)).segment((23,100)).segment((14,100)).arc((12,96),(10,92)).segment((10,84)).segment((9,84)).arc((-1,17),(-9,84)).segment((-9,92)).arc((-11,96),(-13,100)).close().assemble().reset().face(w0.sketch().segment((-24,-29),(0,-41)).segment((4,21)).segment((-23,23)).close().assemble()).finalize().extrude(-54).union(w0.sketch().segment((-20,-100),(13,-100)).segment((13,-96)).segment((23,-96)).segment((23,-12)).segment((13,-12)).segment((13,22)).segment((-20,22)).segment((-20,-47)).arc((-16,-74),(-20,-100)).assemble().push([(2,-56)]).circle(36,mode='s').finalize().extrude(-40)).union(w1.sketch().arc((-10,71),(1,33),(7,71)).arc((-1,70),(-10,71)).assemble().finalize().extrude(-36))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0019_00198387.step')

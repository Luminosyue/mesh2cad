import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-20,0))
r=w0.sketch().segment((-60,-100),(56,-100)).segment((56,-90)).arc((25,-94),(0,-77)).segment((-14,-77)).segment((-14,-56)).arc((-42,-35),(-56,-5)).segment((-60,-5)).close().assemble().reset().face(w0.sketch().segment((-60,-2),(-56,-2)).arc((-36,15),(-11,20)).segment((-11,0)).arc((3,31),(35,49)).segment((35,60)).arc((48,44),(60,26)).segment((60,93)).segment((41,93)).segment((41,100)).segment((-60,100)).close().assemble()).reset().face(w0.sketch().segment((-15,-77),(25,-77)).segment((25,-37)).segment((3,-37)).arc((1,-38),(-1,-38)).arc((-8,-58),(-15,-77)).assemble()).reset().face(w0.sketch().arc((60,-43),(61,-41),(60,-39)).close().assemble()).finalize().extrude(40)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0043_00434931.step')

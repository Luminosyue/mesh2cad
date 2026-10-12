import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,48))
r=w0.sketch().arc((-43,90),(-99,-13),(-17,-98)).segment((-17,-99)).segment((-13,-99)).arc((13,-99),(38,-92)).segment((42,-92)).segment((42,-91)).arc((99,-13),(53,74)).segment((53,85)).segment((49,85)).arc((46,87),(42,89)).segment((42,90)).segment((38,90)).arc((1,100),(-36,93)).segment((-43,93)).close().assemble().push([(1,26)]).circle(63,mode='s').finalize().extrude(-96).union(w0.sketch().segment((-83,-32),(-83,56)).arc((-100,1),(-83,-32)).assemble().reset().face(w0.sketch().arc((75,-32),(92,1),(83,37)).segment((83,56)).segment((75,56)).close().assemble()).finalize().extrude(-10))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0045_00455960.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,34,0))
r=w0.sketch().segment((-25,-100),(-7,-100)).segment((-7,-77)).segment((-25,-60)).close().assemble().reset().face(w0.sketch().segment((-25,-56),(-7,-69)).segment((-7,-9)).segment((-25,2)).close().assemble()).reset().face(w0.sketch().segment((-26,43),(-13,12)).segment((16,77)).segment((0,85)).segment((0,84)).segment((0,82)).segment((0,79)).segment((0,77)).segment((-1,77)).segment((-1,79)).segment((-1,81)).segment((-1,83)).close().assemble()).finalize().extrude(-68).union(w0.sketch().segment((-25,22),(-25,56)).arc((-27,39),(-25,22)).assemble().reset().face(w0.sketch().segment((-1,83),(1,83)).segment((1,81)).segment((23,81)).segment((23,92)).segment((25,90)).segment((25,91)).segment((23,91)).segment((23,94)).segment((1,94)).segment((1,83)).close().assemble()).finalize().extrude(-49))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0064_00648285.step')

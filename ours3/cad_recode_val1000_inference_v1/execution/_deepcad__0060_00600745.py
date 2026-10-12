import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-51,0))
r=w0.sketch().segment((-100,-62),(100,-62)).segment((100,62)).segment((51,62)).arc((29,39),(12,62)).segment((-100,62)).close().assemble().finalize().extrude(89).union(w0.sketch().segment((-88,-58),(88,-58)).segment((88,58)).segment((62,58)).arc((19,-10),(-53,23)).arc((-71,23),(-88,30)).close().assemble().finalize().extrude(102))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0060_00600745.step')

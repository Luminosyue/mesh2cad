import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-50,0))
r=w0.sketch().segment((-34,-92),(34,-92)).segment((34,-43)).arc((30,-42),(34,-41)).segment((34,-29)).segment((33,-29)).segment((33,-27)).segment((34,-27)).segment((34,33)).segment((0,33)).segment((0,67)).segment((34,67)).segment((34,100)).segment((-34,100)).segment((-34,91)).segment((-33,91)).segment((-33,63)).segment((-34,63)).segment((-34,-27)).segment((-33,-27)).segment((-33,-29)).segment((-34,-29)).close().assemble().finalize().extrude(90).union(w0.sketch().segment((-33,-100),(33,-100)).segment((33,-83)).arc((0,-93),(-33,-83)).close().assemble().reset().face(w0.sketch().arc((-33,-43),(0,-33),(33,-43)).segment((33,-29)).segment((-33,-29)).close().assemble()).reset().face(w0.sketch().segment((-20,33),(20,33)).arc((0,38),(-20,33)).assemble()).finalize().extrude(100))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0080_00808680.step')

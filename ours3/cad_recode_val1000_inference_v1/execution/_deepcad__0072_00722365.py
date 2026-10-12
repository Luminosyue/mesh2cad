import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,0,0))
w1=cq.Workplane('XY',origin=(0,0,-28))
r=w0.sketch().segment((-28,34),(28,34)).segment((28,83)).segment((16,83)).segment((23,91)).segment((-6,100)).segment((-13,83)).segment((-28,83)).close().assemble().finalize().extrude(-14).union(w1.sketch().segment((-100,-25),(-77,-25)).arc((-56,-11),(-34,-25)).segment((33,-25)).segment((33,-14)).segment((83,-14)).segment((83,0)).segment((33,0)).segment((33,25)).segment((-100,25)).close().assemble().finalize().extrude(56))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0072_00722365.step')

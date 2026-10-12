import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-12))
r=w0.sketch().segment((-21,-28),(-18,-47)).arc((-12,-54),(-13,-64)).segment((-2,-96)).segment((1,-100)).segment((19,-42)).arc((21,-24),(22,-6)).segment((21,28)).segment((20,28)).segment((1,98)).segment((-4,97)).segment((-4,91)).segment((-5,91)).segment((-5,87)).segment((-7,87)).segment((-7,82)).segment((-14,62)).arc((-19,39),(-21,17)).arc((-22,-5),(-19,-27)).close().assemble().finalize().extrude(24)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0081_00812569.step')

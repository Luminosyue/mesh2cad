import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,88,0))
w1=cq.Workplane('XY',origin=(0,0,-42))
r=w0.sketch().segment((-67,-100),(1,-100)).segment((1,-92)).arc((-12,-85),(-22,-75)).segment((1,-60)).segment((1,-67)).arc((3,-65),(5,-62)).segment((5,-74)).segment((67,-92)).segment((67,82)).segment((5,100)).segment((5,77)).arc((35,20),(-22,50)).segment((-67,50)).close().assemble().finalize().extrude(-26).union(w1.sketch().segment((-100,-88),(-55,-88)).arc((-24,-74),(11,-88)).segment((100,-88)).segment((100,68)).segment((51,68)).arc((1,-1),(-53,68)).segment((-100,68)).close().assemble().finalize().extrude(-25))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0001_00014203.step')

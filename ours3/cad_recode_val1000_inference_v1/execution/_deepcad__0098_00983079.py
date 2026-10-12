import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,45))
r=w0.sketch().segment((-55,-100),(55,-100)).segment((55,100)).segment((-55,100)).segment((-55,65)).arc((-52,64),(-55,63)).close().assemble().push([(10,-7)]).circle(28,mode='s').finalize().extrude(-90).union(w0.sketch().segment((-55,-85),(55,-85)).segment((55,41)).segment((-55,-6)).close().assemble().finalize().extrude(-80))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0098_00983079.step')

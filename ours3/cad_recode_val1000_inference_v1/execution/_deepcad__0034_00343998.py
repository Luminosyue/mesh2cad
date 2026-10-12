import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-85))
w1=cq.Workplane('XY',origin=(0,0,-36))
r=w0.sketch().segment((-100,19),(-96,18)).arc((-88,-45),(-37,-85)).segment((-37,-94)).segment((-24,-94)).segment((-24,-95)).segment((24,-95)).segment((24,-94)).segment((37,-94)).segment((37,-85)).arc((48,-85),(59,-82)).segment((63,-83)).segment((65,-76)).arc((85,-50),(96,-19)).segment((100,-19)).segment((96,-18)).arc((88,45),(37,85)).segment((37,94)).segment((24,94)).segment((24,95)).segment((-24,95)).segment((-24,94)).segment((-37,94)).segment((-37,85)).arc((-48,85),(-59,82)).segment((-63,83)).segment((-65,76)).arc((-85,50),(-96,19)).close().assemble().circle(55,mode='s').finalize().extrude(170).union(w1.sketch().arc((-47,-27),(1,-55),(52,-35)).segment((42,-35)).arc((-53,0),(42,35)).segment((52,35)).arc((1,55),(-47,35)).segment((-37,35)).arc((-54,0),(-37,-27)).close().assemble().finalize().extrude(69))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0034_00343998.step')

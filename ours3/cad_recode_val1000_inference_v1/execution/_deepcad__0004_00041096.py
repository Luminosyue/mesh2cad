import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,9))
r=w0.sketch().segment((-100,-100),(-52,-100)).segment((-52,-97)).segment((-66,-97)).segment((-66,-67)).segment((-74,-67)).segment((-74,-54)).segment((-66,-54)).segment((-66,-51)).segment((-52,-51)).segment((-52,-35)).segment((-10,-54)).segment((-7,-54)).segment((-7,-67)).segment((1,-67)).segment((1,-70)).segment((18,-70)).segment((18,-100)).segment((19,-100)).segment((19,-38)).segment((41,-38)).segment((41,-100)).segment((100,-100)).segment((100,100)).segment((1,100)).segment((1,80)).segment((-19,91)).segment((-48,42)).segment((-48,100)).segment((-100,100)).close().assemble().reset().face(w0.sketch().segment((-66,-29),(-10,20)).segment((-66,53)).close().assemble(),mode='s').push([(30,56)]).circle(16,mode='s').finalize().extrude(-18)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0004_00041096.step')

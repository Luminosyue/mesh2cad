import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
w1=cq.Workplane('XY',origin=(0,0,47))
r=w0.sketch().arc((-19,0),(18,-5),(-14,13)).arc((-10,6),(-19,0)).assemble().push([(0,-1)]).circle(13,mode='s').finalize().extrude(-44).union(w1.sketch().arc((-19,0),(-12,-1),(-15,-11)).arc((-13,-14),(-10,-16)).arc((12,5),(-15,-11)).arc((-17,-6),(-19,0)).assemble().finalize().extrude(-147))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0038_00380675.step')

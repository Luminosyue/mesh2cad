import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,70,0))
r=w0.sketch().segment((-70,-100),(70,-100)).segment((70,100)).segment((-37,100)).arc((-17,8),(-70,-62)).close().assemble().finalize().extrude(-140).union(w0.sketch().segment((-70,-83),(-17,-83)).segment((-17,-35)).arc((50,19),(-17,73)).segment((-17,100)).segment((-70,100)).close().assemble().push([(16,19)]).circle(20,mode='s').finalize().extrude(-140))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0049_00498114.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(17,0,0))
r=w0.sketch().segment((-17,-100),(10,-100)).segment((10,-93)).segment((17,-93)).segment((17,100)).segment((-17,100)).segment((-17,53)).arc((-15,52),(-17,51)).close().assemble().push([(13,-72)]).circle(3,mode='s').finalize().extrude(-34)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0055_00558458.step')

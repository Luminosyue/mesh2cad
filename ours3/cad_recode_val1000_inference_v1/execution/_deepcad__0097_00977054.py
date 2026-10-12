import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-1))
r=w0.sketch().segment((-22,46),(-21,14)).segment((-21,13)).segment((-15,-18)).segment((-15,-19)).segment((-14,-19)).segment((-13,-21)).segment((-13,-47)).arc((-19,-92),(22,-86)).segment((21,-86)).segment((21,-68)).arc((19,-50),(7,-36)).segment((22,-13)).segment((21,-13)).segment((15,18)).segment((15,19)).segment((14,19)).segment((13,21)).segment((13,48)).arc((19,44),(21,38)).segment((21,46)).segment((19,46)).segment((19,68)).segment((22,68)).segment((21,90)).segment((21,91)).segment((15,100)).segment((-15,91)).segment((-15,87)).segment((-22,73)).segment((-21,73)).segment((-21,50)).segment((-17,50)).segment((-17,46)).close().assemble().finalize().extrude(2)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0097_00977054.step')

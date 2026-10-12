import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,1))
r=w0.sketch().segment((-100,24),(-97,-22)).segment((-32,-20)).segment((-32,-23)).segment((-12,-25)).segment((-12,-20)).segment((100,-21)).segment((100,24)).segment((5,22)).segment((10,15)).segment((-12,15)).segment((-12,18)).segment((-32,20)).segment((-32,18)).segment((-68,20)).segment((-68,22)).segment((-61,22)).segment((-61,24)).segment((-68,24)).segment((-68,22)).close().assemble().push([(53,1)]).circle(10,mode='s').finalize().extrude(-2)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0021_00212206.step')

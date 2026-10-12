import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(-100,0,0))
w1=cq.Workplane('XY',origin=(0,0,0))
r=w0.sketch().segment((-67,24),(-48,24)).segment((-48,-67)).segment((48,-67)).segment((48,24)).segment((62,24)).segment((62,67)).segment((-67,67)).close().assemble().finalize().extrude(33).union(w1.sketch().segment((-100,-46),(-90,-46)).segment((-90,-67)).segment((100,-67)).segment((100,67)).segment((-90,67)).segment((-90,62)).segment((-100,62)).close().assemble().push([(25,10)]).circle(36,mode='s').finalize().extrude(-67))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0010_00102026.step')

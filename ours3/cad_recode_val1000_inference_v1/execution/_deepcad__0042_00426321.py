import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,1))
r=w0.sketch().segment((-100,0),(-97,-25)).segment((-86,-24)).segment((-86,-27)).segment((-68,-28)).segment((-68,-24)).segment((-56,-23)).segment((-56,-11)).segment((-29,-14)).segment((-29,-28)).segment((-7,-28)).segment((-7,-20)).segment((23,-22)).segment((24,-19)).segment((24,-29)).segment((62,-29)).segment((62,-16)).segment((100,-16)).segment((100,29)).segment((34,29)).segment((34,25)).segment((-7,25)).segment((-7,26)).segment((-29,26)).segment((-29,21)).segment((-57,22)).segment((-57,28)).segment((-79,28)).segment((-79,27)).segment((-99,29)).segment((-100,11)).segment((-79,11)).segment((-79,9)).segment((-57,9)).segment((-57,11)).segment((-29,11)).segment((-29,7)).segment((-57,7)).segment((-57,6)).segment((-79,6)).segment((-79,7)).segment((-100,7)).close().assemble().push([(62,6)]).circle(12,mode='s').finalize().extrude(-2)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0042_00426321.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,6))
r=w0.sketch().segment((-42,-100),(28,-100)).segment((28,-97)).segment((42,-97)).segment((42,12)).segment((37,12)).segment((37,29)).segment((42,29)).segment((42,100)).segment((-42,100)).segment((-42,57)).segment((-35,57)).segment((-35,29)).segment((-42,29)).segment((-42,12)).segment((-35,12)).segment((-35,11)).segment((-29,11)).segment((-29,-12)).segment((-35,-12)).segment((-35,-24)).segment((-42,-10)).close().assemble().push([(0,-5)]).circle(14,mode='s').push([(0,69)]).rect(24,36,mode='s').reset().face(w0.sketch().segment((-13,-53),(28,-61)).segment((28,-56)).segment((-12,-48)).close().assemble()).finalize().extrude(-12)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0024_00248700.step')

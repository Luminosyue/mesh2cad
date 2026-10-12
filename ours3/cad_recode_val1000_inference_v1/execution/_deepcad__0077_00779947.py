import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-23,0))
r=w0.sketch().segment((-100,-87),(-80,-87)).segment((-100,-50)).close().assemble().reset().face(w0.sketch().segment((-100,-30),(-69,5)).segment((-69,6)).segment((-68,6)).segment((-69,7)).segment((-69,88)).segment((-100,88)).close().assemble()).reset().face(w0.sketch().segment((-47,-88),(20,-88)).segment((20,-78)).segment((22,-79)).segment((53,-56)).segment((53,-42)).segment((75,-42)).segment((75,-47)).segment((100,-46)).segment((98,-38)).segment((69,-41)).segment((68,24)).segment((100,46)).segment((91,62)).segment((85,84)).segment((20,70)).segment((20,88)).segment((-6,88)).segment((-6,69)).segment((-47,69)).segment((-47,59)).segment((-45,59)).segment((-45,58)).segment((-47,58)).segment((-47,57)).segment((60,19)).segment((11,-7)).segment((11,-8)).segment((-47,-3)).close().assemble()).finalize().extrude(46)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0077_00779947.step')

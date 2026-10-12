import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(100,0,0))
r=w0.sketch().segment((-99,-94),(99,-94)).segment((99,94)).segment((-99,94)).segment((-99,-22)).segment((-99,-24)).close().assemble().finalize().extrude(-200).union(w0.sketch().segment((-99,-89),(99,-89)).segment((99,89)).segment((58,89)).arc((2,54),(-54,89)).segment((-99,89)).close().assemble().finalize().extrude(-19))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0027_00279411.step')

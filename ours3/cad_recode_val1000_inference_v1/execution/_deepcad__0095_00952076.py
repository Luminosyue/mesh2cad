import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,21))
r=w0.sketch().push([(-91,0)]).circle(9).reset().face(w0.sketch().segment((82,-2),(83,-2)).segment((83,-4)).segment((82,-4)).arc((99,4),(82,-2)).assemble()).finalize().extrude(-42)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0095_00952076.step')

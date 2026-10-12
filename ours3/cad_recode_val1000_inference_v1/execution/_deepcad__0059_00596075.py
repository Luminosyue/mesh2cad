import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(94,0,0))
r=w0.sketch().segment((-94,-100),(94,-100)).segment((94,100)).segment((-94,100)).segment((-94,-17)).segment((-90,-17)).segment((-90,-24)).segment((-94,-24)).close().assemble().finalize().extrude(-188).union(w0.workplane(offset=-8/2).cylinder(8,57))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0059_00596075.step')

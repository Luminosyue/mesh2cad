import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-75,0))
w1=cq.Workplane('YZ',origin=(6,0,0))
r=w0.sketch().segment((-100,-25),(-33,-25)).segment((-33,-46)).segment((-27,-46)).segment((-27,-75)).segment((33,-75)).segment((33,-46)).segment((39,-46)).segment((39,-25)).segment((100,-25)).segment((100,75)).segment((29,75)).segment((70,68)).segment((37,-4)).segment((-70,49)).segment((-61,69)).segment((-70,71)).segment((-70,75)).segment((-100,75)).close().assemble().finalize().extrude(150).union(w1.sketch().segment((-75,-24),(-21,-24)).segment((-21,-8)).segment((8,-8)).segment((8,-40)).arc((75,-42),(41,12)).segment((41,34)).segment((-75,34)).close().assemble().finalize().extrude(-81))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0063_00637478.step')

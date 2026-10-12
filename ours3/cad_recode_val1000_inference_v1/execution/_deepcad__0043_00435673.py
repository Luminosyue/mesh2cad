import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(49,0,0))
w1=cq.Workplane('YZ',origin=(13,0,0))
r=w0.sketch().arc((-28,-100),(28,0),(-28,100)).close().assemble().finalize().extrude(-98).union(w0.sketch().arc((-28,-97),(10,0),(-28,97)).close().assemble().finalize().extrude(-19)).union(w1.sketch().arc((21,-39),(28,0),(21,39)).close().assemble().finalize().extrude(-62))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0043_00435673.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-67,0))
r=w0.sketch().segment((-83,-100),(-54,-100)).arc((-20,-24),(33,-100)).segment((83,-100)).segment((83,100)).segment((-83,100)).close().assemble().reset().face(w0.sketch().segment((83,65),(85,65)).segment((85,67)).arc((86,69),(85,71)).segment((85,73)).segment((83,73)).segment((83,71)).arc((82,69),(83,67)).close().assemble(),mode='s').finalize().extrude(134).union(w0.sketch().segment((-83,-100),(83,-100)).segment((83,54)).arc((0,51),(-83,86)).close().assemble().finalize().extrude(134))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0053_00530465.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,20,0))
r=w0.sketch().segment((-77,-100),(-63,-100)).segment((-63,-63)).segment((-77,-65)).close().assemble().reset().face(w0.sketch().segment((-77,-41),(-63,-39)).segment((-63,29)).segment((-77,29)).close().assemble()).finalize().extrude(-40).union(w0.sketch().segment((-57,-16),(-41,-16)).segment((-41,-33)).segment((39,-33)).segment((39,-16)).segment((44,-16)).segment((44,14)).arc((48,22),(50,31)).segment((57,31)).segment((57,20)).segment((77,20)).segment((77,100)).segment((-22,100)).segment((-22,91)).arc((-1,80),(17,66)).segment((17,77)).segment((21,77)).segment((21,71)).arc((43,53),(46,25)).arc((45,23),(44,20)).segment((44,14)).segment((39,14)).segment((39,16)).arc((-1,-13),(-41,16)).segment((-41,14)).segment((-57,14)).close().assemble().reset().face(w0.sketch().segment((-57,31),(-41,31)).segment((-41,33)).arc((-49,43),(-57,54)).close().assemble()).finalize().extrude(-27)).union(w0.workplane(offset=-27/2).moveTo(-48,-3).cylinder(27,10))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0093_00932108.step')

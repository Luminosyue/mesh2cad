import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-91,0))
r=w0.sketch().segment((-70,-72),(-26,-72)).segment((-26,-97)).segment((26,-97)).segment((26,-72)).segment((74,-72)).segment((74,-67)).segment((26,-67)).segment((26,-42)).arc((0,-53),(-26,-42)).segment((-26,-67)).segment((-70,-67)).close().assemble().reset().face(w0.sketch().segment((-70,67),(-26,67)).segment((-26,42)).arc((0,53),(26,42)).segment((26,67)).segment((74,67)).segment((74,72)).segment((26,72)).segment((26,97)).segment((-26,97)).segment((-26,72)).segment((-70,72)).close().assemble()).finalize().extrude(31).union(w0.sketch().segment((-4,-100),(4,-100)).segment((4,-99)).arc((37,-93),(69,-73)).arc((55,-83),(41,-91)).segment((41,-93)).segment((37,-93)).arc((20,-97),(4,-99)).segment((4,-91)).arc((0,-91),(-4,-90)).close().assemble().finalize().extrude(169)).union(w0.sketch().arc((-81,-58),(-11,18),(-7,-77)).arc((35,-93),(74,-67)).arc((50,-46),(90,-48)).arc((-13,99),(-81,-58)).assemble().finalize().extrude(182))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0048_00481308.step')

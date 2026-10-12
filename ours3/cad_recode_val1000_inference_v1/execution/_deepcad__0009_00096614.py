import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-97,0))
w1=cq.Workplane('ZX',origin=(0,-71,0))
r=w0.sketch().segment((-54,-4),(-46,-4)).segment((-46,-6)).segment((-26,-6)).segment((-26,-17)).segment((-12,-17)).segment((-12,-23)).segment((12,-23)).segment((12,-17)).segment((26,-17)).segment((26,-4)).segment((34,-4)).segment((34,17)).segment((26,17)).segment((26,19)).segment((12,19)).segment((12,25)).segment((-12,25)).segment((-12,19)).segment((-26,19)).segment((-26,17)).segment((-54,17)).close().assemble().finalize().extrude(-3).union(w0.sketch().segment((-39,46),(-6,24)).segment((-6,46)).close().assemble().reset().face(w0.sketch().segment((10,39),(34,58)).segment((34,59)).segment((35,59)).segment((34,59)).segment((34,58)).segment((10,39)).close().assemble()).finalize().extrude(197)).union(w1.sketch().arc((-31,17),(-28,16),(-26,15)).segment((-26,14)).segment((-25,14)).arc((1,-23),(14,-60)).arc((26,-45),(30,-25)).segment((54,-25)).segment((54,-28)).segment((53,-28)).segment((53,-47)).segment((27,-47)).arc((27,-49),(26,-51)).segment((26,-25)).segment((27,-25)).segment((27,-23)).segment((26,-23)).segment((26,-21)).segment((25,-21)).arc((1,11),(-31,17)).assemble().finalize().extrude(167))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0009_00096614.step')

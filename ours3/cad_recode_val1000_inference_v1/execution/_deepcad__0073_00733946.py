import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-8))
r=w0.sketch().segment((-68,-90),(-20,-99)).segment((-17,-80)).arc((-29,-46),(-25,-11)).segment((-35,10)).segment((-17,19)).segment((-18,54)).segment((-67,54)).segment((-67,-16)).segment((-50,-16)).segment((-50,-27)).segment((-67,-30)).close().assemble().reset().face(w0.sketch().segment((10,-96),(68,-96)).segment((68,-23)).segment((59,-23)).segment((68,1)).segment((68,47)).segment((17,47)).segment((17,24)).segment((32,24)).segment((32,-23)).segment((10,-23)).segment((10,-24)).segment((32,-24)).segment((32,-54)).segment((10,-54)).close().assemble()).finalize().extrude(6).union(w0.sketch().segment((-55,-93),(-21,-100)).segment((-17,-80)).arc((-35,-72),(-22,-59)).segment((-20,-51)).segment((-54,-44)).arc((-50,-69),(-55,-93)).assemble().reset().face(w0.sketch().segment((-36,83),(-31,83)).arc((-13,92),(5,88)).segment((10,89)).arc((-14,96),(-36,83)).assemble()).finalize().extrude(16))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0073_00733946.step')

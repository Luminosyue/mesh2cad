import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,23,0))
r=w0.sketch().arc((-71,70),(-94,-13),(-22,-78)).segment((-22,-80)).segment((20,-80)).segment((20,-78)).arc((29,-76),(38,-72)).segment((41,-73)).segment((42,-69)).arc((53,-65),(64,-59)).segment((42,-59)).segment((42,-46)).segment((65,-46)).segment((65,-57)).arc((67,-55),(69,-53)).segment((70,-53)).segment((70,-52)).arc((94,-13),(98,34)).segment((34,1)).segment((-15,80)).segment((-71,80)).close().assemble().reset().face(w0.sketch().segment((34,80),(84,75)).arc((79,77),(74,79)).segment((74,80)).close().assemble()).finalize().extrude(-46).union(w0.sketch().arc((-98,35),(-10,-36),(38,60)).arc((-26,33),(-98,35)).assemble().finalize().extrude(-14))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0041_00417681.step')

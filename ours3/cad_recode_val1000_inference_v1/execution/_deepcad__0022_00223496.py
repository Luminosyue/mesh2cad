import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-20,0))
r=w0.sketch().segment((-100,-59),(-64,-59)).segment((-48,-20)).segment((-100,13)).close().assemble().reset().face(w0.sketch().segment((-100,43),(-87,43)).segment((-87,59)).segment((12,59)).segment((12,43)).segment((26,43)).segment((26,59)).segment((-100,59)).close().assemble()).reset().face(w0.sketch().segment((-39,-59),(92,-59)).segment((92,-44)).segment((100,-44)).segment((100,43)).segment((92,43)).segment((92,59)).segment((59,59)).segment((59,30)).segment((12,30)).segment((12,14)).segment((16,14)).segment((16,-35)).segment((-19,-35)).segment((-19,14)).segment((-39,14)).close().assemble()).finalize().extrude(39).union(w0.sketch().segment((-87,-59),(78,-59)).segment((78,-44)).segment((17,-44)).segment((17,19)).segment((-87,19)).close().assemble().finalize().extrude(39))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0022_00223496.step')

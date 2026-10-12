import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,23,0))
r=w0.sketch().segment((-100,-87),(0,-87)).segment((0,-27)).segment((-100,-27)).segment((-100,-39)).segment((-99,-39)).segment((-99,-41)).segment((-100,-41)).close().assemble().reset().face(w0.sketch().segment((-100,26),(0,26)).segment((0,87)).segment((-100,87)).segment((-100,54)).segment((-52,44)).segment((-57,26)).segment((-100,36)).close().assemble()).finalize().extrude(-46).union(w0.sketch().segment((-100,26),(0,26)).segment((0,1)).segment((14,1)).segment((14,-34)).segment((0,-34)).segment((0,-60)).segment((69,-60)).segment((69,-51)).segment((100,-51)).segment((100,31)).segment((0,31)).segment((0,30)).segment((-100,30)).close().assemble().finalize().extrude(-23)).union(w0.workplane(offset=-13/2).moveTo(-52,-30).box(72,8,13))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0002_00020426.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,4,0))
r=w0.sketch().segment((-17,-100),(17,-100)).segment((17,30)).segment((16,30)).segment((16,13)).segment((10,13)).segment((10,10)).segment((16,10)).segment((16,-14)).segment((10,-14)).segment((10,-17)).segment((8,-17)).segment((8,-14)).segment((2,-14)).segment((2,-10)).segment((-17,2)).close().assemble().reset().face(w0.sketch().segment((-17,40),(17,56)).segment((17,94)).segment((8,100)).segment((-10,100)).segment((-10,96)).segment((-17,96)).close().assemble()).finalize().extrude(-8)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0013_00133896.step')

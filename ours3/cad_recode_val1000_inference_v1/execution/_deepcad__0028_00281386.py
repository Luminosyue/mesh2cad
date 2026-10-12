import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-38,0))
w1=cq.Workplane('ZX',origin=(0,-23,0))
r=w0.sketch().segment((-37,-3),(-33,-3)).arc((0,-36),(33,-3)).segment((37,-3)).segment((37,3)).segment((33,3)).arc((0,36),(-33,3)).segment((-37,3)).close().assemble().circle(34,mode='s').finalize().extrude(-62).union(w0.sketch().segment((-36,5),(-32,5)).arc((-1,37),(36,6)).segment((42,0)).arc((1,41),(-36,5)).assemble().reset().face(w0.sketch().arc((-35,-12),(-33,-18),(-29,-23)).segment((-29,-31)).segment((-26,-31)).arc((-17,-38),(-7,-41)).segment((-15,-34)).arc((-25,-31),(-32,-23)).close().assemble()).reset().face(w0.sketch().arc((-15,-41),(-1,-42),(13,-40)).close().assemble()).reset().face(w0.sketch().arc((26,-31),(33,-26),(38,-18)).close().assemble()).finalize().extrude(138)).union(w1.sketch().push([(0,3)]).circle(34).circle(33,mode='s').finalize().extrude(-73))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0028_00281386.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,35,0))
w1=cq.Workplane('ZX',origin=(0,26,0))
r=w0.sketch().arc((-24,33),(12,27),(37,55)).segment((37,75)).arc((12,98),(-21,93)).arc((-37,63),(-24,33)).assemble().finalize().extrude(-100).union(w0.sketch().arc((-91,41),(-99,-14),(-77,-64)).arc((-62,-78),(-45,-89)).arc((-30,26),(88,17)).arc((86,24),(84,31)).arc((82,57),(71,79)).segment((71,60)).arc((0,100),(-71,60)).segment((-71,79)).arc((-82,58),(-91,41)).assemble().reset().face(w0.sketch().arc((-18,-98),(0,-100),(18,-98)).close().assemble()).finalize().extrude(30)).union(w1.workplane(offset=-74/2).moveTo(0,63).cylinder(74,37))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0006_00060081.step')

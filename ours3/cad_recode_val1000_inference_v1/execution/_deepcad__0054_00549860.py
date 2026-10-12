import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,23,0))
w1=cq.Workplane('YZ',origin=(90,0,0))
r=w0.sketch().segment((-46,-57),(-46,-47)).arc((-47,-52),(-46,-57)).assemble().reset().face(w0.sketch().arc((-44,-68),(-39,-79),(-30,-88)).segment((-30,-90)).segment((-27,-90)).arc((0,-100),(27,-90)).segment((30,-90)).segment((30,-88)).arc((46,-61),(39,-29)).segment((39,-30)).segment((37,-29)).segment((38,-26)).arc((35,-22),(32,-19)).segment((32,-17)).segment((30,-17)).arc((17,-10),(4,-6)).arc((-1,-7),(-7,-6)).arc((-10,-7),(-14,-8)).arc((-12,-33),(-23,-51)).segment((-23,-57)).arc((-24,-53),(-24,-49)).arc((-35,-59),(-44,-68)).assemble()).push([(0,-53)]).circle(23,mode='s').finalize().extrude(-94).union(w0.sketch().arc((-48,91),(-36,92),(-24,90)).arc((-10,97),(4,91)).arc((7,90),(10,89)).arc((10,94),(11,100)).segment((-16,100)).arc((-32,92),(-48,91)).assemble().finalize().extrude(49)).union(w1.sketch().arc((23,-48),(71,0),(23,48)).segment((23,39)).arc((33,13),(23,-13)).close().assemble().finalize().extrude(-3))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0054_00549860.step')

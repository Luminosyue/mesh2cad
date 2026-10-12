import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,36))
r=w0.sketch().circle(100).push([(0,-18)]).circle(50,mode='s').finalize().extrude(-72).union(w0.sketch().arc((-93,-38),(0,-85),(93,-38)).segment((63,-38)).arc((80,0),(63,38)).segment((93,38)).arc((0,85),(-93,38)).segment((-63,38)).arc((-80,0),(-63,-38)).close().assemble().reset().face(w0.sketch().segment((-48,-21),(-37,-21)).arc((-39,0),(-37,21)).segment((-48,21)).close().assemble(),mode='s').reset().face(w0.sketch().segment((37,-21),(48,-21)).segment((48,21)).segment((37,21)).arc((39,0),(37,-21)).assemble(),mode='s').finalize().extrude(-43))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0047_00476041.step')

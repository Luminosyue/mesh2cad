import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(45,0,0))
r=w0.sketch().segment((-100,-82),(100,-82)).segment((100,22)).segment((-100,-40)).close().assemble().reset().face(w0.sketch().segment((-100,40),(100,49)).segment((100,82)).segment((-100,82)).close().assemble()).finalize().extrude(-90).union(w0.sketch().segment((-96,-82),(-12,-82)).arc((-59,-65),(-96,-33)).close().assemble().reset().face(w0.sketch().arc((-96,33),(-59,65),(-12,82)).segment((-96,82)).close().assemble()).reset().face(w0.sketch().segment((12,-82),(96,-82)).segment((96,82)).segment((12,82)).arc((59,65),(96,33)).close().assemble()).finalize().extrude(-59))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0052_00523323.step')

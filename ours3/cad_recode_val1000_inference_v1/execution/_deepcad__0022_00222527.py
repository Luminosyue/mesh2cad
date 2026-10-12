import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(44,0,0))
r=w0.sketch().segment((-100,-39),(-68,-39)).arc((-87,-16),(-95,11)).segment((-97,11)).segment((-97,15)).segment((-95,15)).arc((-87,33),(-71,44)).segment((-100,44)).close().assemble().reset().face(w0.sketch().segment((-57,-39),(100,-39)).segment((100,39)).segment((68,39)).arc((47,-5),(29,39)).segment((-28,39)).segment((-11,15)).segment((-19,15)).arc((-27,1),(-37,-13)).close().assemble()).finalize().extrude(-88).union(w0.sketch().segment((-62,-39),(75,-39)).segment((75,-30)).segment((62,-30)).segment((62,13)).segment((-62,13)).close().assemble().finalize().extrude(-25))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0022_00222527.step')

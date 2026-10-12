import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-12))
r=w0.sketch().segment((-100,-59),(-82,-59)).segment((-82,-64)).segment((93,-64)).segment((93,-59)).segment((100,-59)).segment((100,64)).segment((34,64)).arc((39,52),(44,39)).segment((85,39)).segment((85,27)).segment((47,27)).arc((-25,-40),(-96,27)).segment((-96,39)).segment((-95,39)).arc((-98,52),(-100,64)).close().assemble().reset().face(w0.sketch().segment((-100,56),(-99,56)).arc((-98,58),(-96,60)).segment((-96,62)).arc((-98,60),(-100,56)).assemble()).reset().face(w0.sketch().segment((-93,-29),(-82,-29)).segment((-82,-13)).arc((-88,-20),(-93,-29)).assemble()).reset().face(w0.sketch().arc((-44,39),(-41,36),(-38,34)).segment((-38,39)).close().assemble()).reset().face(w0.sketch().arc((-14,39),(0,52),(12,64)).segment((-14,64)).close().assemble()).finalize().extrude(24)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0079_00798927.step')

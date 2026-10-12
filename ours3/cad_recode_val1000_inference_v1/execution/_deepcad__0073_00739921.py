import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-38))
r=w0.sketch().arc((-93,-36),(12,12),(-1,-90)).arc((58,81),(-93,-36)).assemble().finalize().extrude(58).union(w0.sketch().arc((-86,52),(-64,-77),(67,-74)).segment((37,-74)).segment((37,-21)).segment((68,-21)).segment((68,-72)).arc((85,-52),(97,-28)).segment((97,-21)).segment((98,-21)).arc((97,24),(75,66)).segment((75,52)).close().assemble().push([(-13,-5)]).circle(25,mode='s').finalize().extrude(77))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0073_00739921.step')

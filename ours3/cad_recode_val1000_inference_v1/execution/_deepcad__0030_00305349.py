import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-86,0))
w1=cq.Workplane('ZX',origin=(0,-45,0))
r=w0.sketch().segment((-48,-87),(60,-87)).segment((60,33)).segment((6,33)).segment((6,99)).arc((-44,77),(-48,22)).close().assemble().finalize().extrude(152).union(w0.sketch().segment((-60,33),(-58,15)).segment((-1,22)).segment((1,7)).segment((22,8)).segment((20,24)).segment((49,27)).segment((47,34)).segment((2,31)).segment((0,46)).segment((-31,42)).segment((-30,34)).close().assemble().finalize().extrude(172)).union(w1.sketch().arc((-58,15),(-18,14),(11,-14)).arc((12,86),(-58,15)).assemble().finalize().extrude(72))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0030_00305349.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-7,0))
w1=cq.Workplane('YZ',origin=(25,0,0))
r=w0.sketch().segment((11,45),(14,45)).segment((14,25)).segment((26,25)).arc((25,27),(24,29)).segment((19,29)).segment((19,30)).segment((24,30)).arc((29,46),(39,59)).segment((39,64)).segment((23,64)).segment((23,67)).segment((-39,67)).segment((-39,-18)).segment((-39,-20)).segment((-39,-21)).segment((-39,-22)).segment((-39,-49)).segment((-31,-49)).segment((-31,-28)).segment((11,-28)).close().assemble().reset().face(w0.sketch().segment((-39,-100),(16,-100)).segment((16,-99)).segment((17,-99)).segment((17,-100)).segment((23,-100)).segment((23,-49)).segment((16,-49)).segment((16,-100)).segment((-39,-100)).close().assemble()).finalize().extrude(23).union(w1.sketch().arc((-15,6),(-11,19),(-15,32)).close().assemble().finalize().extrude(65))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0083_00830666.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-49))
w1=cq.Workplane('ZX',origin=(0,59,0))
r=w0.sketch().segment((-100,-15),(-97,-15)).arc((-72,-41),(-37,-55)).segment((-37,-59)).segment((54,-59)).segment((54,-55)).arc((80,-34),(97,-5)).segment((100,-5)).segment((100,59)).segment((41,59)).arc((27,60),(14,59)).segment((-100,59)).close().assemble().reset().face(w0.sketch().arc((-45,-15),(43,-29),(14,56)).segment((14,-15)).close().assemble(),mode='s').finalize().extrude(98).union(w1.sketch().segment((-49,-95),(-24,-95)).segment((-24,-100)).segment((43,-100)).segment((43,-95)).segment((49,-95)).segment((49,100)).segment((-49,100)).close().assemble().finalize().extrude(-79))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0063_00630888.step')

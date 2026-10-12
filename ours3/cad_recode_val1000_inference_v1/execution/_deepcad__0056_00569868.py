import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,2))
r=w0.sketch().segment((-50,-74),(-43,-74)).segment((-49,-77)).segment((-42,-98)).segment((2,-83)).segment((6,-100)).segment((47,-94)).segment((40,-56)).segment((50,-56)).segment((50,-28)).segment((44,-28)).segment((44,-34)).segment((38,-34)).segment((38,-56)).segment((28,-56)).segment((28,-54)).segment((25,-56)).segment((17,-56)).segment((17,-34)).segment((10,-34)).segment((10,-28)).segment((2,-28)).segment((2,-17)).segment((50,-17)).segment((50,43)).segment((44,43)).segment((44,24)).segment((38,24)).segment((38,43)).segment((36,43)).arc((50,67),(38,91)).segment((38,100)).segment((-43,100)).segment((-43,91)).arc((-50,67),(-43,43)).segment((-43,40)).segment((-50,40)).segment((-50,34)).segment((-43,34)).segment((-43,24)).segment((-40,24)).segment((-40,4)).segment((-43,4)).segment((-43,-7)).segment((-50,-7)).close().assemble().push([(-16,-18)]).circle(12,mode='s').finalize().extrude(-4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0056_00569868.step')

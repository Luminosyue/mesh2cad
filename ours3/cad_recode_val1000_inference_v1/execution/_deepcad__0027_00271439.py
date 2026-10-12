import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-10,0))
r=w0.sketch().segment((-45,-100),(10,-100)).segment((10,-84)).segment((45,-84)).segment((45,-40)).segment((31,-40)).segment((31,-56)).segment((10,-56)).segment((10,-54)).segment((-2,-54)).segment((6,-14)).segment((5,-14)).segment((-3,-54)).segment((-45,-54)).close().assemble().reset().face(w0.sketch().segment((-45,-7),(-30,20)).segment((-30,31)).segment((-45,31)).close().assemble()).reset().face(w0.sketch().segment((-45,44),(-25,44)).segment((13,92)).arc((1,96),(-10,100)).segment((-35,100)).segment((-35,93)).segment((-45,93)).close().assemble()).reset().face(w0.sketch().segment((-22,-19),(10,0)).segment((45,0)).segment((45,65)).segment((25,83)).close().assemble()).finalize().extrude(20)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0027_00271439.step')

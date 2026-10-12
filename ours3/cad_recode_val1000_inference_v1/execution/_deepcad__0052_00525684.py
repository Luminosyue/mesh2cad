import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,4))
r=w0.sketch().segment((-100,-9),(-45,-9)).arc((-41,-5),(-36,-9)).segment((43,-9)).arc((41,-5),(38,-1)).segment((38,0)).segment((37,0)).arc((33,5),(28,9)).segment((-100,9)).close().assemble().reset().face(w0.sketch().segment((46,-9),(100,-9)).segment((100,9)).segment((46,9)).arc((49,5),(53,0)).segment((52,0)).segment((52,-1)).arc((49,-5),(46,-9)).assemble()).reset().face(w0.sketch().arc((65,-6),(69,-7),(73,-9)).segment((76,-9)).segment((76,-6)).close().assemble(),mode='s').finalize().extrude(-8)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0052_00525684.step')

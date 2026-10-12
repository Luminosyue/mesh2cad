import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-10))
w1=cq.Workplane('ZX',origin=(0,92,0))
r=w0.sketch().segment((-10,-91),(10,-91)).segment((10,-82)).arc((1,-86),(-10,-82)).close().assemble().reset().face(w0.sketch().arc((-10,-47),(1,-43),(10,-47)).segment((10,100)).segment((-3,98)).segment((-3,92)).segment((-10,92)).close().assemble()).finalize().extrude(19).union(w1.sketch().arc((-8,-9),(0,-8),(8,-8)).arc((0,10),(-8,-9)).assemble().push([(0,1)]).circle(8,mode='s').finalize().extrude(-139))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0002_00022216.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-38))
w1=cq.Workplane('ZX',origin=(0,41,0))
r=w0.sketch().segment((-100,-41),(100,-41)).segment((100,41)).segment((68,41)).arc((5,-8),(-68,41)).segment((-100,41)).close().assemble().finalize().extrude(76).union(w1.sketch().arc((-38,-98),(22,0),(-38,98)).close().assemble().finalize().extrude(-82))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0035_00350803.step')

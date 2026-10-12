import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-88))
w1=cq.Workplane('XY',origin=(0,0,-96))
r=w0.sketch().push([(0,-1)]).circle(36).circle(34,mode='s').finalize().extrude(-12).union(w0.sketch().arc((-35,4),(1,-35),(34,7)).arc((33,8),(33,10)).arc((10,33),(-22,27)).arc((-29,19),(-33,10)).segment((-33,4)).close().assemble().finalize().extrude(188)).union(w1.sketch().arc((-36,-20),(35,-10),(-36,0)).arc((-34,-10),(-36,-20)).assemble().push([(0,-1)]).circle(33,mode='s').finalize().extrude(12))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0098_00981499.step')

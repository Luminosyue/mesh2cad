import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
w1=cq.Workplane('XY',origin=(0,0,19))
r=w0.sketch().arc((-69,29),(53,-53),(-21,71)).arc((-22,69),(-24,69)).arc((-44,61),(-60,46)).arc((-67,34),(-69,29)).assemble().finalize().extrude(-200).union(w0.sketch().arc((-73,16),(49,-51),(11,74)).arc((-11,19),(-73,16)).assemble().finalize().extrude(-44)).union(w1.sketch().arc((-62,43),(51,-55),(-43,62)).arc((-33,27),(-62,43)).assemble().finalize().extrude(-109))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0083_00839496.step')

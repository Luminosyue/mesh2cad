import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
w1=cq.Workplane('ZX',origin=(0,-87,0))
r=w0.sketch().arc((-49,-11),(29,27),(0,-50)).arc((25,31),(-49,-11)).assemble().finalize().extrude(95).union(w0.sketch().arc((-44,-25),(29,39),(1,-50)).arc((1,-48),(2,-46)).arc((27,31),(-43,-11)).arc((-44,-18),(-44,-25)).assemble().finalize().extrude(200)).union(w1.sketch().arc((-38,-33),(-35,-35),(-32,-37)).segment((-32,-33)).close().assemble().finalize().extrude(87))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0067_00674103.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,57))
w1=cq.Workplane('ZX',origin=(0,-14,0))
r=w0.sketch().arc((-83,12),(-93,-34),(-47,-29)).arc((-44,-26),(-43,-23)).arc((-44,-17),(-43,-11)).arc((-66,14),(-83,12)).assemble().finalize().extrude(-143).union(w0.sketch().push([(-72,-15)]).circle(28).push([(65,24.5)]).rect(12,37).finalize().extrude(-96)).union(w0.sketch().segment((-43,-43),(100,-43)).segment((100,14)).segment((54,14)).segment((54,15)).segment((51,14)).segment((-43,14)).close().assemble().push([(29,-14)]).circle(3,mode='s').finalize().extrude(29)).union(w1.sketch().segment((31,14),(78,14)).arc((54,31),(31,14)).assemble().finalize().extrude(49))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0040_00402014.step')

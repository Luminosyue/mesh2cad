import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-37,0))
w1=cq.Workplane('ZX',origin=(0,-26,0))
r=w0.sketch().segment((-55,-99),(-47,-99)).segment((-47,-100)).segment((-43,-100)).segment((-43,-99)).segment((-35,-99)).segment((-35,-93)).segment((-29,-93)).segment((-29,-99)).segment((-8,-100)).segment((-8,-99)).segment((20,-99)).segment((20,-93)).segment((34,-93)).segment((34,-81)).segment((46,-81)).segment((46,-76)).segment((55,-76)).segment((55,-23)).segment((55,36)).segment((41,36)).segment((53,35)).segment((52,24)).segment((-16,98)).segment((-16,100)).segment((-55,100)).close().assemble().push([(1,-12)]).circle(21,mode='s').finalize().extrude(74).union(w1.sketch().arc((-16,91),(14,51),(55,24)).arc((21,67),(-16,91)).assemble().finalize().extrude(62))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0037_00373164.step')

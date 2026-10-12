import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,0,0))
w1=cq.Workplane('ZX',origin=(0,-18,0))
r=w0.sketch().push([(16,56.5)]).rect(68,27).push([(16,57)]).circle(8,mode='s').push([(56,-19.5)]).rect(88,27).push([(62.5,58)]).rect(75,26).finalize().extrude(-40).union(w0.sketch().segment((-100,-71),(12,-71)).segment((12,-70)).segment((72,-70)).segment((72,-53)).segment((73,-53)).segment((73,-13)).segment((72,-13)).segment((72,32)).segment((-16,32)).segment((-16,23)).segment((-100,23)).close().assemble().push([(-50,-47)]).circle(21,mode='s').push([(52,-31)]).circle(20,mode='s').finalize().extrude(40)).union(w1.sketch().arc((-17,-29),(-15,-21),(-17,-12)).close().assemble().finalize().extrude(-10))
compound=r.val()
cq.exporters.export(compound, "/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_official_hash_verify_fixed_smoke_v3/execution/pred.step")
compound.exportStl("/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_official_hash_verify_fixed_smoke_v3/execution/pred.stl")

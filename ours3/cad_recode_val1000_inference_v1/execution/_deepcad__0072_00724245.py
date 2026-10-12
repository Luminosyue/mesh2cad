import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,39,0))
r=w0.sketch().segment((-48,74),(-26,74)).segment((-26,-89)).segment((0,-89)).segment((0,36)).segment((-1,36)).segment((-1,45)).segment((-26,45)).segment((-26,75)).segment((-48,75)).close().assemble().push([(-13,82)]).rect(16,36).push([(30.5,-87)]).rect(35,26).finalize().extrude(-78).union(w0.sketch().push([(-24,72.5)]).rect(48,55).push([(-24,72)]).circle(4,mode='s').push([(-13,62)]).circle(1,mode='s').finalize().extrude(-58)).union(w0.workplane(offset=-45/2).moveTo(-13,-12).box(26,94,45))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0072_00724245.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-67,0))
r=w0.workplane(offset=2/2).cylinder(2,74).union(w0.sketch().segment((-83,-100),(-10,-100)).arc((-16,-91),(-21,-81)).arc((-83,-19),(-46,55)).arc((1,95),(59,95)).arc((79,84),(83,62)).segment((83,100)).segment((-83,100)).segment((-83,50)).arc((-84,0),(-83,-50)).close().assemble().reset().face(w0.sketch().segment((-36,-100),(83,-100)).segment((83,59)).segment((83,60)).segment((83,100)).segment((-36,100)).segment((-36,50)).arc((-34,51),(-32,51)).arc((-24,53),(-16,51)).arc((-12,52),(-8,52)).arc((-10,56),(-13,60)).arc((-14,60),(-16,61)).arc((-24,62),(-32,60)).arc((-24,62),(-16,61)).arc((-24,60),(-32,58)).arc((-29,56),(-26,53)).arc((-21,52),(-16,51)).arc((-13,52),(-8,52)).arc((-10,51),(-13,51)).arc((-14,50),(-16,50)).arc((-24,48),(-32,50)).arc((-34,50),(-36,51)).close().assemble(),mode='s').finalize().extrude(134))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0077_00772051.step')

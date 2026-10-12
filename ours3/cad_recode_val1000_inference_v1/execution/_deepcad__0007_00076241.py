import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-17))
r=w0.sketch().segment((-83,-87),(-69,-87)).segment((-69,-100)).segment((83,-100)).segment((83,100)).segment((55,100)).segment((55,93)).segment((83,93)).segment((83,50)).segment((39,50)).arc((37,35),(29,22)).segment((29,100)).segment((-73,100)).segment((-73,93)).segment((-83,93)).segment((-83,-10)).segment((-52,-10)).arc((-29,50),(29,22)).segment((29,37)).arc((-29,20),(-52,-38)).segment((-83,-38)).close().assemble().reset().face(w0.sketch().arc((-35,-53),(11,-64),(55,-43)).segment((55,-53)).segment((83,-53)).segment((83,22)).arc((65,49),(39,65)).arc((29,-29),(-35,-53)).assemble()).finalize().extrude(34)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0007_00076241.step')

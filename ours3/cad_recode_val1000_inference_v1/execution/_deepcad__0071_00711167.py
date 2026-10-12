import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,9,0))
r=w0.sketch().segment((-100,-12),(-80,-12)).segment((-80,1)).segment((-55,1)).segment((-55,-27)).segment((-79,-27)).arc((-76,-30),(-73,-33)).segment((-94,-33)).arc((-70,-71),(-33,-94)).segment((-33,-95)).segment((-29,-95)).arc((0,-100),(29,-95)).segment((33,-95)).segment((33,-94)).arc((88,-47),(92,27)).segment((92,12)).segment((80,12)).segment((80,-1)).segment((55,-1)).segment((55,1)).segment((46,1)).segment((46,12)).segment((33,12)).segment((33,33)).segment((29,33)).arc((0,38),(-29,33)).segment((-33,33)).segment((-33,31)).arc((-59,57),(-29,80)).segment((-29,95)).segment((-33,95)).segment((-33,94)).arc((-70,71),(-92,33)).segment((-96,33)).arc((-99,10),(-100,-12)).assemble().reset().face(w0.sketch().arc((-22,-56),(0,-63),(22,-56)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-22,86),(22,86)).arc((0,93),(-22,86)).assemble()).finalize().extrude(-18)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0071_00711167.step')

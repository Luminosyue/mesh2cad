import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,8))
r=w0.sketch().segment((-50,-100),(50,-100)).segment((50,30)).segment((19,30)).segment((19,43)).segment((50,43)).segment((50,100)).segment((-50,100)).segment((-50,51)).arc((-44,55),(-37,58)).segment((-37,73)).segment((-19,73)).segment((-19,58)).arc((8,0),(-19,-58)).segment((-19,-73)).segment((-37,-73)).segment((-37,-58)).arc((-44,-55),(-50,-51)).close().assemble().reset().face(w0.sketch().segment((-8,-100),(8,-100)).segment((8,-97)).arc((0,-98),(-8,-97)).close().assemble(),mode='s').reset().face(w0.sketch().arc((-8,97),(0,98),(8,97)).segment((8,100)).segment((-8,100)).close().assemble(),mode='s').finalize().extrude(-16)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0033_00334836.step')

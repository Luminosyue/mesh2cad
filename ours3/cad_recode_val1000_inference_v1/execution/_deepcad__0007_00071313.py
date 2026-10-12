import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,6))
r=w0.sketch().segment((-93,-37),(-71,-50)).arc((-74,-48),(-76,-45)).segment((-80,-45)).segment((-80,-41)).arc((-86,-18),(-86,6)).segment((-86,22)).segment((-83,22)).arc((-78,40),(-66,58)).segment((-75,64)).arc((100,0),(-78,-60)).arc((-75,-55),(-71,-50)).arc((-74,-47),(-76,-45)).segment((-76,-59)).segment((-79,-59)).arc((-74,-66),(-69,-72)).close().assemble().reset().face(w0.sketch().arc((-62,-77),(0,-98),(62,-64)).segment((65,-64)).segment((65,-60)).arc((88,0),(65,60)).segment((65,64)).segment((62,64)).arc((26,84),(-16,86)).segment((10,88)).segment((10,87)).arc((79,38),(62,-47)).arc((18,-86),(-43,-76)).arc((-52,-73),(-62,-77)).assemble(),mode='s').finalize().extrude(-12)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0007_00071313.step')

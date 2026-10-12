import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,2))
r=w0.sketch().segment((-97,-37),(-97,-29)).segment((-66,-29)).segment((-66,-47)).segment((-88,-47)).arc((-87,-50),(-88,-54)).segment((-41,-54)).segment((-41,-45)).arc((-26,-55),(-10,-59)).segment((-10,-58)).segment((-6,-58)).segment((-6,-59)).arc((12,-58),(30,-49)).arc((46,-59),(63,-59)).segment((72,-59)).segment((72,-56)).arc((99,-49),(86,-25)).arc((89,25),(46,57)).segment((46,59)).segment((32,59)).segment((32,57)).arc((14,51),(0,39)).arc((-30,55),(-60,51)).segment((-60,59)).segment((-97,59)).segment((-97,40)).arc((-100,29),(-97,17)).segment((-97,16)).arc((-93,10),(-97,4)).close().assemble().reset().face(w0.sketch().segment((-66,16),(-22,-15)).segment((1,16)).segment((-43,47)).close().assemble(),mode='s').push([(39,12)]).circle(14,mode='s').push([(79,-43)]).circle(10).finalize().extrude(-4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0029_00297473.step')

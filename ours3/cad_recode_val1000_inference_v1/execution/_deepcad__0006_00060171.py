import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-7))
r=w0.sketch().segment((-100,-30),(-92,-30)).segment((-92,-55)).segment((-66,-55)).arc((-39,-19),(-39,-59)).segment((-39,-55)).segment((-8,-55)).segment((-8,-30)).segment((1,-30)).segment((1,-10)).segment((12,-10)).segment((12,-48)).segment((18,-48)).segment((18,-55)).segment((88,-55)).segment((88,-48)).segment((100,-48)).segment((100,38)).segment((88,38)).segment((88,45)).segment((18,45)).segment((18,38)).segment((12,38)).segment((12,30)).segment((1,30)).segment((1,37)).segment((-8,37)).segment((-8,55)).segment((-29,55)).arc((-62,24),(-86,55)).segment((-92,55)).segment((-92,37)).segment((-100,37)).close().assemble().reset().face(w0.sketch().segment((60,-41),(65,-41)).segment((65,-36)).arc((91,-10),(65,16)).segment((65,21)).segment((60,21)).segment((60,16)).arc((34,-10),(60,-36)).close().assemble(),mode='s').push([(75,41)]).rect(26,26).finalize().extrude(14)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0006_00060171.step')

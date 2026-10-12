import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
w1=cq.Workplane('ZX',origin=(0,-98,0))
r=w0.sketch().segment((-48,-14),(-48,-13)).arc((-49,0),(-48,13)).segment((-48,14)).arc((-50,0),(-48,-14)).assemble().reset().face(w0.sketch().arc((-42,-27),(-33,-37),(-23,-45)).segment((-23,-44)).arc((-33,-36),(-42,-27)).assemble()).reset().face(w0.sketch().arc((-21,-45),(49,-9),(13,48)).segment((13,49)).arc((30,40),(42,27)).segment((42,26)).arc((49,10),(48,-7)).segment((48,-8)).arc((49,-10),(48,-13)).segment((48,-14)).arc((49,-17),(48,-19)).segment((48,-20)).segment((47,-19)).arc((37,-33),(21,-45)).close().assemble()).finalize().extrude(191).union(w1.workplane(offset=198/2).cylinder(198,50))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/fusion360__41970_24ba0c1b_0009.step')

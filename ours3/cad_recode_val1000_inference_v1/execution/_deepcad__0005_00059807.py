import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-10))
w1=cq.Workplane('XY',origin=(0,0,-30))
r=w0.sketch().segment((-99,-20),(-97,-20)).arc((-88,-48),(-71,-70)).segment((-71,-71)).segment((-70,-71)).arc((0,-100),(70,-71)).segment((71,-71)).segment((71,-70)).arc((88,-46),(97,-18)).segment((99,-18)).segment((99,-13)).arc((100,0),(99,13)).segment((99,18)).segment((97,18)).arc((88,46),(71,70)).segment((71,71)).segment((70,71)).arc((0,100),(-70,71)).segment((-71,71)).segment((-71,70)).arc((-88,46),(-97,18)).segment((-99,18)).segment((-99,13)).arc((-100,0),(-99,-13)).close().assemble().push([(0,-3)]).circle(68,mode='s').finalize().extrude(-80).union(w0.sketch().segment((-7,-10),(-2,-10)).segment((-2,-20)).segment((2,-20)).segment((2,-10)).segment((7,-10)).segment((7,-36)).segment((11,-40)).segment((7,-44)).segment((7,-45)).arc((100,0),(7,45)).segment((7,20)).segment((2,20)).segment((2,30)).segment((-2,30)).segment((-2,20)).segment((-7,20)).close().assemble().finalize().extrude(100)).union(w1.sketch().arc((-7,-2),(53,-54),(97,12)).arc((95,13),(95,15)).arc((53,53),(2,32)).arc((1,19),(-7,7)).close().assemble().push([(46,-10)]).circle(43,mode='s').finalize().extrude(120))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0005_00059807.step')

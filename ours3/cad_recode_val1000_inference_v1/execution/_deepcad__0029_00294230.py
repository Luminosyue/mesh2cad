import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-12))
w1=cq.Workplane('YZ',origin=(17,0,0))
r=w0.sketch().segment((-17,-82),(-11,-82)).segment((-11,-94)).segment((11,-94)).segment((11,-82)).segment((17,-82)).segment((17,-37)).arc((10,-36),(17,-35)).segment((17,73)).segment((11,73)).segment((11,100)).segment((-11,100)).segment((-11,73)).segment((-17,73)).close().assemble().finalize().extrude(-4).union(w0.sketch().segment((-17,-13),(11,-13)).segment((11,100)).segment((10,100)).segment((-17,80)).segment((-17,72)).arc((8,35),(-17,-2)).close().assemble().finalize().extrude(28)).union(w1.sketch().arc((-100,10),(-63,-15),(-23,-8)).segment((-23,12)).segment((100,12)).segment((100,-12)).segment((-14,-12)).arc((-10,4),(-10,16)).segment((-52,16)).arc((-76,14),(-100,15)).close().assemble().finalize().extrude(-6))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0029_00294230.step')

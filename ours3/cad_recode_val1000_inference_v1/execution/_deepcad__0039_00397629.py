import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-50))
w1=cq.Workplane('XY',origin=(0,0,50))
r=w0.sketch().segment((-100,-65),(-57,-65)).segment((-57,-60)).segment((-26,-60)).segment((-26,-65)).segment((100,-65)).segment((100,-35)).segment((-45,-35)).segment((-45,-20)).segment((-50,-20)).segment((-50,-35)).segment((-100,-35)).close().assemble().push([(47,16)]).rect(6,86).finalize().extrude(101).union(w1.sketch().arc((-50,-26),(-14,-41),(23,-26)).segment((4,-26)).segment((4,-35)).segment((-13,-35)).segment((-13,35)).segment((-4,35)).segment((-4,65)).segment((38,65)).arc((17,65),(-3,58)).segment((4,58)).segment((4,35)).segment((-13,35)).segment((-13,28)).segment((-20,28)).segment((-20,65)).segment((-50,65)).segment((-50,58)).segment((-20,58)).segment((-20,-35)).segment((-50,-35)).close().assemble().finalize().extrude(-90))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0039_00397629.step')

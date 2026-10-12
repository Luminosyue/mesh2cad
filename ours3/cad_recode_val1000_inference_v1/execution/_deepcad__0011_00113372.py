import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-1))
r=w0.sketch().segment((-100,63),(-96,35)).segment((-96,12)).segment((-93,12)).segment((-87,-20)).segment((-97,-37)).segment((-96,-37)).segment((-96,-60)).segment((-70,-60)).segment((-70,-65)).segment((-68,-65)).segment((-68,-60)).segment((-42,-60)).segment((-42,-59)).segment((-5,-65)).segment((-2,-44)).segment((100,-56)).segment((100,-25)).segment((78,-25)).segment((78,-37)).segment((44,-37)).segment((44,-25)).segment((12,-25)).segment((15,-7)).segment((99,9)).segment((96,25)).arc((99,48),(87,65)).segment((87,60)).segment((58,60)).segment((58,65)).arc((50,61),(44,55)).segment((44,65)).segment((-7,65)).segment((-7,59)).segment((-76,59)).segment((-76,65)).segment((-87,65)).segment((-87,63)).close().assemble().push([(-49,12)]).circle(14,mode='s').push([(-49,-19)]).rect(38,12).push([(-49,36)]).rect(38,24).finalize().extrude(2)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0011_00113372.step')

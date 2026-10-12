import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,2,0))
r=w0.sketch().segment((-100,35),(-87,30)).segment((-95,-9)).segment((-87,-11)).segment((-95,-81)).segment((-59,-85)).segment((-57,-60)).segment((-35,-78)).segment((-28,-67)).segment((-51,-50)).segment((-43,-11)).segment((-26,-11)).segment((-26,-27)).segment((-33,-27)).segment((3,-56)).segment((3,-78)).segment((15,-78)).segment((15,-59)).segment((68,-85)).segment((94,-36)).segment((83,-30)).segment((94,-30)).segment((94,-15)).segment((100,-15)).segment((100,85)).segment((51,85)).segment((51,75)).segment((2,79)).segment((0,56)).segment((15,49)).segment((15,69)).segment((3,69)).segment((3,77)).segment((-49,79)).segment((-50,54)).segment((-73,65)).segment((-79,52)).segment((-44,35)).segment((-51,20)).segment((-68,27)).segment((-60,40)).segment((-68,44)).segment((-76,33)).segment((-86,38)).segment((-84,41)).segment((-97,46)).close().assemble().push([(1,11)]).circle(8,mode='s').push([(45,15)]).circle(17,mode='s').finalize().extrude(-4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0005_00054919.step')

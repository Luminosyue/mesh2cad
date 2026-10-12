import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,0))
r=w0.sketch().segment((-100,-46),(-68,-55)).segment((-68,-40)).segment((-56,-40)).segment((-56,-56)).segment((-60,-56)).segment((-52,-58)).segment((-40,-15)).segment((-29,-30)).segment((-29,-56)).segment((-7,-56)).segment((-7,-36)).segment((21,-44)).segment((23,-37)).segment((23,-48)).segment((72,-51)).segment((73,-47)).segment((100,-47)).segment((100,-22)).segment((78,-22)).segment((79,-9)).segment((96,1)).segment((92,9)).arc((94,47),(57,49)).segment((43,55)).segment((28,37)).segment((42,27)).arc((44,15),(51,4)).segment((52,2)).segment((23,10)).segment((5,50)).segment((10,51)).segment((-10,51)).segment((-10,50)).segment((-22,50)).segment((-22,43)).segment((-91,55)).segment((-97,29)).segment((-22,15)).segment((-22,11)).segment((-92,11)).close().assemble().push([(-50,-15)]).circle(6,mode='s').push([(-16,-16)]).circle(8,mode='s').push([(61,13)]).circle(21,mode='s').finalize().extrude(-1)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0082_00820771.step')

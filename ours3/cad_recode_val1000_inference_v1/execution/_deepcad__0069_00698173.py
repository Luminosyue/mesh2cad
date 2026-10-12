import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,2,0))
r=w0.sketch().segment((-100,21),(-87,18)).segment((-95,-5)).segment((-88,-7)).segment((-94,-52)).segment((-69,-56)).segment((-66,-40)).segment((-35,-56)).segment((-28,-40)).segment((-51,-40)).segment((-51,-30)).segment((-33,-30)).segment((-24,-10)).segment((-24,-22)).segment((-11,-22)).segment((-12,-41)).segment((1,-41)).segment((1,-56)).segment((34,-56)).segment((34,-47)).segment((86,-52)).segment((87,-37)).segment((100,-37)).segment((100,-22)).segment((89,-22)).segment((90,-8)).segment((100,7)).segment((100,38)).segment((79,38)).segment((80,55)).segment((28,51)).segment((28,44)).segment((71,44)).segment((71,37)).segment((34,37)).segment((34,38)).segment((1,38)).segment((1,56)).segment((-24,56)).segment((-24,45)).segment((-34,51)).segment((-41,35)).segment((-41,51)).segment((-87,56)).close().assemble().push([(4,10)]).circle(8,mode='s').push([(4,-27)]).circle(12,mode='s').finalize().extrude(-4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0069_00698173.step')

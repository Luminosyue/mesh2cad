import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,2,0))
r=w0.sketch().segment((-50,23),(-44,23)).segment((-44,-14)).segment((-36,-14)).segment((-48,-96)).segment((-25,-100)).segment((-24,-91)).segment((50,-98)).segment((50,-72)).segment((41,-72)).segment((41,-65)).segment((47,-65)).segment((47,-41)).segment((41,-41)).segment((41,-27)).segment((29,-27)).segment((29,-14)).segment((38,-14)).segment((38,23)).segment((50,23)).segment((50,74)).segment((47,74)).segment((47,94)).segment((38,94)).segment((38,100)).segment((-17,100)).segment((-17,94)).segment((-44,94)).segment((-44,74)).segment((-50,74)).close().assemble().push([(-4,50)]).circle(22,mode='s').push([(-34,-10)]).circle(2,mode='s').push([(19,-42)]).circle(15,mode='s').finalize().extrude(-4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0038_00388772.step')

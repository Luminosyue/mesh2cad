import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-10,0))
r=w0.sketch().segment((-90,-100),(13,-100)).segment((13,-62)).segment((16,-62)).segment((16,-54)).arc((19,-47),(16,-40)).segment((16,-32)).segment((13,-32)).segment((13,-29)).arc((76,-45),(81,19)).segment((90,19)).segment((90,100)).segment((-26,100)).segment((-26,65)).segment((-39,85)).segment((-90,52)).segment((-90,19)).segment((-58,19)).arc((-55,12),(-51,5)).segment((-90,5)).close().assemble().reset().face(w0.sketch().segment((-36,-23),(-32,-23)).arc((-12,-85),(1,-22)).segment((1,4)).segment((-36,4)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-36,19),(-16,19)).arc((-26,20),(-36,19)).assemble(),mode='s').push([(49,59)]).circle(15,mode='s').finalize().extrude(19)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0074_00748931.step')

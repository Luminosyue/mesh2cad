import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,63))
r=w0.sketch().arc((-100,-60),(-88,-90),(-61,-100)).segment((60,-100)).arc((91,-87),(100,-56)).segment((100,11)).arc((91,16),(100,21)).segment((100,64)).arc((91,87),(68,100)).segment((-67,100)).arc((-88,90),(-100,70)).close().assemble().push([(-16,0)]).circle(35,mode='s').finalize().extrude(-125)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0047_00476093.step')

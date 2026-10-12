import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-5))
r=w0.sketch().segment((-100,-48),(-97,-48)).segment((-97,-73)).segment((-85,-73)).segment((-85,-48)).segment((-78,-48)).segment((-78,-22)).segment((-45,-22)).segment((-45,-48)).segment((-32,-48)).segment((-32,-73)).segment((-19,-73)).segment((-19,-78)).segment((24,-78)).segment((24,-73)).segment((27,-73)).segment((27,-51)).segment((51,-78)).segment((100,-78)).segment((100,78)).segment((-97,78)).segment((-97,53)).segment((-100,53)).close().assemble().reset().face(w0.sketch().segment((-74,31),(-24,10)).segment((-24,-34)).segment((1,-34)).segment((1,-10)).segment((45,-27)).segment((84,51)).segment((1,78)).segment((-24,12)).segment((-71,37)).close().assemble(),mode='s').finalize().extrude(10)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0050_00508400.step')

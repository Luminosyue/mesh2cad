import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,3))
r=w0.sketch().segment((-6,-95),(0,-95)).segment((0,-100)).segment((6,-100)).segment((6,94)).segment((0,94)).segment((0,100)).segment((-6,100)).close().assemble().push([(0,27)]).circle(7,mode='s').finalize().extrude(-6)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0067_00676933.step')

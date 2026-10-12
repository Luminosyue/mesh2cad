import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,4))
r=w0.sketch().segment((-22,-100),(22,-100)).segment((22,29)).segment((17,29)).segment((17,50)).segment((22,50)).segment((22,94)).segment((17,94)).segment((17,100)).segment((-9,100)).segment((-9,94)).segment((-22,94)).segment((-22,50)).segment((-17,50)).segment((-17,35)).segment((-22,35)).close().assemble().push([(-4,-8)]).circle(18,mode='s').reset().face(w0.sketch().segment((17,50),(20,50)).segment((20,52)).segment((17,53)).close().assemble(),mode='s').reset().face(w0.sketch().segment((17,74),(20,73)).segment((20,75)).segment((17,75)).close().assemble(),mode='s').finalize().extrude(-8)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0049_00499038.step')

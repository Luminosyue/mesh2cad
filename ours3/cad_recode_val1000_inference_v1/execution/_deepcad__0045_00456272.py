import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-2))
r=w0.sketch().segment((-100,-8),(-66,-8)).segment((-66,-7)).segment((-64,-7)).segment((-64,-8)).segment((-14,-8)).segment((-14,-11)).segment((0,-11)).segment((-3,3)).segment((2,3)).segment((2,8)).segment((-100,8)).close().assemble().push([(-87,1)]).circle(5,mode='s').reset().face(w0.sketch().segment((-66,-7),(-51,-7)).segment((-51,0)).segment((-48,0)).segment((-48,2)).segment((-66,2)).close().assemble(),mode='s').reset().face(w0.sketch().segment((11,-8),(64,-8)).segment((64,-7)).segment((78,-7)).segment((78,-8)).segment((91,-8)).arc((95,-5),(99,-8)).segment((100,-8)).segment((100,8)).segment((91,8)).segment((78,8)).segment((64,8)).segment((11,8)).close().assemble()).finalize().extrude(5)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0045_00456272.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-7,0))
r=w0.sketch().segment((-100,-48),(10,-48)).segment((10,-39)).arc((12,-40),(14,-40)).segment((14,-48)).segment((98,-48)).segment((98,-23)).segment((100,-23)).segment((100,23)).segment((98,23)).segment((98,48)).segment((14,48)).segment((14,40)).arc((12,40),(10,40)).segment((10,48)).segment((-86,48)).segment((-86,23)).segment((-88,23)).segment((-88,-23)).segment((-86,-23)).segment((-86,-48)).segment((-100,-48)).close().assemble().reset().face(w0.sketch().segment((-82,1),(-34,-42)).segment((82,19)).segment((34,49)).segment((14,17)).segment((14,23)).segment((-14,23)).segment((-14,10)).segment((-34,10)).segment((-34,23)).segment((-40,23)).segment((-40,32)).close().assemble(),mode='s').finalize().extrude(14)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0045_00457351.step')

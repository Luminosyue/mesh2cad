import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-2))
r=w0.sketch().segment((-40,0),(-36,0)).segment((-36,2)).segment((-29,2)).segment((-29,0)).segment((-28,0)).segment((-28,1)).segment((1,-7)).segment((1,-32)).segment((12,-32)).segment((12,-10)).segment((18,-12)).segment((18,-27)).segment((12,-27)).segment((12,-32)).segment((1,-32)).segment((1,-73)).segment((12,-73)).segment((12,-77)).segment((0,-77)).segment((0,-78)).segment((1,-78)).segment((1,-100)).segment((40,-98)).segment((38,-73)).segment((40,-73)).segment((40,-27)).segment((38,-27)).segment((38,-23)).segment((40,-23)).segment((40,0)).segment((38,0)).segment((38,2)).segment((32,2)).segment((32,0)).segment((18,0)).segment((18,2)).segment((12,2)).segment((12,0)).segment((11,0)).segment((11,11)).segment((40,25)).segment((40,52)).segment((32,52)).segment((40,98)).segment((-34,100)).segment((-40,36)).close().assemble().push([(-1,36)]).circle(19,mode='s').finalize().extrude(4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0040_00403102.step')

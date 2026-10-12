import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-2,0))
r=w0.sketch().segment((-13,33),(-12,33)).segment((-12,-100)).segment((13,-91)).segment((12,-89)).segment((12,-65)).segment((11,-65)).segment((11,-63)).segment((12,-63)).segment((12,-27)).segment((13,37)).segment((12,37)).segment((12,75)).segment((4,75)).segment((4,87)).segment((10,87)).segment((10,100)).segment((-6,100)).segment((-6,96)).segment((-13,96)).segment((-12,44)).segment((-12,43)).segment((-12,42)).segment((-12,33)).close().assemble().reset().face(w0.sketch().segment((-11,-39),(-10,-39)).segment((-10,-40)).segment((10,-40)).segment((10,-39)).segment((11,-39)).segment((11,-36)).segment((10,-36)).segment((10,-35)).segment((-10,-35)).segment((-10,-36)).segment((-11,-36)).close().assemble(),mode='s').finalize().extrude(4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0000_00003210.step')

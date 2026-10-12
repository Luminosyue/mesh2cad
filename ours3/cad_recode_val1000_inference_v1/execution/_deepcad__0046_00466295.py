import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,0,0))
r=w0.sketch().segment((-13,96),(-11,55)).arc((-13,20),(6,-10)).segment((-12,-10)).segment((-12,-54)).segment((-11,-54)).segment((-12,-97)).segment((13,-98)).segment((13,-54)).segment((12,-54)).segment((12,-10)).segment((13,13)).arc((13,36),(1,55)).segment((13,55)).segment((13,98)).segment((-1,98)).segment((-1,100)).close().assemble().finalize().extrude(0)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0046_00466295.step')

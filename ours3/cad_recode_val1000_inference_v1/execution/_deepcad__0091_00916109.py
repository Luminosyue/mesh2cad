import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,13,0))
r=w0.sketch().segment((-13,-100),(-10,-100)).segment((-9,-97)).segment((-9,15)).segment((-13,15)).close().assemble().finalize().extrude(-26).union(w0.sketch().segment((-13,51),(13,51)).segment((13,39)).segment((12,39)).segment((12,37)).segment((13,37)).segment((13,-14)).segment((-10,-14)).segment((-10,-34)).segment((-12,-34)).segment((-12,-75)).segment((-10,-75)).segment((-10,-79)).segment((-13,-79)).close().assemble().reset().face(w0.sketch().segment((-13,82),(8,64)).segment((13,70)).segment((13,91)).segment((1,100)).segment((-13,100)).close().assemble()).finalize().extrude(-4))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0091_00916109.step')

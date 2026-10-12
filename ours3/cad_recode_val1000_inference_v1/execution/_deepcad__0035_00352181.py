import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-34,0))
w1=cq.Workplane('XY',origin=(0,0,22))
r=w0.sketch().segment((-37,74),(11,25)).segment((35,41)).segment((-14,100)).close().assemble().finalize().extrude(68).union(w0.sketch().segment((-36,79),(31,42)).segment((34,42)).segment((34,41)).segment((32,41)).segment((32,40)).segment((12,24)).segment((22,-5)).segment((36,3)).segment((15,31)).segment((34,41)).segment((15,70)).segment((-1,60)).segment((-29,87)).close().assemble().finalize().extrude(68)).union(w1.sketch().segment((-100,-21),(-94,-21)).segment((-94,-34)).segment((-37,-34)).segment((-37,-21)).segment((-31,-21)).segment((-31,-34)).segment((25,-34)).segment((25,-22)).segment((20,-22)).segment((20,20)).segment((14,20)).segment((14,34)).segment((-31,34)).segment((-31,33)).segment((-100,33)).close().assemble().push([(-65.5,16)]).rect(11,26,mode='s').push([(-12,-8)]).circle(4,mode='s').finalize().extrude(17))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0035_00352181.step')

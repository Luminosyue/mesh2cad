import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,27,0))
r=w0.sketch().push([(-8.5,88)]).rect(11,24).push([(-8,88)]).circle(2,mode='s').finalize().extrude(-61).union(w0.sketch().segment((-14,-42),(-3,-42)).segment((-3,-41)).segment((-1,-41)).segment((-1,-42)).segment((21,-42)).segment((21,-41)).segment((30,-41)).segment((31,-20)).segment((21,-20)).segment((21,-17)).segment((-14,-17)).close().assemble().push([(25.5,88)]).rect(9,24).finalize().extrude(-51)).union(w0.sketch().segment((-31,2),(-18,2)).segment((-18,-6)).segment((-30,-6)).segment((-30,-39)).segment((-31,-39)).segment((-31,-40)).segment((-30,-40)).segment((-30,-72)).segment((-31,-72)).segment((-31,-93)).segment((-28,-93)).segment((-28,-100)).segment((7,-100)).segment((7,-93)).segment((9,-93)).segment((9,-72)).segment((8,-72)).segment((8,-63)).segment((13,-63)).segment((13,-16)).segment((12,-16)).segment((12,39)).segment((11,39)).segment((11,41)).segment((-31,41)).close().assemble().finalize().extrude(7))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0077_00777624.step')

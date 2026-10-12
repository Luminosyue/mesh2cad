import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-1))
r=w0.sketch().segment((-76,93),(-68,59)).segment((-71,53)).segment((-65,50)).segment((-62,40)).segment((-62,26)).segment((-57,26)).segment((-41,0)).segment((-75,-14)).segment((-73,-20)).segment((-55,-13)).segment((-43,-39)).segment((-69,-52)).segment((-64,-60)).segment((-69,-97)).segment((-40,-100)).segment((-38,-88)).segment((-37,-98)).segment((76,-87)).segment((72,-59)).segment((74,-59)).segment((74,-30)).segment((76,-30)).segment((76,14)).segment((63,14)).segment((74,41)).segment((46,41)).segment((46,67)).segment((74,67)).segment((74,87)).segment((7,94)).segment((5,83)).segment((3,85)).segment((3,86)).segment((2,86)).segment((-21,96)).segment((-25,86)).segment((-26,86)).segment((-26,85)).segment((-68,100)).close().assemble().push([(16,11)]).circle(29,mode='s').finalize().extrude(2)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0064_00642792.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-5,0))
r=w0.sketch().segment((-96,11),(-96,12)).arc((-99,-6),(-85,-16)).segment((-85,5)).segment((-69,5)).segment((-69,-17)).segment((8,-17)).segment((8,-11)).segment((17,-11)).segment((17,-17)).segment((86,-17)).segment((86,-16)).arc((100,-1),(86,15)).segment((86,17)).segment((17,17)).segment((17,15)).segment((8,15)).segment((8,17)).segment((-74,17)).segment((-74,16)).segment((-79,16)).segment((-79,14)).arc((-80,14),(-80,13)).segment((-80,11)).close().assemble().push([(-88,-5)]).circle(2,mode='s').push([(-85,4)]).circle(2,mode='s').push([(-40,0)]).circle(2,mode='s').push([(83,0)]).circle(9,mode='s').finalize().extrude(10)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0089_00893672.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-1))
r=w0.sketch().segment((-100,10),(-96,-5)).segment((-99,-7)).segment((-91,-18)).segment((-89,-16)).segment((-86,-24)).segment((-53,-15)).segment((-53,-22)).segment((-25,-22)).segment((-25,-19)).segment((14,-23)).segment((15,-18)).segment((100,-10)).segment((96,5)).segment((99,7)).segment((91,18)).segment((89,16)).segment((86,24)).segment((53,15)).segment((53,22)).segment((25,22)).segment((25,18)).segment((-14,20)).segment((-15,20)).segment((-14,21)).segment((-25,22)).segment((-25,20)).segment((-53,20)).segment((-53,14)).segment((-99,14)).segment((-99,11)).close().assemble().reset().face(w0.sketch().segment((-83,1),(-48,-15)).segment((-33,10)).segment((-68,26)).close().assemble(),mode='s').push([(59.5,-4.5)]).rect(27,5,mode='s').finalize().extrude(2)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0083_00838161.step')

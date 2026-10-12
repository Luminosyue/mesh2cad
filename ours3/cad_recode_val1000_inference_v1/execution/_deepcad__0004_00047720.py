import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(-23,0,0))
w1=cq.Workplane('XY',origin=(0,0,35))
r=w0.sketch().segment((-88,30),(-44,30)).segment((-50,4)).segment((-23,-1)).segment((-18,30)).segment((-15,30)).segment((-15,44)).segment((-18,44)).segment((-64,89)).segment((-88,67)).close().assemble().reset().face(w0.sketch().segment((-88,-100),(88,-100)).segment((88,-57)).segment((87,-57)).segment((87,-84)).segment((50,-84)).segment((50,-92)).segment((42,-92)).segment((42,-84)).segment((14,-84)).segment((14,-62)).segment((88,-62)).segment((88,-57)).segment((88,-56)).segment((88,-55)).segment((88,-54)).segment((88,-53)).segment((88,-52)).segment((87,-52)).segment((87,-56)).segment((83,-56)).segment((83,-49)).segment((14,-24)).segment((14,-8)).segment((-88,-8)).close().assemble()).finalize().extrude(46).union(w0.sketch().segment((-89,19),(-35,19)).segment((-35,40)).segment((-4,35)).segment((0,30)).segment((1,31)).segment((-88,100)).close().assemble().finalize().extrude(46)).union(w1.sketch().arc((-20,49),(-10,2),(23,38)).arc((-2,31),(-20,49)).assemble().finalize().extrude(-43))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0004_00047720.step')

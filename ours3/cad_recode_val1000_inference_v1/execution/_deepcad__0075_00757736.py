import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-6))
r=w0.sketch().segment((-69,-88),(-58,-88)).segment((-58,-100)).segment((78,-100)).segment((78,-88)).segment((96,-88)).segment((96,100)).segment((-48,100)).segment((-48,88)).segment((-35,88)).arc((-19,92),(-3,88)).segment((83,88)).segment((83,-87)).segment((-5,-88)).segment((-5,-92)).segment((-56,-92)).segment((-56,9)).segment((-64,9)).segment((-64,10)).segment((-69,10)).close().assemble().push([(23,-39)]).rect(120,98,mode='s').finalize().extrude(6).union(w0.sketch().segment((-96,91),(-91,89)).segment((-91,90)).segment((-69,90)).segment((-69,93)).segment((-47,93)).segment((-47,87)).segment((-35,87)).segment((-35,88)).segment((-91,94)).close().assemble().reset().face(w0.sketch().segment((-65,-92),(87,-96)).segment((88,-92)).segment((-60,-92)).segment((-60,-57)).segment((-64,-57)).close().assemble()).push([(89.5,10)]).rect(5,150).finalize().extrude(12))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0075_00757736.step')

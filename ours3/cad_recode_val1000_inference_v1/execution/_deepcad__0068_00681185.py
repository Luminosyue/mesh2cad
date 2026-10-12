import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-6))
r=w0.sketch().segment((-100,-62),(-68,-62)).segment((-68,-100)).segment((-66,-100)).segment((-66,-62)).segment((-56,-62)).segment((-56,-35)).segment((-10,-58)).segment((-10,-34)).segment((-13,-34)).segment((-13,12)).segment((-10,12)).segment((-10,28)).segment((12,28)).segment((12,12)).segment((15,12)).segment((15,-34)).segment((12,-34)).segment((12,-49)).segment((40,-64)).segment((40,-100)).segment((68,-100)).segment((68,-88)).segment((90,-98)).segment((100,-74)).segment((100,16)).segment((100,93)).segment((68,93)).segment((68,100)).segment((40,100)).segment((40,93)).segment((12,93)).segment((12,100)).segment((-10,100)).segment((-10,93)).segment((-23,93)).segment((-23,81)).segment((-45,92)).segment((-68,42)).segment((-68,100)).segment((-100,100)).close().assemble().push([(-60,-10)]).circle(20,mode='s').push([(-19,-84)]).rect(26,32).push([(69,16)]).circle(31).finalize().extrude(12)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0068_00681185.step')

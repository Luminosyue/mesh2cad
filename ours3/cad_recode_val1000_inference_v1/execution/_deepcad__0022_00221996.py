import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,9))
r=w0.sketch().segment((-97,16),(-96,15)).arc((-96,-21),(-81,-53)).segment((-81,-27)).segment((-38,-27)).arc((-45,10),(-29,40)).arc((-10,45),(8,45)).arc((14,45),(20,44)).segment((76,44)).arc((67,61),(55,76)).segment((55,82)).segment((49,82)).arc((10,98),(-30,92)).segment((-31,93)).segment((-32,91)).arc((-67,73),(-87,39)).segment((-90,37)).segment((-90,36)).arc((-94,25),(-97,16)).assemble().reset().face(w0.sketch().arc((-61,-77),(-14,-97),(36,-90)).segment((19,-41)).arc((-14,-45),(-38,-26)).segment((-38,-77)).close().assemble()).reset().face(w0.sketch().segment((43,89),(90,-42)).arc((91,31),(43,89)).assemble()).reset().face(w0.sketch().arc((44,-89),(60,-78),(73,-64)).close().assemble()).finalize().extrude(-18)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0022_00221996.step')

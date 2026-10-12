import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-2))
r=w0.sketch().segment((-100,-32),(-79,-32)).segment((-97,-84)).segment((-68,-96)).segment((-45,-32)).segment((-31,-32)).segment((-31,-96)).segment((-7,-96)).segment((-7,-32)).segment((14,-32)).segment((14,-16)).segment((49,-16)).segment((49,-32)).segment((73,-32)).segment((73,-55)).segment((100,-55)).segment((100,13)).segment((99,13)).segment((99,84)).segment((73,84)).segment((73,91)).segment((49,91)).segment((49,84)).segment((37,84)).segment((37,96)).segment((-21,96)).segment((-21,77)).segment((-98,77)).segment((-98,48)).segment((-74,48)).segment((-74,37)).segment((-100,37)).close().assemble().reset().face(w0.sketch().segment((-74,-16),(-74,13)).segment((-41,13)).arc((-21,40),(12,37)).segment((12,13)).segment((37,13)).segment((37,-16)).segment((12,-16)).segment((12,-26)).arc((-21,-38),(-45,-16)).close().assemble(),mode='s').push([(63,26)]).circle(19,mode='s').push([(63,-84)]).circle(12).finalize().extrude(4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0027_00273567.step')

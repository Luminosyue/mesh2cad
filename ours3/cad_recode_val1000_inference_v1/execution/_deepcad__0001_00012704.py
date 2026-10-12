import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,79))
w1=cq.Workplane('YZ',origin=(21,0,0))
r=w0.sketch().segment((-100,-72),(-94,-72)).segment((-94,-79)).segment((59,-79)).segment((59,79)).segment((-94,79)).segment((-94,72)).segment((-100,72)).close().assemble().finalize().extrude(-169).union(w0.sketch().segment((-95,30),(-77,-10)).segment((-77,-47)).segment((-61,-47)).segment((-51,-69)).segment((10,-40)).segment((10,-79)).segment((59,-79)).segment((59,-14)).segment((100,5)).segment((82,45)).segment((82,18)).segment((59,18)).segment((59,69)).segment((10,69)).segment((10,38)).segment((-10,24)).segment((-10,63)).segment((-59,63)).segment((-59,28)).segment((-61,32)).segment((-61,79)).segment((-77,79)).segment((-77,34)).close().assemble().finalize().extrude(1)).union(w1.workplane(offset=27/2).moveTo(13,86).cylinder(27,5))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0001_00012704.step')

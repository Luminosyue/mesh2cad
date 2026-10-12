import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(45,0,0))
r=w0.sketch().arc((-99,12),(-50,-86),(56,-83)).arc((36,-50),(70,-61)).arc((71,69),(-53,85)).arc((-34,11),(-99,12)).assemble().finalize().extrude(-90).union(w0.sketch().arc((-65,76),(-99,-13),(-45,-90)).segment((-45,-93)).segment((-37,-92)).arc((13,-98),(58,-81)).segment((66,-80)).segment((66,-76)).arc((99,13),(55,83)).segment((55,86)).segment((47,85)).arc((-5,91),(-59,74)).segment((-65,74)).close().assemble().reset().face(w0.sketch().segment((-58,60),(-55,51)).segment((-55,60)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-45,-60),(-39,-60)).segment((-45,-51)).close().assemble(),mode='s').finalize().extrude(-76))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0074_00742620.step')

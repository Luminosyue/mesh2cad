import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,13))
w1=cq.Workplane('XY',origin=(0,0,13))
r=w0.sketch().segment((-74,29),(-62,11)).segment((-48,20)).segment((-59,31)).segment((-59,32)).segment((-60,32)).segment((-61,33)).segment((-74,32)).close().assemble().reset().face(w0.sketch().segment((-45,0),(-1,-45)).segment((1,-43)).segment((-40,4)).close().assemble()).reset().face(w0.sketch().segment((30,-2),(40,-18)).segment((92,26)).segment((87,33)).close().assemble()).finalize().extrude(-26).union(w0.sketch().segment((-100,20),(-85,20)).segment((-85,26)).segment((-78,26)).segment((-78,20)).segment((-74,20)).segment((-74,26)).segment((-55,26)).segment((-96,46)).segment((-100,46)).close().assemble().reset().face(w0.sketch().segment((-66,15),(-25,-8)).segment((-21,-2)).segment((-52,20)).segment((-55,20)).close().assemble()).finalize().extrude(-13)).union(w1.sketch().arc((2,-46),(19,-29),(2,-12)).close().assemble().finalize().extrude(-25))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0043_00437238.step')

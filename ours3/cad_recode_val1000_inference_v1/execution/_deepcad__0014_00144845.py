import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,94))
w1=cq.Workplane('XY',origin=(0,0,30))
r=w0.sketch().segment((-85,-86),(-61,-86)).segment((-61,-47)).segment((-29,-47)).segment((-29,-78)).segment((1,-78)).arc((23,-87),(46,-86)).segment((94,-86)).segment((94,-65)).segment((86,-65)).segment((86,-43)).segment((94,-43)).segment((94,12)).segment((86,12)).segment((86,13)).segment((94,13)).segment((94,65)).segment((86,65)).segment((86,92)).segment((24,92)).segment((24,90)).segment((-31,90)).segment((-31,88)).segment((-85,92)).segment((-85,45)).segment((-61,33)).segment((-61,83)).segment((-85,83)).segment((-85,42)).segment((-61,38)).segment((-61,12)).segment((-85,12)).segment((-85,-17)).arc((-80,-10),(-74,-4)).segment((-61,-11)).segment((-61,-25)).segment((-74,-18)).arc((-80,-12),(-85,-6)).close().assemble().push([(12,5)]).circle(35,mode='s').finalize().extrude(6).union(w1.sketch().segment((-94,-92),(-79,-92)).arc((-86,-88),(-94,-92)).assemble().finalize().extrude(-122))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0014_00144845.step')

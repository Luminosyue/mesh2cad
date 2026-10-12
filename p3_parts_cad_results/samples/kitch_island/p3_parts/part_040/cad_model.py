"""Standalone mesh-derived faceted CAD; not a recovered parametric feature tree."""
VERTICES=[[0.95603448, 0.01427545, -0.02034074], [0.95603448, 0.01428087, -0.01220426], [0.95603448, 0.01428628, -0.00406789], [0.95811564, 0.02034269, -0.02847723], [0.95810223, 0.02034269, -0.02034074], [0.95808905, 0.02034269, -0.01220426], [0.95812839, 0.02847917, -0.02847723], [0.95811492, 0.02847917, -0.02034074], [0.95810175, 0.02847917, -0.01220426], [0.95808834, 0.02847917, -0.00406789], [0.95814109, 0.03661554, -0.02847723], [0.95812768, 0.03661554, -0.02034074], [0.95811445, 0.03661554, -0.01220426], [0.95810103, 0.03661554, -0.00406789], [0.95808786, 0.03661554, 0.0040686], [0.95815378, 0.04475202, -0.02847723], [0.95814061, 0.04475202, -0.02034074], [0.9581272, 0.04475202, -0.01220426], [0.95811397, 0.04475202, -0.00406789], [0.95810032, 0.04475202, 0.0040686], [0.95808715, 0.04475202, 0.01220496], [0.95807374, 0.04475202, 0.02034145], [0.95816654, 0.05288851, -0.02847723], [0.95815331, 0.05288851, -0.02034074], [0.9581399, 0.05288851, -0.01220426], [0.95812672, 0.05288851, -0.00406789], [0.95811331, 0.05288851, 0.0040686], [0.95809984, 0.05288851, 0.01220496], [0.95816606, 0.06102488, -0.02034074], [0.95815265, 0.06102488, -0.01220426], [0.95813918, 0.06102488, -0.00406789], [0.95812601, 0.06102488, 0.0040686], [0.95817876, 0.06916136, -0.02034074]]
FACES=[[32, 29, 28], [28, 24, 23], [28, 29, 24], [29, 25, 24], [29, 30, 25], [30, 26, 25], [30, 31, 26], [31, 27, 26], [6, 4, 3], [6, 7, 4], [7, 5, 4], [7, 8, 5], [10, 7, 6], [10, 11, 7], [11, 8, 7], [11, 12, 8], [12, 9, 8], [12, 13, 9], [0, 4, 1], [1, 4, 5], [1, 5, 2], [0, 3, 4], [22, 16, 15], [22, 23, 16], [23, 17, 16], [23, 24, 17], [24, 18, 17], [24, 25, 18], [25, 19, 18], [25, 26, 19], [26, 20, 19], [26, 27, 20], [27, 21, 20], [15, 11, 10], [15, 16, 11], [16, 12, 11], [17, 13, 12], [17, 18, 13], [18, 19, 14], [16, 17, 12]]
TOLERANCE=5.488591e-09

from pathlib import Path
import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing
from OCP.ShapeFix import ShapeFix_Shape, ShapeFix_Solid
UNIT_SCALE=1.0  # original STL numerical coordinates, unknown physical units
def build_model():
    sew=BRepBuilderAPI_Sewing(TOLERANCE)
    for face in FACES:
        points=[cq.Vector(*VERTICES[i]) for i in face]
        sew.Add(cq.Face.makeFromWires(cq.Wire.makePolygon(points,close=True)).wrapped)
    sew.Perform()
    fixer=ShapeFix_Shape(sew.SewedShape());fixer.Perform()
    shape=cq.Shape.cast(fixer.Shape())
    shells=shape.Shells()
    # Only promote genuinely closed shells. Open shells remain surface CAD.
    if shells and sum(len(s.Faces()) for s in shells)==len(shape.Faces()):
        parts=[]
        for shell in shells:
            if shell.Closed():
                solid=cq.Solid.makeSolid(shell)
                sf=ShapeFix_Solid(solid.wrapped);sf.Perform()
                candidate=cq.Shape.cast(sf.Solid())
                parts.append(candidate if candidate.isValid() else shell)
            else: parts.append(shell)
        shape=parts[0] if len(parts)==1 else cq.Compound.makeCompound(parts)
    return shape.scale(UNIT_SCALE) if UNIT_SCALE!=1 else shape
if __name__=='__main__':
    result=build_model()
    cq.exporters.export(result,str(Path(__file__).with_name('model.step')))
    print({'valid':result.isValid(),'faces':len(result.Faces()),'solids':len(result.Solids())})
elif 'show_object' in globals():
    show_object(build_model())

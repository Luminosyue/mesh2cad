# V12 experimental implementation diff

Added isolated module `chamfer_v12.py` (not imported by canonical V11):

- `Box(width,height,depth)` and `Chamfer(body,distance)` AST nodes.
- Deterministic parser and canonical serializer with parse/serialize/parse equality.
- Real OCC `BRepFilletAPI_MakeChamfer` executor; all deterministically enumerated solid edges receive one symmetric distance.
- Positive-distance and body-reference validation.
- BRep validity and geometry statistics.
- STEP export and reload helper.

No canonical V11 file, dataset, P1 checkpoint, prediction, or evaluator was modified.

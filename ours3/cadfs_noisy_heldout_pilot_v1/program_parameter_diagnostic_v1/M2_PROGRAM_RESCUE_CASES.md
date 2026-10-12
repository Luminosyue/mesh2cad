# M2 Program Rescue Cases

Existing paired OpF1 definition selected exactly these three cases.

## cadfs__00826947

M2_RESOLVED_ERROR: removed extra operation(s), corrected operation/profile primitive type

```text
GT:
# CADFS FeatureScript → V4 canonical CAD DSL (lossless subset)
body_0 = ExtrudePolygon(points=[(-0.666429, -1.066286), (0.666429, -1.066286), (2.799001, 1.066286), (-2.799001, 1.066286)], height=0.3732, axis=(0, 0, 1), origin=(2.797505, 1.066286, 0.0), x_axis=(1, 0, 0))
result = body_0

B0:
# CADFS FeatureScript → V4 canonical CAD DSL (lossless subset)
body_0 = Extrude(Circle(radius=2.118068), height=0.353011, axis=(0, 0, 1), origin=(2.117937, 2.117514, 0.0))
result = body_0

M2:
# CADFS FeatureScript → V4 canonical CAD DSL (lossless subset)
body_0 = ExtrudePolygon(points=[(0.0, 0.0), (-5.807685, 0.0), (-5.807685, 1.468477), (0.0, 1.468477)], height=0.346884, axis=(0, 0, 1), origin=(5.807159, 0.0, 0.0), x_axis=(1, 0, 0))
result = body_0
```

## cadfs__00830309

M2_RESOLVED_ERROR: recovered missing operation(s), corrected operation/profile primitive type

```text
GT:
# CADFS FeatureScript → V4 canonical CAD DSL (lossless subset)
body_0 = Extrude(Circle(radius=2.121769), height=0.127306, axis=(0, 0, 1), origin=(2.11953, 2.121462, 0.0))
result = body_0

B0:
# CADFS FeatureScript → V4 canonical CAD DSL (lossless subset)
body_0 = ExtrudePolygon(points=[(-3.853795, 3.046349), (0.945538, 3.046349), (0.945538, -0.553152), (-3.853795, -0.553152)], height=0.099986, axis=(0, 0, 1), origin=(3.853865, 0.553123, 0.0), x_axis=(1, 0, 0))
result = body_0

M2:
# CADFS FeatureScript → V4 canonical CAD DSL (lossless subset)
body_0 = Extrude(Circle(radius=2.124149), height=0.070805, axis=(0, 0, 1), origin=(2.122956, 2.117655, 0.0))
result = body_0
```

## cadfs__00984691

M2_RESOLVED_ERROR: recovered missing operation(s), corrected operation/profile primitive type

```text
GT:
# CADFS FeatureScript → V4 canonical CAD DSL (lossless subset)
body_0 = Extrude(Circle(radius=0.104453), height=5.992724, axis=(0, 1, 0), origin=(0.104437, 0.0, 0.104435))
result = body_0

B0:
# CADFS FeatureScript → V4 canonical CAD DSL (lossless subset)
body_0 = ExtrudePolygon(points=[(0.0, 0.0), (5.364632, 0.0), (5.364632, 2.682316), (0.0, 2.682316)], height=0.160939, axis=(0, 0, 1), origin=(0.0, 0.0, 0.0), x_axis=(1, 0, 0))
result = body_0

M2:
# CADFS FeatureScript → V4 canonical CAD DSL (lossless subset)
body_0 = Extrude(Circle(radius=0.486665), height=5.839977, axis=(0, 0, 1), origin=(0.486662, 0.48666, 0.0))
result = body_0
```

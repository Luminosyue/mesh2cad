# Backend probe

The server environment provides `OCP.BRepFilletAPI.BRepFilletAPI_MakeChamfer`.

Constructor: `BRepFilletAPI_MakeChamfer(shape)`.

Symmetric operation: `Add(distance, edge)` followed by `Build()`; `IsDone()` and `Shape()` provide the result. `TopoDS.Edge_s` is required for explorer results.

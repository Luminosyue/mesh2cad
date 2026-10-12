# FutureCAD Grounding Integration Pipeline

```text
Original OBJ -> P3-SAM -> PhysX -> CAD Part Graph -> Geometry Analyzer
-> Semantic Surface / Feature Graph -> Dual-Modal Mesh Context
-> Candidate Generation [V6GeometryBackend | V11 Planner | MAC optional]
-> Base Part BRep -> Structured Feature Program
-> Primitive Grounding Resolver [Deterministic V1: IMPLEMENTED]
                              [FutureCAD BRepGround: FUTURE BACKEND]
-> Transient BRep Feature Loop -> Candidate Verification
-> Nativeness / Geometry QA -> Topology Hybrid -> XCAF -> STEP
```

- IMPLEMENTED: inventory, descriptors, query schema/parser, deterministic grounder, resolver, feature loop, provenance.
- INTERFACE_READY: `PrimitiveGroundingBackend` and `FutureCADToV11Adapter`.
- FUTURE: official FutureCAD BRepGround backend or a trained project-specific grounding model.

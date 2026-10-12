from OCP.BRep import BRep_Builder
from OCP.BRepTools import BRepTools_ReShape

print(BRepTools_ReShape)
print([name for name in dir(BRep_Builder) if "UpdateEdge" in name])

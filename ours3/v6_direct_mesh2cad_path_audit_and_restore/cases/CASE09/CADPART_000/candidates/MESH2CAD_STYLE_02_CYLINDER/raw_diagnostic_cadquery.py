from cadquery import Workspace, Cylinder, Boolean
base = Cylinder(radius=0.5, height=1.0, center=(0, 0, 0))
cut = mesh_to_cadquery()
result = base.cut(cut)
print(result)
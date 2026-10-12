from cadquery import Workspace, Plane, Extrusion
plane = Plane((0, 0, 0), (1, 0, 0), (0, 1, 0))
extrusion = Extrusion(plane, mesh_data)
result = extrusion.to_mesh()
print(result)
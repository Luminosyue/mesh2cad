from cadquery import Workspace, Revolution
profile = mesh_to_profile()
revolution = Revolution(profile, axis=(0, 0, 1), angle=360)
result = revolution.to_mesh()
print(result)
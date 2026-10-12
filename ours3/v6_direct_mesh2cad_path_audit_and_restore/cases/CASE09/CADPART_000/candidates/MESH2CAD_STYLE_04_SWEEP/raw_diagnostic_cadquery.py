from cadquery import Workspace, Sweep
profile = mesh_to_profile()
sweep_path = Path((0, 0, 0), (1, 0, 0))
result = Sweep(profile, sweep_path)
print(result)
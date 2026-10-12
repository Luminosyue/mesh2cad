# Historical Fusion360 canonicalization dataflow

`raw JSON -> program.dsl`

`raw OBJ -> STL -> Dora sampler -> features.npy`

`features[:,0:3] min/max -> scale + translation -> coordinate_transform.json`

`program.dsl + transform -> program_canonical.dsl`

Raw STEP is copied as official geometry but is not read by historical `compute_transform`. Only geometric XYZ is used from Dora output.

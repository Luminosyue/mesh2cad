# HY3D Part Watertight Audit V1

## Dataset

NPZ root: /data/home/cuiyuehan/project/mesh2cad/mesh2cad. The first 100 files in full-path lexical order were audited. They contain 64 recognized part keys.

## NPZ schema

The first NPZ contains uint8-encoded PLY bytes with one `full.ply` key and `part_N.ply` keys. Full meshes were excluded from part statistics. Unknown keys are preserved in NPZ100_MANIFEST.csv. 89 of the fixed NPZ100 could not be opened and were not replaced.

## Watertight audit

64 parts loaded successfully. Strict valid: 15/64 (0.234375). NOT_WATERTIGHT=49, NOT_VOLUME=49, BOUNDARY_EDGES=0, NONMANIFOLD_EDGES=49.

## Pilot20

Pilot count=0, unique objects=0, independent recheck=0/0. Actual category distribution: {}.

## Data integrity

Extracted PLY files are byte-for-byte copies decoded from NPZ arrays. SHA-256 is recorded. No repair, remesh, simplification, smoothing, welding, hole filling, or source mutation was performed.

## Conclusion

The fixed NPZ100 sample did not satisfy the strict gate; watertight criteria were not relaxed.

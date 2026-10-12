# V3 CAD visualization and assembly previews

Open index.html for all 20 objects. Every object has source/CAD comparison, assembled view, reverse view, status coloring, and exploded view. The 209 current V3 CAD part meshes are transformed by their recorded world_transform into the original object canonical frame. No new fitting or geometry changes are made. Exploded-view offsets are display-only.

All candidates are included, including Near and Reject; these are diagnostic previews, not accepted complete CAD assemblies. Status images use green Strict, amber Near, red Reject. GLB scenes use distinct part colors and preserve part names/statuses. They can be opened in a 3D viewer. PLY exports provide the assembled mesh. Neither GLB nor PLY is a Boolean-fused STEP solid.

Rendering uses deterministic area-sampled points with normal shading and a shared source/CAD camera and scale. This makes fitting errors visible without changing the source or CAD inputs. Per-object manifests record all transforms, input hashes and statuses.

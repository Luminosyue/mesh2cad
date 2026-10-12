# BRep surface type audit

STEP 文件用 OpenCascade `STEPControl_Reader` 直接读入，没有经过 CadQuery 重建，也没有改几何。`BREP_FACE_N` 是拓扑面数。`DISPLAY_TESSELLATION_TRIANGLE_N` 是同一实体在显示容差下的三角剖分数，容差与 v1 teaser 相同：线性偏差 `max(对角线 × 0.0012, 1e-4)`，角度偏差 `0.12 rad`。这两组数字不是一回事。

## Gate

`TRIANGLES_ARE_RENDER_TESSELLATION=TRUE`

`FACETED_BREP=FALSE`

六个文件都是 1 个有效 solid、1 个 shell。平面三角面数量都是 0。BRep 面是十几到几十个，其中绝大多数是 `BSplineSurface`。显示三角数是面数的大约 1000 倍。图上的三角线来自显示剖分，不是 CAD 面。几何没有改。

判定规则：平面三角面不少于 200 且占全部 BRep 面 80% 以上，记为 `FACETED_BREP`。否则，只要存在曲面且显示三角数不少于 BRep 面数的 8 倍，记为 `TRIANGLES_ARE_RENDER_TESSELLATION`。

## PART_000

| | Generated | Canonical |
|---|---:|---:|
| STEP | `airplane3_fullseq_14bit_ir_v1/frozen_success_v1/step/PART_000.step` | `airplane3_fullseq_14bit_ir_v1/dataset/DeepCAD/geometry_pack_v1/airplane__PART_000/target.step` |
| BRep valid | TRUE | TRUE |
| solid count | 1 | 1 |
| shell count | 1 | 1 |
| BREP_FACE_N | 18 | 18 |
| edge count | 68 | 68 |
| Plane | 2 | 2 |
| Cylinder | 0 | 0 |
| Cone | 0 | 0 |
| Sphere | 0 | 0 |
| Torus | 0 | 0 |
| BSplineSurface | 16 | 16 |
| BezierSurface | 0 | 0 |
| SurfaceOfRevolution | 0 | 0 |
| SurfaceOfExtrusion | 0 | 0 |
| OffsetSurface | 0 | 0 |
| Other | 0 | 0 |
| plane triangular faces | 0 | 0 |
| DISPLAY_TESSELLATION_TRIANGLE_N | 32892 | 30616 |

面的边界边数：16 个面各 4 条边，2 个面各 2 条边。没有 3 边平面。

## PART_001

| | Generated | Canonical |
|---|---:|---:|
| STEP | `airplane3_fullseq_14bit_ir_v1/frozen_success_v1/step/PART_001.step` | `airplane3_fullseq_14bit_ir_v1/dataset/DeepCAD/geometry_pack_v1/airplane__PART_001/target.step` |
| BRep valid | TRUE | TRUE |
| solid count | 1 | 1 |
| shell count | 1 | 1 |
| BREP_FACE_N | 22 | 22 |
| edge count | 82 | 82 |
| Plane | 2 | 2 |
| Cylinder | 0 | 0 |
| Cone | 0 | 0 |
| Sphere | 0 | 0 |
| Torus | 0 | 0 |
| BSplineSurface | 20 | 20 |
| BezierSurface | 0 | 0 |
| SurfaceOfRevolution | 0 | 0 |
| SurfaceOfExtrusion | 0 | 0 |
| OffsetSurface | 0 | 0 |
| Other | 0 | 0 |
| plane triangular faces | 0 | 0 |
| DISPLAY_TESSELLATION_TRIANGLE_N | 53730 | 53842 |

面的边界边数：20 个面各 4 条边，2 个面各 1 条闭合边。没有 3 边平面。

## PART_005

| | Generated | Canonical |
|---|---:|---:|
| STEP | `airplane3_fullseq_14bit_ir_v1/frozen_success_v1/step/PART_005.step` | `airplane3_fullseq_14bit_ir_v1/dataset/DeepCAD/geometry_pack_v1/airplane__PART_005/target.step` |
| BRep valid | TRUE | TRUE |
| solid count | 1 | 1 |
| shell count | 1 | 1 |
| BREP_FACE_N | 42 | 42 |
| edge count | 162 | 162 |
| Plane | 2 | 2 |
| Cylinder | 0 | 0 |
| Cone | 0 | 0 |
| Sphere | 0 | 0 |
| Torus | 0 | 0 |
| BSplineSurface | 40 | 40 |
| BezierSurface | 0 | 0 |
| SurfaceOfRevolution | 0 | 0 |
| SurfaceOfExtrusion | 0 | 0 |
| OffsetSurface | 0 | 0 |
| Other | 0 | 0 |
| plane triangular faces | 0 | 0 |
| DISPLAY_TESSELLATION_TRIANGLE_N | 54236 | 53398 |

面的边界边数：40 个面各 4 条边，2 个面各 1 条闭合边。没有 3 边平面。

## v1 图上的线从哪来

`paper_teaser_demo_v1/scripts/build_teaser_demo.py` 先调用 `shape.tessellate(...)`，再把超过 30000 的三角形抽成 30000 个，然后把只出现一次的网格边画出来。PART_000 的显示网格有 32088 个三角形、46880 条内部边、2504 条未焊接边界边；抽稀之后邻接被拆开，三角边被画进了图里。拓扑边只有 34 条（`TopExp.MapShapes` 去重）。那些三角线是显示剖分，不是 BRep face。

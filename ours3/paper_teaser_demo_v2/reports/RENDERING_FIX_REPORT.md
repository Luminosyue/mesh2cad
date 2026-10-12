# Rendering fix report

`TRIANGLES_ARE_RENDER_TESSELLATION=TRUE`，所以 CAD 几何没有改。Generated / Canonical 重新按 smooth BRep 渲染。

`NO_TRIANGLE_WIREFRAME=TRUE`

`NO_MESH_EDGES=TRUE`

`SMOOTH_SHADED_SURFACE=TRUE`

这三项只针对 Generated CAD 和 Canonical CAD。Input Mesh 仍然画出三角边。

## 回答

1. v1 图里的三角线来自 display tessellation。六个 STEP 的平面三角面都是 0。v1 脚本把 STEP tessellate 之后，把超过 30000 的三角形抽成 30000 个，再把未共享顶点的网格边画出来。PART_000 generated 的显示网格有 32088 个三角形；抽稀前内部边 46880、边界边 2504，拓扑上的 BRep 边只有 34 条。

2. BRep face 数，generated 与 canonical 相同：PART_000 是 18，PART_001 是 22，PART_005 是 42。

3. BSplineSurface 数，generated 与 canonical 相同：PART_000 是 16，PART_001 是 20，PART_005 是 40。其余面各有 2 个 Plane。

4. 显示剖分三角数（线性偏差 = 对角线 × 0.0012，角度偏差 0.12 rad）：

| Part | Generated | Canonical |
|---|---:|---:|
| PART_000 | 32892 | 30616 |
| PART_001 | 53730 | 53842 |
| PART_005 | 54236 | 53398 |

5. Generated CAD 是真正的 smooth BRep。三件都是 `BRepCheck` 有效的 1 solid / 1 shell，主体是 BSpline 曲面，不是三角平面拼出来的壳。

6. 最终图上 Generated / Canonical / Overlay 不画任何边，包括 BRep 截面边界。`drawn_segments=0`。着色用的细网格也不画边。三角 mesh edges 只留在 Input Mesh。整体图是 `teaser/airplane3_teaser_overview.png`。

7. Input Mesh 是灰色三角线网。Generated CAD 是青色光滑曲面加少量截面边界。Canonical CAD 是灰蓝色光滑曲面，边界规则相同。两者在视觉上分开。

## 渲染协议

三件共用：正交相机，方位角 -45°，仰角 25°，白底，1600×1600，同一盏主光 `[0.35, -0.20, 0.92]`。每个单件面板按投影包围盒放到画面宽度的 86%。Overlay 把 generated 和 canonical 放在同一个世界坐标系里再一起归一化，不各自缩放。

着色网格比显示审计更细（线性偏差 = 对角线 × 0.00028，角度偏差 0.045 rad），只用于 Phong 插值，不进入线框。PART_000 / 001 / 005 的 generated 着色三角数是 271604 / 611756 / 698998。这些数字不是 BRep face，也不是上面的 display tessellation。

Overlay 上偶尔露出的窄青色边是 generated 与 canonical 包围盒大约 2%–4% 的尺度差，两边中心几乎重合。画出的线仍是两边各自的 BRep 边。

## 输出

- `paper_teaser_demo_v2/renders/part000_input_mesh.png`
- `paper_teaser_demo_v2/renders/part000_generated_brep.png`
- `paper_teaser_demo_v2/renders/part000_canonical_brep.png`
- `paper_teaser_demo_v2/renders/part000_overlay.png`
- `paper_teaser_demo_v2/renders/part001_input_mesh.png`
- `paper_teaser_demo_v2/renders/part001_generated_brep.png`
- `paper_teaser_demo_v2/renders/part001_canonical_brep.png`
- `paper_teaser_demo_v2/renders/part001_overlay.png`
- `paper_teaser_demo_v2/renders/part005_input_mesh.png`
- `paper_teaser_demo_v2/renders/part005_generated_brep.png`
- `paper_teaser_demo_v2/renders/part005_canonical_brep.png`
- `paper_teaser_demo_v2/renders/part005_overlay.png`

审计表在 `reports/BREP_SURFACE_TYPE_AUDIT.md`。

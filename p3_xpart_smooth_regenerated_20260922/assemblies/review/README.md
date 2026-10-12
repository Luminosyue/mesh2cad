所有 77 个非 tank case 的 793 个 CAD 零件按原始数值坐标拼合，未施加额外配准或布尔合并。每个零件保持独立。

精确装配 STEP 位于服务器 `/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_regenerated_20260922/assemblies/<case>/assembly.step`。

四视图展示整体、部件分色、正视和拟合状态；橙色代表待改进零件。对比图左右保持同一坐标和比例。零件拟合误差仍会出现在装配中。

离线打开 index.html 浏览，进入每个 interactive.html 可旋转、缩放、隐藏零件、显示实际 B-Rep 边界或拆分查看。拆分滑块为 0 时是原始装配位置。交互显示网格经过简化，精确几何请使用 STEP。输入物理单位未确认。

Three.js 0.160.1 (MIT) 已内嵌，不需要联网；使用支持 WebGL 和 DecompressionStream 的现代 Chrome / Edge。

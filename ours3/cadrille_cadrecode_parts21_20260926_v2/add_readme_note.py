from pathlib import Path
p=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/cadrille_cadrecode_parts21_20260926_v2/finalize_run.py')
s=p.read_text()
s=s.replace("(delivery/'README.md').write_text('\\n'.join(lines),encoding='utf-8')", "lines += ['', '输入说明：沿用服务器已有 X-Part 完整/补全部件。本次没有重新训练分割模型。鸟屋、音箱、酒架的部件合并边界与原始整网格存在约 15%–22% 的最大边界偏差；详见 INPUT_COORDINATE_AUDIT.json。预览中的 Input 是实际送入两种方法的部件合并网格。', '', '编辑后重建：安装 CadQuery，在 scripts 目录运行 python regenerate_case.py ../cadrille/案例名（或 ../cadrecode/案例名），生成 edited_assembled.step。']\n(delivery/'README.md').write_text('\\n'.join(lines),encoding='utf-8')")
p.write_text(s)

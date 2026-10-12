# V3 encode() 真实截断打印  arm=M2

公式: allowance=max(32, 4096 - geometry_extra - prompt)
geometry_extra=B1.total_llm_input_length - k_valid + 8
这就是 target=tokenize(dsl+eos)[:allowance]

## fusion360__63539_dd7fddaa_0005
geometry_extra=3070 prompt=36 allowance=990
GT+EOS=19289 kept=990 cut=18299
kept has result=False EOS=False
cut  has result=True EOS=True
file: /data/home/cuiyuehan/project/mesh2cad/ours3/v3_sft_chain_audit_v2/truncation_prints/fusion360__63539_dd7fddaa_0005.txt

## fusion360__30400_8824ce97_0007
geometry_extra=2340 prompt=36 allowance=1720
GT+EOS=10874 kept=1720 cut=9154
kept has result=False EOS=False
cut  has result=True EOS=True
file: /data/home/cuiyuehan/project/mesh2cad/ours3/v3_sft_chain_audit_v2/truncation_prints/fusion360__30400_8824ce97_0007.txt

## fusion360__109232_04340d62_0014
geometry_extra=3915 prompt=36 allowance=145
GT+EOS=7179 kept=145 cut=7034
kept has result=False EOS=False
cut  has result=True EOS=True
file: /data/home/cuiyuehan/project/mesh2cad/ours3/v3_sft_chain_audit_v2/truncation_prints/fusion360__109232_04340d62_0014.txt

## fusion360__50409_4a322fbf_0009
geometry_extra=2637 prompt=36 allowance=1423
GT+EOS=4797 kept=1423 cut=3374
kept has result=False EOS=False
cut  has result=True EOS=True
file: /data/home/cuiyuehan/project/mesh2cad/ours3/v3_sft_chain_audit_v2/truncation_prints/fusion360__50409_4a322fbf_0009.txt


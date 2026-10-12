"""Standalone mesh-derived CAD code, with embedded vertex and triangle data.

This reconstructs a faceted BREP, not an inferred sketch/extrusion feature tree.
Original numeric coordinates are retained; physical STL units are unknown.
Open meshes remain CAD surfaces. No guessed closures or thickness are added.
Run: python part_XXX_cad.py [--output-directory PATH] [--no-validate]
"""
from pathlib import Path
import argparse,base64,io,json,time,zlib
import numpy as np
import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/844fc9a82f46421c9f10804bd8055212/part_008.stl', 'relative_path': '844fc9a82f46421c9f10804bd8055212/part_008.stl', 'source_sha256': '1fb4a28c78c1f2af2057cf8178279f6952587faeaf031f682be926fc73cb5c27', 'input_faces': 916, 'input_vertices': 531, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1571688950061798, -0.1616302728652954, -0.21422594785690308], [-0.13564106822013855, -0.0541485920548439, 0.004082661122083664]]}
GEOMETRY_BASE85 = 'c$}r22b2^=yN0_LOn?$ZF+2Pqh~yk3jN}|eG7L#TV97`j7(fw0f<!@q0VFR`!tRoqpt!pr2qsW)6cJR!h!OR6O+7W+Rnz}D_uM<4I`3Q0S6f|OUv<^Y>|*O?IdT@X<g2jtX`Q8O8dtC^QSw*?t<imlj~vju?}#$VL&w@yz8DuTrSn_1Z_&DwZH>0Z7w^+|MDO9nYXpkde7aikQi0-64;emkc+cb>Lx%V1D|o}6gGTgq`H22KhxT>rk5;Z&zEq%MiBf?Hf&b$xmpg>u0}mZND75pky+W<fkPR`Net(QRt-g!#K$Df3UT(q7_QB#;Vmwr4OQs)>ZeFPIa52f9>#H{SaqH)x#seRokMYQ))J$JqV1|C(4<vVL9N*x_t!V}H{@=-x{Y*QQ>C4+s(Rk>X<l(1&*x<*5^L}3M<<Up>NWS&$Oh0a29Iszj@jr5I^y86ZXSM#VE;5hddKsC1+<A4JK0oB$X_9xNAGcP#uk{})I?Z?dikst)6q)8be#ISQ{DCRM{O4bBbN(j}^PhjXIsbu?J^a^?;>P+3jp*UKeiS#?Ph@sm-}SG!x&EWG+WM}4#m)5}`m>eq^BDP~mG(S_Hx!c3Z<Uh!yzLba+)*sXLzVaV@<`X28g~ZfkMZ!VOkW<#IY#5*F+a(9X!D6LkIv|?@o2>i*}mhKzC2RByT;XewyIw7<-snU_4{J|nEl7smC?WRUQ^%kD{hWIbfM&4zxh$zoFA)Zp}l_duedq?fk}C_yoY<-E%}ws2eiDyourn&JaD{9jEA-bHu>>Dz60yL+!|j>@*a0@^5ahE9j$#Z<Nf_HzIT0!FE91@TJ5@HGGjdY#1gH&1&^$4s<jVJ9k<`_zQVT+^yQJ}y=6cB7jE?9!46H<dwKM9yBH4@nz_-Bhu62$+6Qi}A=}r!uvr^FJh<_uHQM-_Rgm}lT87p>0C$?-r?n5%3dr_rS8np-&b_s?`FA?pDaVs@)+Rq5+1o~IAD*yV?hnOArTFpak^%bsmrB_upR+D0empX3y52r%bc{RoR&DX)!RKneq0L+J2zlL=v$Xcn!IC=-pVHb#f2tt+Y4Dde9tR#8e^H<R%+hinYx8M}FHcU=$Im$!YIkXi9}jOo<;#ORN^JIRe;}8hcX;5jvupggbNeoTUiHp5eEFb1R(pA9qTDwU?iU_0?l;;#*IwWGgolm!bk1d@$MUvH&sPL)<}1|jSd2%_^#C{5Lty&s7!Mfh&4N4Tddr$7`!UvY0B$YS*K_oT5-}b&pBK1eJTIZ#56XVl>Ca;j9yOlF@ZY&)``7j7Jp?zO_ed~@9FMV|gyH6X;*9z_Emk-7s|Y+|>{m{|k7C?0_d|Hd*bf7BPRDq_JV(kqzC3(txa4*9{X7JBjQu<`seg=H`;7BK@zVNv5jl}B#)HOr6oy+pjq~VA4mm&Oc?S=f=Uv0^Q+@9%^o7Q)s`-7--#9nUS(B@CR&n#(OyHcG@qUbRM{)DqiT7jd!zNeHU7Q>HUi`YoKBKt#T*vz{o@>R;b*{L%&g1<X>m=U4u}<RL$a{9a^t{KfYvk9tn%DPzh2rM>1e2@x35uKNvdPuCthjm3np~Z;@o`?6qP@?Lw_iL)=C|)#zTA3tqQ)b6JIHgB_sJ$#?~~*G80TpM=X{CJ&)6c87x^dCk2}frHEzwnB+tiXw`ckB=r5J@_UdzP-hx?vJUFF{K7Qj|R@^+7<L&o!@Ewoh3FG1Yym`NhoA+y;*YW<1^E#fF8egUR<_m7-E4t%oy5D+G+*}V%&-8S^b!DE*@%u8)<#_+bIUDcaIA`PBIM?F$Wt?mA@fhcnbLnRJTog#tp9{EET0Te7!Y6!rVCX1~tLH2Dz;$14IW2W=H`u4GLxacHA>7GxU9O*g#k2gl_1OLTI9bopqGhxEcxdpQTKnLJ2EP3(ZuTE({Cm3J_!UnWKkLMtAH~i22|V~py5IaOZq9$C>hsz<3|fC4iRtct_WAPlS0x|ukw1TUpvIlGdu6^3+?M6X!w=Tb`)Qag*H3b}EI%G7Qb2ECFOS?mzi*u7$Ahc>$nbKN$H=d3vix}HwI8(h(VNTf_3K~pg#L4$O!phV;^z26t0$-X&5z>d{6ubVneI3Lac<1NwV<|^U#su67&p&f#m)2A<m&uY+&q6xuFhY@&GXmf>ims!;~Y%j?Avi}oI8q}=Z@m$xe)KiI2Ypm82hv0=KdU?H)DT}&yTS`$GNdTD{k)3@$s0SBc^>L#~-b<-<x;Et=jVY4QpJ~mj`?G)_7#nW%<74TA?gI9$o#I-oE-Q**<@REI%F%|DB;-cmMq|kLkU#{J2y2bG^O#9{$k4EMI==L#=&aR^h#V{VQ(vAI`Te-EaJgo8u2>womt)AH~i23FP5(t}*|LoAVzXaI60OcE9BR{K6BSUwFcE3Qu?*6*r$d#m(mnp70#O6P_0}PV>1?<22WQ-9xe;^YftM=I23!$3G9k6Fv``Tzwu?{g|Hz;R&AyRX^tEL4(IXuPJVR9#q#gKM%qaJ`bvX%+G`HgwKQUgwKPjfAjO8>fii4sJQugFrF{t^Psw}@p&+O?>;%77soiU`|6?d@UOjmd9X`|7!P#cpW@4B6kDtHpH?@<L(eSN+DB6*54I2L?Hhb|Fc#nN=2oqJeaVA&m0Yb|cYjulI|aj9dkY@k)Lm;Io^&v_KBG%-*{<~ikIXn3(c14^6XW5D7q@wN2<{v%v{LJ*(X;yRDc}je*HG<Cwv*Q_QErnT4=&oWPV2|~eTTv0zwc1<U|p5(AGRLT=l|bt<vy0bkT(Abzwa=)`h5r7ncPG^r<?L@@#Eowr{B=}=~Q2~&y%6ezXgx9T(VrdFZ1^is=fL92z6g0s><Il99yCF@4&-7Yp>Aq+b%5M-zI&cjXwyt4&>0sZ+`!8@c8$=inE_Y@6WTtm)DJM_vJN;Z1v;u@9ow6nBS8dJha8}<&lv!m;3gUf7UW>otxiptMQoMZ!3O%U%KCX2H@s=M&G|l@^_4U!5t%C3EwBHJeuDptMPyTdz#;R3&NwudJ9+hQSPh8dJe%O#(GZpzBj&~7~l7*`)b@qes63%j}ds#d>+m3d*l0w@qMov&x7B@_W7u}pTNV$e)8YWg`oYmFL(Z35aSVJKa9YwBgTH1F+uXz^!+vfj~e@JXy&jzvG`s3ejbEJjs4uo(Rz=}yMA6o;1T1z2-n@UJN9$Nc@%<2%=74<nK2$V&b#Q}aO1oS9UB?rL37@wG}CynZMVa*>s3sW-=p-<xpiizyw35N+x)my?AS_;7d<2U%bR1Tmq&|89-g;%q1L|J$V0JlEpv8zxzkm0>(0?HXyeR1GIpL?H>Rd~c|h?y4i5J6u=?D$|DiPPy6W$6QXhTN%Y(HtWFC$FqctVB3h4b?bDoUdr?p%ke`GfNE`9t_YjJG-S^4z&2`j!ppPyiZb+PpnI$_K|+$wI&|B+#Gzfj-T6|5zBi)~td6%SqNB)>-t{Jzc0gYfW#YY{JZBISJh3GTelmq#~6<vMXTYW+Kk_nW=a%OkfPm+Q3QYg+p-JXm49-hNjP$xpw#Q@byCxXP4yULKh7yNp+_uC=$|!6hFr(C+K)%W}NQ4{PlM@bJ+(3$^RkJ{McJfkS8aXzk(F_npRS*Bw45#-jsrYwew3l3QCJo~q5m%Tr|kEidoZt_u&(2|lm2&pI#Pe+J%7)2<7*N^R><$9vsp=F0Y)KS|Z*0d6%P-AlXf3sYk}Fkpw)KKi`m))&kBY2#7P;}7G~{djQk_%uK69B8GFUp>EbSJv_6){sZN_Z95~|0{K<mxqs}$>-e|e*kWMrH?;wAw}-z#{4+vCAV7Z^ArBMtIVr0|IsUwTLFFkqh+hb)>+8NZx|kaMbB@v&qHz_c}8D9VR(4EzJ5Z-r@tBF#`?72)-U?{4DA~n+n0hv^!0DSt+$Q!A88Wfj`@5kzEpp{obwapb8bGr@L)Cl`3=`?5Zm{Hjr9E?2oF@$_XjKOC%GS*`%kLmR)2l}2`<j%yMKl+?bz(cts4bmJXBcUKb^lM4^Pzh&tSK-*!!V~I)5)b;=4a9Ztl;DoBOlk=6)FO$Jh_!+}N)aH}@;W&HW@keq%q0w>O@5#m(n2-rjg#;_Z#+B|d&*J;%pmtY^i|^%n2PSa0!ujQqy?G4dPFi;-Vv+~`Ao`BgmO{Dmi+zwm_fPW5A+cZ!?m5j^2Mf+w68YW(JTq1v1KIXq#%Rqf6FP_;MrLp6SLzf$8d_bYh9exmv@_Y>8R`TVMW%;#6-#mw*4uKxLjC*&8NkY9L0epNqaeib+K3s1-|JR!eo{APYtdo#cAg#4=ZW`0$BGrwy5W`5Op%>2R=@~iqW^Q-zX^Q-zX^Q-dW&2MY%U!jcNH1X8Xl9naPZB{|+>7Jf{f+C=JDfRy+C<7|}ul@;2_3~BzzyAc~M|TYO+Lm>nTYho<Pj0#2mMWO=zgjZ(0Br;l{&!2p9;A(6!vAT>*h91tO!ym?j6F;n!G!<ElCc171QXsORu~mb_#|TgK?~#GajS2;C8sS_v=jcAC1W{gBbe}SSu$qRMlj)zSTgo6Dwy#5EE)S7{TIKR*k9=1_$|c#K>xz8Bla8m2YwB)>*#Oz)x>^Auj5w|`w{&azlzvT=#Tg}i2Z{8gx~Czwd8CqITd~vu|Lt@@q3BgK>x%aCiV|{121xMlza%a$l+wyP9QfEXeazcOU90&@8CxhdkZ~=A5QED`WF5fV*Ah|_`bw;qx<k7Vq4JN_>RQZp<D1z5?h0=!#5|k8eM~LOl&2(8sCiADs&~j9kDmiRrn6X){?(p;lIM(K-=Ma@H3mywfH{7cA=Z`1BmTKcj1Q-JB;qdk0N%Ie2e@ZMvv0wC~Xdt>rv!;6fxmPx@8Qx8bdCHf7&gB$jKmbCVY2dA+#_4DPkSb5Wcrtx^Yk4xM$%95*vW_!H*y|3>|=<>6RDWG6kK4pH3`{PQgD<Yz!L4_j5}!V^8MZgzrkMJNh)fHL<7A?s!q!5^s%f=$5)@Q?xC<HnB!%Q~VRenxKvFUEI=&ITP9*--}ppv>Sdfv4LoB{8(Zm(1G}=#GYkd#Qcn=2tN^>f}e<=j84K&#!o<>#ZSPibvlacj)IRs$KqdPOq0-O@h_9V8Tgr=y2$Y~{B-Ki!N!r_apYL6X|aY!qJ!{*XrrEkk@PbX{yaJjKa^`Eqv|^SiS<L1@tuivMf>4f5^Ifi#n&g+5N(YYT&$ZQzM-cs)=e#ZUF!8Lxo%qE8&GeBZ;!UIve%Z-9u(m_pl$FS@M4b>&$ifS)w3XcTeLa8Exsw*7~d4%2yKRMgl~ej!?)wQO(?=Yfi|$RpP?t1hg$eLXajr$=0f-(mRx(|nUgNeRSSG4v=_b;z9%{u-xEKCGT76vSjR8m$5Iz-_$5oO<C*vu(HHP9&{p{6{7eM@lBX`#{R;fc)R)1gp)>G;i}m^%ewwE)*6R}dbDp|buZ!_RJ$12O7vlSS>SDdl$9MMB#d>`O-;(+qSP-p`pF{p;;e(#K$lGjuEl*wKbS}P*r!I0i4`0ty7r9)3Z{ewnTrR?Q^3+9MU&Z(I)J0yG;)i(ZB7d*r$9w88k;B(vqF%*4uPfOyheDT=&&sxpt)NYWd{(q&Y#D7<kk9hAjJ-yiW#qH8>&x0QS3;MNx01GuEu_t2@>bmSC2W}!q4UYlBesmqq0KAgr-&_MvuHDi{1mliY&LCXk)L9=jLoIZZ1VG{Eo1X&Gnf24X3N+D+RP(AWn5p%mUAz35qT(Q%h*!dyh<J_*fRDyZI+S;G3OPS_X@;?AHn=TYfE2=`bb!1v<iMC^FI_{nff!Z@@PeTA7W+6*%ETNgglie_Kc^!$Wsq|Sx;T$vNOIk^(SE^$nkt~KA*gnB-Yu}UgWhUzJ#YP^4b(%oO(l85%dv!6JkZtBKRicw*|har!Ml^4qwbu7rF0*f7DYK`R>k|Si~Ax#5#D4cqe>!)<bW6DNkLjg8}$5p1N2EL-6H1^-8RTAuv&I?Us(rSx4scNlHuNt?|v#rugRg#%^hVHbk4^8xd=QHpDk0)&gyUZ^nGJ!ndH_0oDm^hacva!Q9he?s*7&2=_b1EibrbG&%-9k=Sr_G=3bhWOO+GX}5&j(w`!HPq#dUc0@z?`ovnJ9X<2eoOpeF&@DC5#%OcAn%|lf;j5vI@YV2-yQL1=3~hw3N30dv4Bwtu2ecJ_f?LKimt&b<;U_bXQz^nvbIbGS6!ZmrnAk*g3jR4_<Isutj?7_aits(qr|~`TVlNT<*eG&60zZs0iu;&=S7R4C1|5YTMPFmkk@zwA(dbb8X#8;W8T@d3GTH~<hcPGH+3RT>+8;j-{~Sg5L2l`V_C)*R+Y);URqL@XvHIv!cJ_J;60eJ|?Uov7O;oK%QK}KIfv@V8>geNWHGC~%bx^e)pCDEbt%GkvtUX!}--TFLTduu+wp@Qg`{D=V2T+9XjdsKL#*4kP6WRgohVOuHk9Ng(Wema(WK8{N)0cQ(SXZ<Qemp-j7VU?hL~H^&7B9G1i&OCvsK08<XK5*Zs;4fVr6qXv{4Ius(dY3Ci9Lsg@$-odLZ8FGLaZ06)}Y{GJ<Y-QqCN{&7j285Nvt+n7caP2PcPxs8hjB}6|I4vPOLhr*5C|cwb1JLmx(=r*22#w)&_k7Kbzdm#kcX)MgHdDyHH;M8;=geFCsPx9glyN*i>{9{$28S8viQwldvV|QhWxn#pn|J5n>C`#rXZi=A#SoX~bSZ=i_$~n}fcB-%4y2ItRaj*i3X5el@X|(3$uZ#9l;S!mlDW9eokMp4bd@I(`eWm(dycoy2CNFXK~*%|&P9_Ys?i&cz=lwg8=ne}~v2bOHWdVy~i$@HgD@k6ZF3NiC2h{ok(t%Psknq~=Y^_J2?pdV7-e*Ioa!TW(8|dP`Ea|B<@To078q_tb^vNXqu#Q5R|_W&3Zb3;h>=)zxcmv67@FC1v{`s0+=Rl<j|_F7)Q4Z2t>&p|>Vw`(LRG&6Skxf2S@qPg1u3le*A5lCu2`>Nl8g;jg&<8)Dy(3+2D2F6O-eIVnJ%{wDS{Ug%}~WpbzdCF+;Ro$?o{=T4G&{Ed7H_8YN_c%h%;MP750^W6O0bz-06g?@(rjJ2WsdFtm`8_It|{S(%P@@J`^Wo;<`5%rH)8_Iu7U91DKPOh?EzQun_o2%$K{5jT=@}E-wl(nS%1?m@AOUg&7M_EhCe?k2V){^pHQvZ^*r2JRZh5qUBSEyfMjR^miTe57qcM8qGZ+6R@w%qfC?!vEiOT?CYlF(K79d1dn<=!K73qI2=M{T)h2tADd&@Jz~<qUcX{{gZ0&@=dBZaKktPcT;D4-q?vzJ=dQES>SEa}T@lY24?2e&#LwK{O4YM*D;4A^di(@g}OSvx(Sd^iBLSx2$o?N^~7w%;9q8aTR_Ax)Q$vzZzYKUyWC1)CR7#0lt~Cj&ZHy+QPran3kg}@vjq$pv&<a-SP&xT~B`3qAB<k+Nd?Mmj2elh2KVBJJ1yTZen|ExlRt)a;+T3??d<C_u<vKmr6gW@Ezzjyu&pPpnLFd6FZ6?z>76`+?MN7tT(YPv(WeOS@;Z!@F&qT_>=h4=qdbZygFBfW}>I?rx=5JhB6s%CS3SOEctqrB3{KP;`JYjcs)cBulp$CbvH%43Q)xB4vKi?qKMbc6iaTAu_9hKQN-&uig?{l5wH9d@w$s5UiVVO>p_Zm6{d)nxYwF)so|F5Xc7G5#EPQD@q!23QXOBEdR5p1XaFzxJ#MLtf51~0f6h`7e~+i0&n@Ng1wHjVZYhh;=c(W7meTk<o_bEVl*Hfask>>mO5k&P>N(u<7~ZB{3U&*c17C(%ZuAzs;CbCr4xgKP1=yWvUVJ5Dh0r_kg5U3!D)>U4`onIihQHraFG3Eh!9@L#TMm-LgT#e*h&_(h#5?5g0RD06>9DG3b$lwZ%4k)5D*4-quk5Ld{O!P3q`nPS7A=oYAyyhKi%%hc8}X&7uZNXDOXAm)zYX{j)HlIOp^xFW5-Wq2!fz*54lRR!lUN0`9DWb6N@xXq8nG&9CH#J3)zB*VgT!i})$pIX<s3OYN4rCCk-tyyhp3;09Y7uYN5s<61NaY!rK0Kh56Isce5$7|^7kHoC-sxCZRigC31TVeHhdPbjc5u!i~MEaH&V}pZ9v!Kj}zO3Zot1wY%976e~Q?4bSwT8`8$o@?x~CXy^nvB`iHPIbPxVxV*AlF{5fI=(f#-z+;WW^UZdToaFM_7@t;!v4t5s(1ph6ukI=LDuZewteuTeF><sz={t~hG&@=dp#7?5`;XfyK0zHZUocw);KSBLGECbELpC^A8@EO#ju;XYZ{tII7qQ~)H5<7*yi~o}ReT6?o{R-@T^fdk(VjrUK<F69?82u1`jo3N#WBlE=%-=n>^w+HHy2xK4Tlyc!=UujB-x2$sd<rh|cc(4=cjPm_E!o$^z9pY|Z5g{vo3F{|?Y4|vqRnOUncJ4Ji?q2!J_Q%~yUmvVBKf?<mh3ZPpOep<Y#BRGo6pGS&9;nPpv`&md8;jBQQBM}pMs10<+7!ZlFvN0WM2~df_w@t@^^<V{g>o3pDo!HVqcNZ0=A5OLz^q)v!E?wS84MN`4qV;Nd8(kvy%$u_;3Hq`0SVXPSw)>2lD1m>VM|z{mE%=U-3WsZQbmq*!#yM_doH+N9Dy|ZCU>VXE+US'

def decode_geometry():
    with np.load(io.BytesIO(zlib.decompress(base64.b85decode(GEOMETRY_BASE85)))) as data:
        return data['vertices'],data['faces']

def build():
    vertices,faces=decode_geometry()
    center=(vertices.min(axis=0)+vertices.max(axis=0))/2
    extent=float(np.ptp(vertices,axis=0).max())
    if extent<=0: raise ValueError('Source has zero extent')
    construction_scale=100.0/extent
    v=(vertices-center)*construction_scale
    sewing=BRepBuilderAPI_Sewing(1e-7,True,True,True,False)
    planar_faces=[]
    skipped=[]
    for index,tri in enumerate(faces):
        points=v[tri]
        if np.linalg.norm(np.cross(points[1]-points[0],points[2]-points[0]))<=1e-12:
            skipped.append(index)
            continue
        wire=cq.Wire.makePolygon([cq.Vector(*p) for p in points],close=True)
        face=cq.Face.makeFromWires(wire)
        planar_faces.append(face)
        sewing.Add(face.wrapped)
    if not planar_faces: raise ValueError('No non-degenerate triangles')
    sewing.Perform()
    shape=cq.Shape.cast(sewing.SewedShape())
    representation='faceted_surface'
    if SOURCE_INFO['input_watertight']:
        solids=[]
        for shell in shape.Shells():
            solid=cq.Solid.makeSolid(shell)
            if solid.Volume()<0: solid=cq.Shape.cast(solid.wrapped.Reversed())
            solids.append(solid)
        if solids:
            candidate=solids[0] if len(solids)==1 else cq.Compound.makeCompound(solids)
            if candidate.isValid() and len(candidate.Faces())==len(planar_faces):
                shape=candidate
                representation='faceted_solid'
    if not shape.isValid():
        # Explicitly represent troublesome nonmanifold edges as separate faces.
        shape=cq.Compound.makeCompound(planar_faces)
        representation='independent_faces'
    shape=shape.scale(1/construction_scale).translate(tuple(center))
    return shape,{'representation':representation,'degenerate_faces_skipped':skipped,
                  'construction_scale':construction_scale,
                  'sewing_tolerance_original_units':1e-7/construction_scale}

def describe(shape):
    b=shape.BoundingBox()
    return {'valid':bool(shape.isValid()),'solids':len(shape.Solids()),
            'shells':len(shape.Shells()),'faces':len(shape.Faces()),
            'bounds':[[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]],
            'solid_volume':float(shape.Volume()) if shape.Solids() else None}

def export(out,validate=True):
    start=time.time();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    shape,metadata=build()
    state=describe(shape)
    if not state['valid']: raise RuntimeError('Constructed BREP is invalid')
    shape.exportBrep(str(out/(PART_NAME+'.brep')))
    shape.exportStep(str(out/(PART_NAME+'.step')))
    report={**SOURCE_INFO,**metadata,'cad':state,'step_unit':'mm',
            'source_physical_unit':'unknown','coordinate_policy':'preserve original numeric coordinates',
            'code_kind':'standalone embedded faceted geometry','source_modified':False}
    if validate:
        reopened=cq.importers.importStep(str(out/(PART_NAME+'.step'))).val()
        report['step_reimport']=describe(reopened)
        if not report['step_reimport']['valid']: raise RuntimeError('Reimported STEP is invalid')
        if report['step_reimport']['faces']!=state['faces']:
            raise RuntimeError('STEP transfer changed the face count')
        error=float(np.max(np.abs(np.asarray(report['step_reimport']['bounds'])-np.asarray(state['bounds']))))
        report['roundtrip_bounds_max_error']=error
        if error>max(float(np.ptp(decode_geometry()[0],axis=0).max())*1e-5,1e-6):
            raise RuntimeError('STEP transfer changed bounding dimensions')
    report['seconds']=time.time()-start
    report['status']='SUCCESS'
    (out/(PART_NAME+'_report.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-directory',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--no-validate',action='store_true')
    args=parser.parse_args()
    print(json.dumps(export(args.output_directory,not args.no_validate)),flush=True)

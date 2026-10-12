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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/36793e98c89f41c186617d4581598ec4/part_004.stl', 'relative_path': '36793e98c89f41c186617d4581598ec4/part_004.stl', 'source_sha256': '68edb6ddc81aa8c7661794cc7140e06d96fd2cb54e8400ba8d4a372f98cb7e05', 'input_faces': 672, 'input_vertices': 408, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10321421921253204, -0.009332865476608276, 0.11786137521266937], [-0.016039980575442314, 0.14280730485916138, 0.20197883248329163]]}
GEOMETRY_BASE85 = 'c$}r233N@@+y74@rX=PdB;}@vm?J{Wt}#eTqKK(nLx?$vAcDGPVixld*H}T#D#lzv3^f)twR$P4sy{K*SiJXnzF!^w>;JCxuJ^Upv%a76&A$8W^Xz^0-sjxAM1<vV^D^+y&)BuZFT?I{7!sa_moXwbKB0f_=wVfd#Ex<?3aT&vK59yv4xdGIb}>d6qs#Y+9@aa)d|gxd`h9DcuWTyccW8V<e9s|0hQ{}a7QaQ$LBpb*{;-&yvC+=sfZ)K|l}$A&R5pz@{V)HyJDXr`G-!W@v?aFD&PH+^>Sh<Um+1>XA=hp_zHlN#)bgeq{P0+mFFabyn@2~%cT~{wmZ&K89k)8dZ!&bd9NRvrs=l!-6u$3f_=h&AZ_TO;f69eDT2HSA@cRV9zqM1(Yu)q`?d(_u{xyr9*PM19{;9I?SJeDk>sizTe!r6N8@$l-T8sK0(a-r6gTF3A%Nu^zwY=?t7wdVc?XfS}hW6~p1OH(6y?VT^8tO0qaG(0ogVlE|U#h<8@dNnndvDeD^zMxFe)9|bHQSK4XJP6aCF%c}XP4GnZWPL&xD5Z?{4{M}#l>jn>`U-%^}oS!SuJmBc^-a)$Q|0wN1N2QMxB74UU`$Y)4QPh_EyJO|JigsU#043|H~clFYZ;}G;NOhmc!fON37QCwWQ=gJ&RVrzvH(}&sV^qzU{~|_<e8cdCgttqCM{>!@qe!>$lf^i1Bl55`2@7=HLA8H1cz29Q@tGH9tn!d(@vk0)Fcang@%=a`i3y2f}|+YQNTdy#@MlOAP$~T;HeHm9ZTCm>Lbgl*<M!_xUAUuPgm|hmp@t!I@gVepmRf+>xK_gK=J47x)iWY5i8mP4rj4&hSTU)cWm%TBCgbHt<tdZq|0LEw1&O*VlpnvcA@1jA?@L;9VWQ_Z!W#{n0=z@7Pck{zJ=GdcI?)kY^ts_(Q8{9!ymWAfLlL;k#T@-@NuD^8YLs{L3pf|F*1f)L+klAJFcA`Y#eN59IieuD+v+jtAT8BAGbPJNSp5Yk!%~Oo89%A$;HE7;kfLXnPzF@4!Ffzfs$LxviGBwxQo^*cLq=xK4e`x?AwG>*)Mon2w<Qk?Zge&RnC%{zXv#+w<@zHD0Ujuug^Ve-8eiKWLt9Iac95ir)eM_#@4a5!Vg*-0~It?!$FHF=f8Rbrqx^?y^qHdAq4^xGjaBc@%kTnjiIlF%Eu(AqTbm)xEgyE{uS`^`+*)@!1c^|LCFc8wO#VyIe#b+y}#7bqe#+A9HZt5DWa+2|CX>VhbHr?b#jv^~QR==0x<bxxyFlV@_)OjhxePU7ModCw0|%(lM&0)?=+43V&$|#?Pvp$p7j3@XKUszgWJC(DHV-8t{)zOjSR3M~vrRD|0-!*|c0t7V><v0{nOTG;fYq>6m9CJ>Zw#u6Z-w_dz`#x#7P*rS(__HN<^-%$3)R`QH>ZTias_eY#iu7xUI@zoZpb-!kVn__HtRd~4Y>7}q=g0sNLphxB|VPmG^NN8vAs!+8FXAN2>>;g_7ZTH9ecjP@+dfbV`$`_bGZ3gwgb!LR-t^TxcR=$GHO!*`9;b;Jldt>tYOH^C1pfqC-bO0=`xdid`?*Sy(JBw+lkoCg0^vgXaU*AMkim;irsB-Wihw^7e8BjB5&mgw>P73i13!{NuiSgQ3-&xLU^B7xU+SL?S|sC-!4+b9NpAB)a=rg3Y~{<G2WXD&cKM_|4(m5YMEv8~>}rnKfLzpFj`h?M18Z+s&1Iixv!k8wIbTaJ8sOg~qv8T_Dqy6)I}xx!DY2Y=KsZJ(+95X{4e3d3LLyHc-f$y4Ob%MJdkT-XnIKE>yLaD|^)Qv1tMY#zqX>v!L%|7gA57uH#gkk4YT;kS&(Jn8re*EKyG{-j8q&&_2l+D@bCBltcAHJ|2<57C~Z_u<djm5y?2wLRubx8M)it?jh7sigJTDqese^ttBQnj;1C!_#x{vpjS@G%~)^_88Gw@XJ@!d>RKA>ORnM&kjGmhORG;@LF2GrNK`4iT8B;m@LE8H>YfcpJ(6#ZHI3wjFZD#;Kz=^JkTov^F#P1_`eT8es_nUyjL3hn62}*{U`2Y{VKNzzFUb!>Q~r_`S81m@KZPHdTMF76nXGWf`30sug81~>yCX~9DF}dov-Yp_9FlBL*UQKjq&{1L2Z|%br<-?^2K_5v<&i=6av4^3e?}KHulfEtH95nf%`hLDC+m7|2RVLQ|rCMsHbTq_#LO|xV7D^hkeV%0QkPAw7+cq`ykI2fB5FCRoXAr-(jBjC=GvmAsr`<Z82KjI<yr0I!E-n9J%{q+#W9p|3MY(lefRn^7an};r~1t<LCA>&4cZkEBwZudTdX3$2>N{fZsj8u3yH?GsiG~KI~C{|7TdgcBZ3W=DmWSehKqT?NsDp>QC_PE_2lHjCIYt?gspFRWL5^e67B1+GY3w;q$Z|)gEE|3_b_HW!)M2dGC;a`*%j+Ibw+0ajoad7Wn5@>wd#gB2az%CmY~DErfmHrxCc1?yZA=ISb>H>zz?06@J5?k)J0mFdlLy!_T)|$D1uQ4E1|WfM0f^u3zS$8OYnZ1o#OKoo_9vCiqPT!1qnYeq-`0^sluw{8qnXTv^PxPrq-$dNNb=y!-9w_f`$z-{`6RYZ`tR?H^Gc{+2g74?Cu2Vjp`w5WdehI!=t7Gtqv(ittZA)qb~p+Y5gGGVm+x&^$O?r(%5mP!j%yHOYG3iT;=ea+grwYAt~0#<X3UH&c@WC?B(Jik9nr6Z7GWce~N=OJ?cu#zd{h-265C$KUJctxYPxpMMely6eld{DCy&^YAhFo&maETg<-Ne$$kr@Mqn^e)n1=o)>=2gnuDH=Qn$`ddL3dw_Bt8CA)hT#+BC*_>22v{FFL__3P+b_{N#p+Rh?3&`zI)@RK{~{>0v3me%8VGDCgqqb11C{F2zW&l!*Mc?L~WzvUv-GdTu+`l?A<|CNEvb0@ZQB=%7iGcitXwSj-<HysZa&NJ2_jp5h2qx&Mm^a}lJX$ar`YMlCmf-ny(4~9RWzUJTVnG5%O-O}*KcrVm;k2?&1t`Gc^VN>;ZKGsL`^OEqh%ji5{xz-BhuX(Ya+qxfcln&AM7!C8nj|@V8g>S?<>t(>N?T+>1X)o-z2R+%P{)(H}r(M~q^_a`wf#33t&hzG?cz$<$eg%G`%h=D?T90~sF2ipZjOT@<49wdf&caXIf#bsAxbHS+!C%_}_g(IV`1{JE@coi>-nQPqgZ|xe0Di!aRz0qhg*-Rd3V%Q_o?AWqvb6p#Y4AgKWB#dw=Xc}gTKH8q<Glf&N336@sBcYfi*@ln-g_8(CZW7B5cl1xmKZ0;#=!6X81ve>6y!U0IQ))hbY8W(oAI3fJ|4bzs`jHP-wCW==|kX~YK+k1flDwy-0cZ}$>oK}OQ`mX^*|^1M;_w2X@3*k7pvOAZ`KX#Q-Ql!XS+6q|7Skk*IB>9{rH#Pa3b;>um<<#!aDG~Y{IzRIT`ho4S_%5j?UYT)RD;B2T%A<*XlfJwwkm4<!_0>eDOm7#;tE2`1bIzdYmf=^H2Vq@bkXGJo{!J#>0yTJJtW=iO#p?A9rG(eB>g0+ndSy`I|>jf7|owTiZRr^(3A{J{zBb{|MvQ{>KgU@4JJj$5;%1tQ-4l2mEz4=j!pfaO6LFIehDjA=;iB9_Yt@bK$!k)BTva_+>3`nKT3bG8eoDyP1u=9ksx(9jp65>--LyH`|wy@N2Zhb3p?;`nP!m{DKQHKO8hLf5x_f|9&T)H(ppUFV$%Rf4eP7k4JAoKd!0;f8kr~A13BN{eh+6ukgovDoY^t33=U-H-Fqeri&Xf{x9TV{eF61SdyA!o-c4~2lDwq^Jbm)J?j7El={}@`OtrrBhg>K9%lKmeYIR@GV0H>4gR&4I{(<`T9BV5tKmQYLhpCW_*kri$*HJ+^gTQee>orLNf?Rp)^?f)n@2b7mxd35pPeyE>-h%z9HUEL_+RhE=M!gOz6=h9UpO0iUUVJv<lE-()8=S@8P7s6|1@m`KN0W6Oox_XTwSV;c4idEefMfC^7g(O%9{#l|61Rk#dxdhgYtoxr)(?spgqrvp}b{>-govj+p#}f?FK&{^Rm(2AJ>)mc02O<SoeqK(LHgWcKbtp>yc%+-=eN#o*#1q<?Wk$>3O3HqMqKT;EyVT@;|vEpZPQ4Pc)&Oe|(4W)@Ct$W4J}@Eq@5_Np>uP-}(uj-zEm(`6Vft=RKkQWlY(J{4Ab~c3$zvb-t*8@xR-O@@Jy-K5`t*Mtkml0snCd?xW}Z@VU;dS^rtxCs_AHX&y{x8pE$pT<;6xPHXk;+v~xPIgb9#wNZUX(Lngk%OVf$o}!&SO2H2(qVuz<<r-X9nkW2bp17}Gw?KPBU2$DEH=~}ptB~h&*SDdaU3=^C)@2wEOETfl+^YA5>0TiA343?Kzd8)h-FF<Q|JllIxPO}=FF|XOw<$>|@BS&C|35@>JoklfH0r9K<MW+)SOfZ*I&T}Zn`U8L`ND6qU)O6}@~7Bel_?7Uo12*LVy5DG;pgdF)h}KV&xvlkP|vV2@E`uB>+;9vGV|P#@Ds-AxOHU5!Ot;t>%a1UpgYF%>A~>1e>3*xJE7%0YO8OZ5Q;p^{|))67=ZHG2giw;Pp4!5Z!HV|(Jbr_y#{GLM&BavjkWw<q%g)wAy3rbdl9bp^<|9nwa>oBeLX5hKi|L~*Bf#H{`P$OzQS}V4ev>|FNbgcDPGiaYYy6T(W<`nMj_n)g)l#u*Oy0m;|S)Bn!Ayo8O7iymc@IC-H+g(aDl(09`5s7crLI%-nK>kfz{D3IrAfLPu9U7hkdrSUIwoBN~-$SSyeEelRKdPz$BE<<AMA7RW$0k9SOf&O?|Ioi>rclGp-rx@t%qOQ}eOt$L%Fhp3mv_^rOiCe_n6a@-E+^JvGN8KhLghMjjT9*7C+H<TLdmeEV;sHJ?vD;CgGUMLq71QBNa`XZr^$$`44^_1ZLf0M?`NMNxiNUhHQ^6x8;ZY&lW>#~R4nqbT*QH{Nd2^2^_0J{<5Z_N!B#!(ZDB*V_}%JN9~;H({LjgMa)-w5QVs_-=TgXdnDF@@ZNR|JDv&uPwH<XlI!@@Qw3*^n9xuAkR1I!uS1TqUIqH&pWms%fj#W0^{7_ep2;qY4{s+j2E@Fi$y)N|4dWg`!`(gcP-E!m*?>3MW}B(9*p`+JyzcuhW(s*#%}cQE<4KKdZg>PE%_?yPn`|_P#ZkAo}8xjJBoKfJq58YTf9SYy?=g=^1oC<zr3%b<!vR}!nfaTtDieL3D2jCUvE@@)?+;1CC))RfByqM_s{0i4)kxItMFem)%Q-;rnxZBM=XOMymW%7X~U0L@4g<OzIELojH}{hP*0g~lrNKt>*~4$<K$s$_@2Sq9{cV_ntw+NANaPaLpA>aXYm|*AUAxUfw(WszakHxJ^o7lgH!Z9m^lXf8SBhr@Ll=*R)NpCXJ^At4AJ)6ch}?d>_GTe(y-6TdX0RpE3Llu0>3X`I}h!D<Ad_1llY!-d}HkQlJmn4c%<*Oj20a+UmbUY@93VW*EOvu*1Pd@HmJXHJm&3@JunV^%<5bHenviB>!Y3zbx?j<b*rfPz=ePN0q696l)X|S`YWq8{M+vM-lyLp?9V%y;M-b#sqN|64fX7LyI%d!+~}{A4;bf#j=&!?UC(PwT*31u!naxVeU5bx>bIBf4u5nVeeZ4Gdmnza>~-oNxQgrjWsqL4b?^oF);0Q^Yah20<%7?wZ#~oj_fh&Tw12^LlwTaB>xfaWI`${6%<wPdi`DYU-y+XvPpwtoNUy2qi@SqyQuYA+$btC2GCcw7RKFzn=C|5k_ES}{Uz#)={)NWT+OC6mA7TzmfZs71c`Fov{qW#6tmpJFXhF<xd7iJ)<LpFT7tCF@p?p$J_;)?@djaE;1M|k>K=@-{VqZ6HG0KlE4L`7n-Y@n;x6%HG<5#OcqN=_RH)`iOfqrNYKihYRwtsOZ+T-m8Kdv9<L#vCHx173ZQ-47pegAJ<Er;=caUFcir5;*O+f!&~a4YzA_vyT0?}d5EJiG{e=aZ@)SG$Ynnr(SmPw6P!2h~u2)tjsIc;r6p>*D&L{l#~~&)%l@srA_u)IZY(KPE)qqgszOMLq6e@a+%d_47X)D8C^)RsH&x_5G@SX>*hxo(?~~#RT;W`C|PYGZX%qUHTr?e!C&slbs0P2%V|NR{~Lf(GM%t-|`IK*Objb{rfh<H`X-Mc2w_&@_yCeo8t7j!(96m+W9i?3iW+U;66$yp!bV;Lbv6}!>(A|Z&)9#-Onsj|Cg!w9`I0a%qI>D{PBVKJ}av|{NF>Ds-O4<_uZyvIB)R%C1_7Wd_R~n3*{#)UabDj7CLV2YtrGzOo4Aa(Rsl9xTgB{jFIqTx9Ix{`+!L(fAGvA^@CsNb(wn?JEi`XQShs-(tU{i*%d8s`?3;zw-0#V-f5`%ro=@H)h~7!-}lwNhw~Px5C4IO_OD?{#d#xr;TwhYIo%v_U46?ZZx*Qk<|*E%#ofnwA02_;a+$6##@<Zizvou?g<Io$w5vDJo;KT4&@X=a9?V#hqSs~HQv-g$cX+RLsf_xTB_rqKey@bzS%n=?-@Nn0JoP&jUZKbCz126p7!AK)4Sg?UKldH-R`JKV=&xvfpJ_d?P<=;%Gw_#<)9*FRaW~+f90Wh$8NNs0dH?eFZ_@Yq<{)SN5&!!2+rjt}`3;kt$}sX8UPj-Z|M=;f{=qQ*(*OTY-}(ptkAC`AD<tUu`qQ^H&Nl3E#ztq1a>fd0%;E70dU8C$8J(Rm&c!g|oiWH6No4VcIU~jyefYN+dQ+S+mSwGE@#Z*V0=<c3@uoXtsxwj;Q~CD=&Y0zl+0IBNFW~V^XDnvSWF5iI@N~u-XPbS=;yra9KXyh57ld#D7ld$57liO5hVT`J@I{93x74TPqtqAFr{t$R=L@QdEE+(T5PoGKgx^vF$)a`062c!0gs>a`ZYGPiB)gIGGKBL}+mJ;&kn@uZF@$}nUC5%{$v))L4B>Lro@CL!<Z|T74B;Boeq_-B<Qn994B;l!!DP{)<R;`+4B@ua1hVJ|a$9nHhHz(UB3X14xih&NL%0WZBw2Jgxd++85bjNlB}Y&@GK8ZU!b7OB<bl*UhVW>H@R!tBaxBmHB|~^TLwFK(BzYvSXA(nr8bdglnn+G$zLFWjvlzm&sR`r+_Q!07@JxpAbn0O8VD|TPhVWE|@I-1qvS?rOMDhfNu$9`AEZUuHC68qYCsDhQMLUp_$ngx}LDV*6(U#;v<QRr<AF7!wT8G?+`~^d}9W{_F8bEGGZp{#GKsAv?OOP9ot1*PjPz#VnbCS!Di!y}W8N%-jgz&FanNNS^yn2QFEBSkd@Daupu1|Z&8>tt`7dg*vWPHnYYXy1EKjvlOkzC6%sB_43SSEw|g8YJWaR&7*c_j4!^(}cMHJ$pF{FZZcI#uRk;TU@RsN(OVFM5zF{y}P9vS@yCFP61a#kbQJJw_G(7_|^t)Q3EXWzSN@KTBWqJF58KQA?9W%aO;h><y~;H|UGrriy=?TA3_bgS?n!A5g`AKwtD3Rs3hvdSuZi<h?BWo+|!(`l5MwEPft-t`%9dE%`^5EzIM#Wbs8y@whEnv^`n0Gg<Z}q7``DnJm6&FpoQvMZ1wjdysvpji^1yzSK}^53;C*EZUp=aqS7^XGJSAghQwiWYLb~5OPz7a2P|l6GONcHJU6sg#2+m6Yfur<MBXxV_dMdeaXL#ruR9|(TnHpM6VdH;bS|ceKi?PSyt+j^=~pm_~Uvf>)c$1a5DSoA^T6(6xp}VBa6zubvkt+Syc9?v#E>7q6=8B=zQ{go^uj)26+bC80I{G7iZL`hLeM+O{n2yvoivn(U4k|ELxe|klcVF+=yC@ELwxyh}?`J+?raOT$|@_%@A(K5bi+@Cx`QTdN70sGla)d2a-j<B#$M}V+h-*^U0!X$u{zKhVXHQ@J@#C28QrLhVT^XeDZvrZwf;=mLc4YI*>e&*VBy}Ms7=OObsK4v0ocAgsU@z{f)oJfp7_G05yml#JmSkYm;lU{{k4opE86$p;jY{RwjQ!_GJi{qE;n~29isW%P@q?GlXj~gqu>$<o47^s+la>kQ_;F!w`<3HXw^OB1e!vX9#zsHY1C+CU+!vX9)MDwj+!7AonFFFoY*j2a`p|k|&W<7{aTm^T?t$@@n!fhVTjMcCzSk@(J=)hVah};Y$qROzKXu=mv5oc?Ux{jUk-M5S~q4NEV$!o=r|<2=}DMl100bKi((8Ur<|7+mb~alUtGNFoY{mtCL0j$rZ>Y8NvmOzwawycd8e)1X(nIEcz)~^b@idxe!CRAk~*FT8dndT!bO)O)WzfEl>6)`!IydGK4EKghQyc$f8ZjA>>eoa0lb>`%t*Pb4{x4jH=WsWYJH_Rmpw~;eym6WYHYtf@Bwl@b3mR+W?C?$iI_sF@#T1&yYp8kx!AgFoYLTmyty$k{6M!4B>v%0ptP9M?Y$NvS=i^AGr@hxHq*8Su}#&n;gv$?oa)kEZULWpFD&iJc8PtEZUbmf;^rfJd>J07M(<%NnXkj{)(DH7F|vLiu?^j_%wAFS@Z<?H2FG1_%8J-S@dV}UGfu#@ShCf-x$I_Q7@52Gs!=ZFEE4;QFo9<)5wR&n;62&si|bq+2rNq=?vjv)I_pqPx8lkO?W7^6ZH$SXe)9jatnrVO==yoXa#ajayf=@QEExDXaRCjvIj#rr}6hZDC|njO?4-WdXYs7kwpuVbCdHhggvQ6$fDk4PjY^SaB->+S+p#<IN8Jyu0*X!77Za+BG+XIx1@%WMLUpNlDjg5<ER73q7%t+<Y^4yRn%o<(QV{a<lPM6^VBnBQ3v@v`3^()IW?OsD)Z@c9t-DU2zyhDkc)7>_GSqCGlZ*CtB|X3J*dtQZpaXBPOVQ4r#7b6C)elt(U>6|#1Jk^^&|Un{V2;2_F@RTQeDU{Tw7duEc_pa@DJ2mWYJUPAIK*e!kejE$fAqLo5>3p!lS8HvS>fDXdkj@Z}Mnz5<_?#HJU8ipFEB{nISxbI)p4bf;@vfmm$1_I-V>#le~nyjv@Rtbtzf&EArRm!wlhb)Njb5r^)BYHyOgeP_L6k?~;EZ|G^M8T%b?LqJNSlg!8!|giE?0gmb$fgkSP=zmY|MBEKZxX9!=TULcDeB3~nCF@(2LH<3k`ledyrGK8m6r;|m8kw2~<!pYQl>QJ(1CvrSFiXq&b+JY=vliZvf%n<gYmLrQ6CHs*JGlcU}J;<Ut$$80c3}M6gd%gMCeey2{)s-xon=G1#Eb2+lLC(bx&PUBp7A;QBM=r(?E=@I&MJtg@ldCX<>rv~HMO%{Vkw0SyTc};hqH$ykc{oFO7Ihj~bQO6Pc|AjTKXo@*^gMY#`7%TJ9`z1c^f~z+`87k>gKLbeD;`{5yvZKqPZ+|LsQzSst{;^c!gU$K&8Q8@4Y__aV+eo75RUrCdL!JG8c7W&hjYD&WC*ul2-l(pk%PG2)M5yiX9yRkdXXc-TwJ|!{CEF#&fov6I>7(=AL;zRpZxdF4*vPc_s+Wh`Vm4zSWX$^&Ktv32S^>+!5IGqen2q('

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

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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/cbb199ae1edf41c6898c997ae785c4db/part_004.stl', 'relative_path': 'cbb199ae1edf41c6898c997ae785c4db/part_004.stl', 'source_sha256': 'e212df561494add57768e5b28d121c9a013b6ec3311024562c5a5da704aa3f3a', 'input_faces': 1622, 'input_vertices': 1053, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.35416966676712036, -0.36126846075057983, -0.05833891034126282], [0.4895835220813751, -0.08835838735103607, 0.1937449872493744]]}
GEOMETRY_BASE85 = 'c$}r3dE89p8~@Kd&m&TnB1_1SQj&xUktu}`5{XiSkQS9J*=l4-Xir%xLkds(YR_cLmL*#$nY2-o`c|~a@4n}LU&lGu%pbqk?^mzu_4&-_`druCbIyIvx#v7*szaOng0i0br<yn9m)5Nt_VPR%CwpbR!Mz6z?ANRJeRcZZGc@9r&gk|Z!Kd4GzNSOhh&R|9Uh~%8_w^c3vvIU$lRgb=){fTfbN7IO1A6qo<?aEu_O^P99(Uf?+vxY**5jVu=Jh!j*1f2H?P&dTYez>$|KI*8ZiWz>U$|qL!Q|x6Ked=B?7XyDKu@51M+%qc(v$BUTainT?>zQ#P*0^6ZnhXx{Y6h74)+&5q53DK5B<GOyS8V1r8jNM<ms<<8NcW;@zY=Han(OPar`G1qpE)jJ#{$TU-Y=@pOilIk4Em!=-wOGyX{7Qt;_heF5}PYqx#3^HrbM^e+*r=zt$6~zv#04qXnI}=b8^%k1N04zoP5?oA|qv>oa_^+YaOEugIk*zaN}a_a^OL71ZPCsrExc{Zk(wb@Om+xWDKL)!+9|4EGm3N&nRTA{jk8d|+stqI>8m<@eT{u_gGvTKD@eJhm;@b`V{EUeWdE(z^7Ib#;2|<1wy(gX+t3>0aGWR)+NbCEfV7A3c46^T#jV?~c#=cW=%3nV(vh`7e5Eh|^`hX<g=<-)HF^n=<dO`lpvTUFN^m6S_aTKmYeHaQb5<wgu;>)@8qB`I(<um;EJr`nHoc1?Q*M6RN-OpQ!qy%l=JQnBm58Zrg3a?XPv&{-USOX&X9!YF)O!=;>~cZOj}8s(%Vyw!hXBs(%vQKR?_y!p*A>w`>h=XRZ6kJ9@g`n9z0;J%#Si|E2f1KHZpaGM|<1&wtThyK_@${wv*||Ko3W+x@biL*v)Fj9>KliETsU7d?h9<B#8eo9k1ne(3y}r85sjPgRI-3C_1Hoq3i1sGI9krM<gu%l=h*ROSzQO#HHcm7b9KgPyu~{JP9IRsSTqTz|D5SN#*{a{Y}p>>N6O%J#|9**>D{>qV9>*M;&0?sF}@VQa8|mOd%$_r^62Uyrm-|Jbgb?!4KzjJtly`bz2k`c3;~eWi4N{f3_2eQZPU_!T{cF56%0an(O5ePn&rcZ2Ky^Q)ollclqLL{AiM44n_NblLtpreyTk%=6uKShl~?Q*s{A{z<v}q~&~qo@&0{ZHKYp{-VcKf8VdhnM6;>`G4H~?sLWVgs&q?Pbt6GyWc0l_Z2;TtJ9@_{M>%dKel^l{%Bo}U(r)zoG!<&*5&vWJw5A=(ERcJ=rVt_9#{R7(ue-Z&bPU7F8|JLAI`U;r#^DJoS#Kce|e+ZKFTk8iu1E~LU-3E`fF(WYhAX#uU~m(X#0zvM3?QKyyy})uc}@iT0dmz%tO)BEoW~G&i^c3&d&wky7k|t`$PS+^hsgA_d|nF|16#Usd2kqpK@a}n7+>WweD?D{?Wa1`_Z*Ox$A<=btk3#qNmp@f6J1&{pjNN-rwxTv2Au}JX)9Wh@M>4Jf~lD?N3c<9~zI=^>`AG9Ne7CFS__+trs}`r6r;9XkEr5x_9`zoPN=@Ki;=*X#85&<M9^n*qqBRy7=SgOwH)AL2E<f(YlPs*Uze&+mEjO(MAJ9<JWrDc=oT|oXan|_@jRf&N+Uq%XoZUjbH29ug9<TtnsMvYhC=w4!62_SfuLC403+fx}5*B{G6Y)F6Vz=@3=N}ebKt^pFr3BMc4h~MW0!p*>0+T3|+1-T92##QS_+lADg*vO|Je?blqQc-QPp^*PlDP<UW3t?jMinS;w!^wLk0lRl0xtN*{gvD&3zy#bP<npIVpkh_26{TGxJk{?xi2k3N5D-S<zcm-G6ib$>jftLvB6wO?Pqw64dauU}gCkM|W(_rC9}4XtmrF6-MY|D@b~WPK~TH(+4SKB8-X;?Uag{Sd9I_l*~M#;v=?hW)-iG3-ywY8qNs`+oF<9)Go`*XQaly6)rq)%&KSPM7|P<)xheX0{LONzqf?ogQWV>HA;4%#C09MVIwwdik-;{`O`K3vGX`%k~#NcEyFE?IU^=-CzGd<@7}SC)ck$*E^-hPyK3DP)|;nlhZG{_)|B1=UzWs%bgeTYdxX--s$~9{k1Or6SwSj$4UEdLf03q%k@R{1iD;bv@X{d(PJgzq3et2QFJ-~Ydx;|d+7f8f53<Cee3QH9WPnB+<!p#&bl*nykzOJK7aCk*QZCf@b*`_zx~m@_Km{ZU+J>_(?biLo?q8}|KNP3bvYl3p4wU>r(g6e|Aeuj^SRdLd?<S2#$Gx7qWkOZlV5OsYP1iHN9+E2Ui7yQewx#duKkJEW{21FO4s8_Ho7vWUvz)H+H|aY-^crg#;<jMJ&YdvX2++w{Gw<1hc5}Qhn1c+o{i__^o#Cazp4#!^W?dKq4}wGnV+J^D^?B7Pp$jst4e*C=L5srN9q3OMbG*^qVz1k{=T4efBT?&N6*OV7u{cv9cZ3&{95<dd+2)nTF>&U@oQa=M~`3YzQ0ZVocmYnvVTR_`&aA!{#{oi_xxA7zrWD4=D*Uj{CfT?-QU0RzIy&E-S^*ea?bOQ*8TB_uFgMN*M5Ee(YhXwKL2Rlzu)rcvCM0I{@1#HKL=f(|FxdwSLc7N>+$IGzt;WFd)n_#SJy|a%ls5wUmvyZ&(HWzu8+FDXX*0y7j%7n&(h`k-gS-poNE1}by@$2uGc?Wm-Ub6di^81UjJx4uKH)Ke_F51=z4vqb^rW;uGfcJm+hY{Tj)NQTHk72`}O)(>;C$-l+*S4T<fwv7hSK<Mc3=|^t@@VkNSQgy8eFQ`_=agt;_d|M5#wyANBoF>;B(Iv|s){qICc7Bk213qt>-we}Bx<)%)u2k6HS}uwQ?F^!@7lqd!jd{ZZ?>kN*BBy8iy?-8IB*H+BC(>;8IDbanqh>)NmHKWN=we~PZ|KWN=wza8u6K9{=xqjmp&Cc3`=qjl}q_kXmm$D{B6Xx%^m*X`(Zb^lH4{`C}H-+$A(_Urp^TG!*z_usVcf8GICIiI?Jt93d5XZhv%E2Yc%-`CasTdnK<`u?rfb$@;TR&;&;R_k%qU*Es={p$X$?^pM4wXXZ?`?rab^<96p-qyOz2VYnB|Fy3D`u@MxWj^?Q)Oud){(Re0I_LPc?$2k@_1|BVuKihme^GkYc=Y!vrThNj-)zcx{3_ia4|>+|t90$pI)0U|$CGvZD&4=|`|>;Pc?Es{T<QM(Wb~~2=StW9to!Fm*W<~$f39@@{F67;^-<R^t^4P5(be@!>)NlcUs~7W(bq4n`^U@liSB*X-^a7`NnyYK`*@Zv_l+BW=bl$nf8Wp2Cx!j`@B3N0tSkPSmU*q8Ptdym{F~_N`2^AR^9iw+9?IzY`3lkX^A)1&=PR@>>(5lZQLevw{zU8k_ZM{i{E626?=R^3`4iu-o<GrgT=mz_pLkPyy5|(t^Eq1gpASLT&*zA)pU;UMspjU1dVWdkvaZhZ%Y9>|r&WLb{F2t=s=t1INp$`EQex+#%;(Y1cV+2ve4*>-yRvlo{=4}lr>p1Rv@XxTW%*_QDqWs`6J0<5Cc1w9P3v*hUqAmAAKWIR>*oWrbh$r(uAdLg(&hX!xzOzo^?YNNJ}K<i&o^f2a{f6u!}U?me`?+T`wO~${!{Dz-(S%6^Pi&Y=RdU`SN-+#pQ-mAa=LmxHcMywh_0WH&C+Fl{{Eorqn_{8y8nDWx_-V_bp3p<x9wi1tLKxoF6U=oSI;MFU7k;lZR_TA^?bF~W&EP+=c`56&sV3eJ1wK@=g+n7AHV4O`E#xN$1l2m{@nMg=g+mCQ2q7u=h3ZSyYDCZ`G2MR&uwbI9Cu3hpXWr+dj4PO3DrOA`G4uJp8ro(80Efqso!5{-QWJ``u7)F_qV_FQNO<sUH|?<>j~Xo{r<vxzEeimzfaM+KmSEnzfaM+%zv+*)AjFbMAyHs5ncbjM(h6e-_p{3U)8@4LeKhrkm&mNK}whYiMQsh3y$Bv{wm#HH)_9Jm(jC+KZTz4`zfU-RR65&h|*>J(UFWt|GrG={_o4svwmNOu76(^8$HNfSJdzCwC+DYuXO+UdEH0#*T26LUH|@0>j~9g|NbtqZN}P+PyPN;>oR`P_3t0G9#{SK?;l0izkk$vT=mz#e@y3lnfodF_ot%k-=AvT|NW8D<Ep>@{i)Xd-ybPGq55b2K5<<2Sr(J)FLU$mxvySd7SLn!|5}y#yi>w@YTLe*nLbL7p+`48yfWB7y|~?q%;(a6bn!=<Pn(yitJrE`=5yiq^$Je+ls`51#Sb$2)UZD_2OWR%=XYG673D(xeSLYkQ2#{#ALqIGyKh0zFS_@T)5RbArA1*zU$G(N_x0r)LjL5mc^N&nYEyVTqOaVvFqc1ZS872{|DCCD|9eh-)na_?>TrMb*qGI!{;^;CXY};S!jNC|)QZBef50mlJuzlP*f09%5#jyy+k#hf?qAXM{zcE)zoM)C8=v{k>zVERVA1)({=WWz)5V|uyY8Er_kDGB$S-=laCOKZzb^7tuKnffYJZ8Y_m}Ti`^#JGEy#5|Mo-wZB$GcjJ9ONM9{+E4=(rPIA9teb<IZdGnbX%!2=x~|wPr%7f4b6Pr`I18@{1lr_x&xZyWgF!?H%@`C)V^1``^Cat+Uj5Ms$6i5j}lQkKBIrEWg@5zF%#hbmfU|{DphN{m~Qi_J;en{J{CwZ43L+<7>Bt{PAL+x;_n-h5VwY>n{uWlij~snrl9YuIGd3`typOH6Nm%eVFl|J$glGKA^|YeSh2MmSu41-mo7%v1D(^A3McM<=VfZ>-{Ub-oL(I?cZqK&Yxu7SJr`#j1TFu4vals@8h8Euj|H#{h~+lr#e2mF@y3wi2hoSDZl@{X1wyFOaJuZKASV2OYVcwU+Zz@_wQ?s5Buf5mM8vL^(~q0!~N%Yt?H|D>B(6e)`WEKKWF*T#h*O&f-P?Uy8HhL{8~>be}en}+Aq5H%l-ej?vJj=BlrKcUv%-uN49i2e}9qjXg#I;^7j|*7hU^f{QV`a{G#jeq!;bjoXan|@1N1f_2KVd{&<w0(tiH_mE}j*eviL@#g$)lJ)S6k|I&WZ#h=(XKIizgp3;6beywZ29>3Q0c=Y(S?)wkT$vJ<to>G22f3&Xsdj4o#k4MiRt&2apY+26ZSL-R|*T=8cwO=2<TG!*z$FJ7K@16fi&hwkrv;6A(rgeWlZ~DrOQ=TK@{H%33Ka1`^S2I5Bm*;Ba{G7U`^QRV*JRd0I(YlOB^f=E4YQO0I_^bBJ=<@uee>^HZ%g^(ZS$=fiKVeu#kMew}?^n9^%k!n$FS<V;UYq)9uH#Yb+Aq)dYQO0I@$$vuoc*<~{kp%_{m*-JSMKejbnVaDK1%nm*Xw`Fxqr2u<yZSx>;Cc5*xQ<GerjF&_59Sj?;kyQYp&x<>vDXFu8%L#_3@SLHs1B&@B99GL+So{Lv;SWpXEo_etrJYdQ$t<`A6%%f6Zj~zIuJ7^px^vt*?}>{aNcPrR(uzt*?~sACJ$y?sRp1)Ot$!_4QHf+OMyVTG!*z*GH}U{)HP{AGJQwdP@7%`b6v6uh%D9*W<}LA1d8HpX@uBbNpIQX}?|{DqZ`t)`v>h<H=edD&7CQ#Y=9>Ie(O%QvR&@qjc@hnm<a{<H?#oN*8}@(AnE^9lu&nDZf5`wXXg8_|>`|k3N32?yomm)OUT<`BUpD?N{edt!uwNe`;NiN1s2n?tk8A54!!RzF%uyt}mkN@7JR1@7LbEk~=bfb$>wXG3D3y2YkP}KM-3~n9=q94bk=e4bk=e4XsOmuYKW{nfW`H=e<98ZBZ^gy>i2npq{LAp3{pgSddFk4EpH9pq}{S5BGPW&2<*%(xZ!7g!)I%-M231c+mBDqKDpbeMZk+m`hI_*}OEUdm|ooe`l-OcwsI*bz`&8_+x+F;rbU|G(Xf|^g~rsq0e=omixS=?p=^e_l6fN3+kyw|8sxWs(JQ;T)Nk*eaP?4yw~aTZ~Y*sr;|=k_8T7>Pkip(IsKwX-(MX1TrttNFI<*O*Zq^z>o|YqWT;O9-Rr+S{CQuQ<(_j^{v>+(F6E!v!|5M{$1l34#-9{jjbC&<{%B&)$C>e~?Js(|XL$R^+s$=;wSPrV4-4<#bgSMO-Ba@?g|6pMbanHLp3w6XJ*nnrwBs4BzncFZdR)){iu+e*bai}*o>IqGs_hpUJ*tjh(LHtiCd<6y`l$0m0zIzI58kw<xyOSp<B4wE5IPS;m;ACQr@nD)$e(C6-JLh;4_%l`Pqg$t4C?WoCpo=u*9E!sbeZU~pq@IbUFbLxJt;c#(AO)E4$WJCJfbUqde17iAJuq7PwDaeb&=E6=M_D!KCkR|Pi;?MXM1|r4%wY+`)BFOueZO}W&4Y+x4+h9`-`r(zvz1V`?}ix{&>{(7hP|Et*7*O)b`hUTzy`>{j+qoXS&6eUuDL*lk4Dm=g-o6J{<DL{+s6Z%dbNg=F*c*k1Y-A@pp^6=Rt1lvLL6vwd%5<?yYv)IX%~HPtnt>(8n$g`ICP?<epzp{)FhtA1(25X1m4Iczj)rC${`zcRtjg7d@dqueX1nJI|=?>FaFI_~!?6ZvQM@`SteKx@>>Z_4d!w`Mjd*?Jv6C{-W#c?~h+?f6?{!&(hU+^!C?!LVaGn{j+qoXY~5cdorljt6G=!q3C+Os&!efimunIT9@^z|GsLys&zdcy<XM2tXD<X>s77GdR272UiJH{^{W55)OuCxvR)NkuUEA$>s5c8YP~ADUayL-*Q;9hue0)b)p}Lyy1!np`kz;=SN+eW)~kLWwO;l8YQ3s;PmN!%SGBIkuh*+um-VW@-PC$j>#|<;_lsJu`r}vYRsVg}dez_WYQ5_F)q2(UtM#g{tM#hZQ|kEA>s76L>iE^`RewIH^{W5AYQ3uU%y>G4{;wM^tX+6$d|S`6aiUk&>(e9fzud5*{YNnO|8k>Wga5n#<;KPJ>ivKIFE_U4dEOT${xb2mi7!q325y5(?pN?P_?Ogf1GffhzBTb9_$B;Ta{Iv_;nwpFzHjJd`PaPO5B>zVbq7rB1;2$$?rU%_`~bDzg5SVD=k?d%|KPUncN4q718~WG4(@{gPVE8kr$EiWCO!p!hks6P3-~GAdj7%p54|kkZsHRY`S}iy!3#`yCU)dG+?eOMjg8c8q;@+swzdHD=#d9*B)6G58=I-OxCtJ~cfIoRkB`Ih|MDDe20x?D#%I)9+zCHQum3>lVIytgPw+GNQF4EPf5NS2557J0xBO>b{{j90w{`nW90b#F$^8r-gzuv^4eo(|$LpWLU*NXxkcscXeQ?Qr2YwGfMD0HChd|8{6JLRc;NOwk4Sof;p2PSK)9VoX{xF`y%%9!V1?SHZ=8ojHgFE0J^X3RW4#P_r{X`Qr!876Kn5bc*Bv>3?5?%s45nhwpbHEz#v%%uv$?)Rv6Ty?<XVL5Iz&Oq(U&=%^@GN+B@+X6(;U~jS0!zWGQCl568(u~AFB9lr*2EcLX?V3jU3Ii7c*@`_LocbRVB&PJEW8T2is0#R>nV?~JiVl*vWaqF1$aerr-9|*)>8>zC3;Cs)WoS^W%z02P61DaTTfMdRq0ikeP0z%RrdWU)CK2H6fU_EU`colYNKFP_?;$hHPINX2X72-1YQWg!$dFYdQoHf?O;8y0lXgkLa;u(AH8k|rH9R5YN7|&58jh}1F#9a0lYqVDZB@@J;B@IT~+_)f&N#T=ms`{_XyPWMC*#DIlkuflA5+AI)YciyOO&W><G7>Hu&1m%kryveJyw$+}3q6(Hd+Em)zB0Yj`JW+k$Q2m-G5+@J6_;yUD~AU?;fbE(foG-$ZRE@VY=va9-U6znoknurb_vdg1FuFUv17alVPZ;4SdmOvFuG4Ay~P48I6GAKsVR+rT)y4_F7R3$Ft|AG`qGn_hha<FNc@urAmTUKf4=cnQ2ay>14jhmDwt>%oTb?&Lay*Tb!+8NO!pxBMDjcLrO+ZCxu9?Z6mZa@T<E;H{{Qfz9Ao@%kFDJ>1rHFwp{R1()1aU<-H$YFmLV12s38xD4z7zlvN_@G`jdbivn!ULDx?UGQ{a-#4W$IDc+{OYS1@VtAa|8^A8`RpuK1k%=Ms4)4o%{C*PyO{~syxIE8s>seu9P`*R!wR|u&)@N~Lp5xZ@v59;09a^vD1E{e+i)->6zbilNU!Ql}zrpbS;2QY3`Ob3}STx^pn=59b7HDfMFOu&(=Yr?KZLYS76To8dwRz4{1n=E&o4d!vx;%%q;dXo8O`XO2;Op|j+w&gy8wMAecnzEnUt&MMi4VcGaGP6X;#F`Vd@-IS;5xX?EimyqxCp)!&th;5`~&5GGvHrl#|*B4zemlR;M;KP`N-~Ha5elLYTgFlg<H=GJAc5H@VBUW7knRXJ*!Nlz~%5asCgfp4_~FWX9|8wfm!pIn33=B<$T908D7!EynKgq@*RH}oB_^(pMt+USP6cbiE<`h%6B+B-|@<L3VAQv%ktUaOW-{CY52>5mEjdkoND5ge22+=$4|#Im-n*0EKh>3fQ9f1_)i5-haWJxgC>T7BjA6UIAmfB_yBwaI1GFMegNM=@K5+p<c5O7;J=yp)kFe(5IzhX3O)$`3Eu(mH~7!whJ!=lznJ*L#7J;7d?+{^91Z^&-%sE#fxctOTRaT^pNW4=i~=8lkAe>e#|HWzrtUB`|06#U&Eiq`UncU+{&^UDGT(6<Pg3_JH8QTF)E%Y9@<&ZfHgOCrTHv^6u$YO*@*O^#@3@U;se6{1N2#~9wyr3(mfQRb<SdpVU&KTS6Hn(moSyHvjp_8APOXfq6m_MjEke&Z^tD)#{7ELtn3$UHaAv;aHfGXyCbcrIiquu4*79j4H_ODy1rEy=I9{4#<i&i4_E>t6uzVUg3vO%5QdgE*%bzj1=S`eY;IL$Y<HgBO$#-b`P9ZFR27DfFYf4gAl3L3jH@W9bL<$_9Sm1ab`6u!n+P+T^mOl<Y2e&mRQg<S?mX9~Nr%e0}78E#s#KeCl#(|UI<KW}Lr{I56dj$NC9uJwAVB&Z1U-&`tBfxR+5%7n=3Gm;kJqR9wZ#40_i4EXR_?ISrF!2?*A8vEIOsoe#hkt?ROYldy&3$I#6L1%NH=ZxReefO1zbW9~W8!;oAAB1%o4_q_>-pNmx8V2iPpR1gZiQRVHzxLi-@-RjvlZM9x1R6vGrv{O;9mGfYPN$r;oqt4nTFqL)<6yHnh3lTKFF@=O!NjXg7=2s3O0Zbq;?Q^7rd^CxQW}qd*J=-y3)jjU=R3(@Va0eejBy@z<c4v_|rfPEDgWh#3`QrBZ0#R{6u&$(1XXQy&OCRZcn2pn<xuj2|vxmRVIpnCE!Ki1>ni>vecdiUIlM}XAF1~e5{G?CN2U?z$MoJya?W%+7jT&@H^#o#Nh^b2@{_fewXL4J6v+M&f;D4_=MW-;7#zijpuz6Ydwe7XZc$Zms^9!YL?$=_<JT!&U08f&+!r_s@QoGacFzp6*-=>btTB(iKjBY%Jj1QcV1sf{!aK+%*j6@4y(W=XX~y)`yJ1n`0k{a<rPdEin#e`F&3E5mz$^v{u*&yauvXeaO;WTi_y#Sxwd!2c`O#gZ|hDpF)!k<U&L|A&E@^((ZhO*;VVWj%Ts0_tn{46;%oSA-RmYk@*J-69G9G}n@2u{=QVt<(aZ81Ox%XYVlirM-HC>G1^ao9OYR1+E8KdD;j?Ia_2XEri^pODZtF&Q?)bKNAzX6Bz!Tx4sJ#%Z3-4pL)x{<TgZ<${?Dt6%eZfoMec^q;i{XQ*9Rl7BzsbbSCI*0m;rEg64&DOq4!;S!89sp8`vT*$yq<}kCT<4@!0#YmAM6FM53dLIgx^l>9f9##UfgUW1Kt(jsqp3|%9uC_%!i)@FAnCxub{R$SO#wMCzz-Jo(`{Qq7pqU7KP`-^S~3}6{xKUR)X7nNfYJ37Vz>WTGGQ}DR@!%31CThIcm#;E#VjA83*1Bf7rw=CN2R>!6kPwcnSO#YD<A7;r-=x#NkGGDHEFvzuR+o3tV!x&f?wl*hK9u;LY%LynZL*@Pmls@0yrzV!h|k*01-D=WN}(<k#W(0N)4nvb;Zf$vlT=<T+l-L{)p7L>$`syCcVQwyqTU{&>#7cLu#I|C84($oGf0<QP00aaa{DIa}8f?N2=Y@%5*d<)@qYE#i(3i&q4WujVEyf&Ys*F1gdeN^tAB0^b$%vb@mtjyR9S;`nXdNhV&6IJ_g`xa10XzgOvDJ;m`Ar<di+%|2M|IgiCR@Y}jKO|0-7e(X6eIa~KC`Q>=t!1o5dEbnIGc03k~Q)}x^GW<sH4$pDPbpvmNTTgL(7HzK#H&G9d#fRXwZnWplHx}!|C086g2|k+I`d~eHN3*TYHqjMq3ct}rGZWW=HQ|!$2wn$oMr}>->_AOTJT=if(x)jsno@6hTNCX}bOyV^yO6&IY!8=QTksnAjnuXW+XZUc<7toHmOfqSA)nFm8YViJXashKUrPQg@LIU!YJg|KyHI;A*db7JEuL%9YtW}NJ>)Z5-pK5;DkeIBHQ?8pILpMPU{$!}8iAL>&!V;}SS3(X6;D<4M)avcj~dipOTL<kbHG~gb4{E_4~u8QC07NM_c)K*Gr?+snltg7iC%?1wdhfc`g6%QHE}lB5nj{8b@Z^<3@*89puER*)HVZ~25Oq&X@*{nJ{{@Nk$THp<9Q4m3V+<ha1(97W^l>12HU`gQ`-z|8mMW8N5<2dK11m-lzPh_;PrptAMj%)4x4xo91fS<1K@-3!_*E3hX!hf<B>5xK%YP8@dx#mPc-Mc$L+Pib7*zTCq!KCH#}DRjoe|ljNv!@k5cm}JuM%`>%YNBp5y<R$TxgAX#K+@$8*EL;c)AT;Ik<2F&rEQJ_`RE-#=hJ{6}8bp<h$@1)Kwaia5-NOU~9^fc9hL`1v*;j09@(@ynQhq)$_N$@$juqb9d6;?6e~YX{C@=bJbdakxL?xa4fzrR0y|sg18Ty`*M8p8dSnQTo)TS8d+Q@=+#tKOT!m;I_|SCPsrp;gTB#j)wn5?NIRkK+RA*L(xak=LkKHP@fsQnOg@u=dm~jzwI;D#7~~XpFPJVXX{3j-;ZYuzA^NYnxFCf%zN#p&lq}*;k_&$WO5_$So{}m`y4ef1RM#M+#qlW{3x{}!4ZL)k$6U;52DY%^!S&0%k8zH6&{O|;I_}Bp1Yn{yc#aKMxb1e9;NnbuvMVuYCKn?H=@rZdQ76;^6F*|onYbyunD}IiOWo!2^NK)39k;G0Kb9SZs29`vL?!z=mg#Xzn=VQV0rjy@UmbzcqeMF4~)<90uxaa4Z%+E#^j5D)!;?o1z;53klMz9@mb!`Y@^C1?g2Z&?={icv;WBrhiAYW!yAH?;rCE`FW4Dw^HCFVuqV8SiC*-uSRH-_yfPSt$EocB_JZ4d6BE~i1K?du+(!?Km%*#UqhJ&G_0)C&?}PWj^DKBj{5ccDO!NgWgG;Ut*cU#G+RMNu@TYivYQ*91@G>U;H2i7L;V`)5Y@NlY>G3DE!@&FDhj=|c;&4*L@kdNNX5v@Rp{@VbJD#(3kB~ovXA-_i^s>AU`uCu{`C$1ECh`pL3)=d=k>j~OU|+cPc=#+%VtjjfeJc4T@G=~O-$Wed!6j$w%AoDV(*$1=dRhLj$)zLi_^?<yaD1I&;=hQ)uOp62&ek<1|1X}>_)62u@`Q<7@mTy8ZtK1?@etS>F1ZBw5d1r8dxN*a_nD7!&~qM(<M7+MhfVzGIsC<QTynPVA@ck1jKepMUX~9u@dO@=rKz=brx-pMeA07Vas$D^aO)|J&!X*RxjlE>ipSzJa9cOobLSh2z2TB;2sVaKrnWbDE8PARqPB_Fc@AskIo`&^c_yy$9G>qvZsUCF&Zo95^|h$0MXlvmgVt;D0_tpBK)uB}@K(J4)q!zXZu9L-oRjC!`Yb<}yzODJJ^gI7r*C^|>rmf{x>nR$ejpO=KfycRf1=?(M;x|?pA)FFXte`)Cg7XE`&vFC;$9yB|AyPTe+(Z9PJ~Nt1UM4@5497)3GgGlwjPTQ;J0-Tn)u6eXzTy-j^~c>et*%!dLF>{0KF_9&+8-LLAb5^#hw$v2jP+%4?Y6_h1v(f2jF%N+1KMiJBP+o7o3N-{u=Lit}S>C{5<C0FZ8gzEHAL<Nqank1K>kU+-IT)7=cT!04xH(kJ<?61!^LABIpJ589<K#)DIz_XJQ~Y7(R%61k8s^&I9E=hESUi<^^i<@#Ld>^chSK`HX|epJ3u1a3K6%^7&v<xa9Icd5=NV76nfT)D*>26g`hV1L+~3(ek(&Pr1N*mN(G@EDFCTP<Jm{98WoX<pSgB0mcL4iPNVXJ<3sU`IWqmgZ1FHPkj?tf#u<nyAr$#UZ2|XV7Wj|c|0=aE9p~@9`&fVye_Y=1Y5vupOz*r1na{kR~Nhx-jdq-V7)+1eLOPey7Xy5j~3KhUY6H&!Jcs2r<aM-z?N{yl?6|O_oB8X*dkEV5|50zEPZ;?qbK#27x20)H~?<@1dsP#aLE;b`grdJ_6*eY!XslYpw9q$$nkD@)I<dn-N26U8%<niq8eBcUJV`vE5N%^dn0%qyen7{tOTzJuK=D7zkyy|1LNpQzPgDH;0^F=$yWl;gja%}4pxVEp!Qm@E4-EJUn|i6JQG)gXTm!K>aIm=g{Kz2TJ(~dOH4Ec&x5xj*92?|x1NjfT}&^jX=dUg@Dg|vat*+X;MQ{)zRTz(HEm3s3pRr{Aa@RUF5G%r<7-W?X6*accv`dX&!H|jf7-w$7X_=qucNjN*c$$gxjcMfVkS5hJ`<h<r@;4`*yXvpUDSL-ewv9ixEKC4`KjP^_*D25a2h;K?bqNpaGRfH;xjM}|D61E@Fn<k_%v`9{4;7l4~)<9&8mN4p#Q5Twtz3eKMT}-j<y+3A-+O-NzJ<^7J{$BH<MccE`(dpJNVwAm*sEqdI7iyZtE7CcpH2dF1feBx8aMaeHVNOK9|>TfuF){-BuIxz{POM%?0Pdw^F+pTokAY&bO`bx#W`IOt|&z!nccFmd`fvyov9@ui!tJ*kj^l@CEqG@Y&$=@b9Vp0o(((`4>%m3w{s(j{FPY4EPK1=fM}@-%|TsV0@PE24{eC;4|Pag0H~8q}T4iICc|nn%EA`fqzME8@L^AJ#XN9gZ`E;;q^A~1Guf5Z(=F<CR}n$z@_l{)V>M60e_FzOTZ7|w$A>h|9x;iTypP$@57f-J0JWYP_xs->)<l@d*ogNUx!=I4tzW4W%+DgzXpB<w{^jJwG%G6+2G6YJ=E?5cff0yb8cl5H-p#1Z!yuu#93e!_*w88U}gBt)ZPMifp-V1fK}mD;FZBM;5X5$dte;h$)9ba6L=H6Gx@4uO?XxK8Q|IQPSkb=yTjY6{&fQVFEDWpSQFkUP}do)EuK2~>d;GSE;VsEcmcdExfpmk+<F@0YfLYxX>Otscqu$at|8b6Zar7vyMkU))854SU~_mwa<#$p;nvd*Upsm=XWzHO(~f;#o4VlqX%ClN4e%^@7i!ys?cjS%>@@KLI2rx|{CV&h_*W)&P`87cJ>;J?@g?{bd^h>Y;B)ZF@Mpkh;a^g_8{7l8`4>%W1HXiCC;uEc1O6QRS@1>pHfpyA#%K8k)&G@1|2ZZ;0cXIs1?sk=ZNT#izE|iaHOow_0_VUtkXs3^f?Lmr_&%hU<x6<I5?l?pbsw8p3NC|7ZV9*){xP-7zz^ZGdA$VO2)A{cOuP(!442$&@MZWWYCi^72Wo=zZ4-Ppx#z(b;MTJP-wt|NKE=cnCU$|J!oM)F)x=crN%&Ow6z~c7E^5C3x591yDHET8yWpRbe-eBe{v`Yf@G1Cb)P5cqpXFP?r@`s)r{Pb5)8L!wwIwi)EyPPE)`HXFo5`&K*TSu57QR{Zw>-t`HQ*w+ty^s3Bk(1-<Wk^A@Ws@=1kQpl;B^XI4!3nHOe_Q!!zH%>TnJx5?P73Ipk}>^ncxce0&+=kCfs_~;af*9%ct-<34RK<b-{VH9xk~l;8gflYS)A7;4kNyahP};TnvB5#1a#)fQtfrF|QX>WBE%a=9_pITnK-U{A_SRfG_0rLTW6ZVPd9<_rdw_56CCMS#ZhC0F&?q)XoBD25M&EnT2loJQJ^)SPCwKe`q3Qq7ZxyF1dMNA-oXJJn&WcQhI&}rr>Xyn1eQlZ7O-Yt=|IY!k6JmflJ_%OpG(}JU9jZf{Cdn9t9tUKab}Ha4LMfi3ujAfzQLIlYa!92$$S=@DcbUc*cVh;M3?iJup7YA25+H@f7$B{Am-DO*{yWf=liJ@Im-wYDa;IK+PyTqtGpX2;URnv+yTPJZEAwI61(d<@K}FSU!f=kAYL*kF#yZg3kr`6kboE#`0k%M&!9UWAXL8<MZkb6T`ug0scC#U#CWLBk4C1-SYcQ3^nnhi4JWdd1dpD|3}P*{L;F0!(L`h*vtJ+NB*&YoAkWFy$1~J$A8sKSBC%dXTi$BrkDR8L+j9{h<!%g%QOGlhY%XsZ|~m!0ac9a%K'

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

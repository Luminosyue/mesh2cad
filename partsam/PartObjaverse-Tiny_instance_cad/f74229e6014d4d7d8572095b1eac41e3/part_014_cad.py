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

PART_NAME = 'part_014'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f74229e6014d4d7d8572095b1eac41e3/part_014.stl', 'relative_path': 'f74229e6014d4d7d8572095b1eac41e3/part_014.stl', 'source_sha256': '90954b20412346cb6a4e0da1e6895f2495a35558194a4cdd6061beae4733ff91', 'input_faces': 1545, 'input_vertices': 874, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.13040649890899658, -0.1735791563987732, -0.31578928232192993], [0.11301188915967941, -0.04760351777076721, -0.2631438672542572]]}
GEOMETRY_BASE85 = 'c$}r23Ajz=`}g-bM<SF&rNk~%rp%FXEAvd0*+xVnnNm@^BAS(G#7=|yWuDGC9PAWHDeTikYKuyxiS%ny|9xAZd;QnC_j<4Ez23L$+Sm89zU#i9v-f)LXHCzOo?UW^lnpumT^br+YhRfOy+a}Slnj*(O&vLL@|Y1LCtWdq!tGh1(x-j-Pjz1RzTJBE&k9Wq-C6yHk&{MDtllhKy~U`e)oX{VkGf^z<cY(^54~mL4I{;GKkVj7Bh&t*(ZeQ;OmAP_v`M4d;f6J8hi8QUAOAZ`zC(@GiLIiaciSMESaknB(bSJ|zdv_>pr2aS;Ito|^rYjzer&6^ozSN<eSZ9nj|2VGosCcXk;nx9-yKma8R*yea_{N9F@61icYD=jke|Bko73^pntdF<VeQwv-!t|>JD;DrZ*QO<&u{Md*VlFYt&3N9+llP29@u_lVAa!p?Bgaoynf>Eu<v(;Uz?H)@}ozd+UxWAyOHg?_XYaXT04KY(nY@S6X{$&8RW;R?hcF(T^I@UqbE+B{yw4j1-{=E|M0ziL4Iho(@yN=V!nO}Jv=TM<i}PocKUb0Pg}jeD}HmCWRRZ<|K-FVIJDLGdk>aQ2KmwG-_G$o_}NzP_l&l5;;kPFojM&KuD0E2XU5Q1z5N&-o9p=R&wDG#k3HBn(2sny>rJ0ucbTvKP{$pCe*9#6XFS$h>i=Ea1}202@Vl#>{+hhV_dUa}Zr>N=N9T9&`TG5By!tj?f0vC{U*l7=Zr<vx^Z20+$sj-R`gNzjf8_1azJ3o)?UfAjBNr5$j*mSs+<!bL<|Kps*t^A@I)7-e@3<w}_eci$@!vK($McbXzB&mn?Vb$sV+*!8-{<{4zT+Hgkev+j!zD`W^ZI(6ZM@qrCSH%Tjd%Nn_;{adwtB~1bpEnrkRN_E>Wr6hr?#AK@6R!-ymhO-Js+kff4jvuUVdnv4D@^Kb<WR?kNVn=K3A|W$PX{+>GSpP+IaOd;<X=l&rb&Vp$WG+=aZ(NZ}Iil+0BwceyDEJ7w`6$iC5poyZvS2)z|p&&b7YZ6<ISU8R#FFc{)D+?rXl|mKy!@z92tQSi$GJ=T#H$_OFfC^KHZXlY#z#+0OSb^~x6CxVUCkGRRMLn&Z^Ni#Iy$a2|-YI+hIbQ~!jW-#fnJ7H{3AhNqH2e!ONKXZ+Uf;HyKu9$7z@6?e`*6Rz<ex9Z_!pkM9>U%Y$VOuXxB{KQtix=NKCn+)>f^_KYJwXSTu`Ziwc%Eqg&@u7}czJ828ygeD@hq5|4^?d#(o4vm)bbNg>$d7fo-f4fp2b;a^ge$L22KmvO1~~2Se{Zw5PU44GCxiUZfPv2W_R@`;ef{!#r(~et_Dx^B+b<^G^@&fMyl1noPA*xH4D!Qa=X?^IcE@IKKSsOHO9uI&)_3^g-RrE0ch4s#-o4J6c=vpw@w;1Z_Ku@y>b$}rKQj1_J*WM?H8y+4QFwdN!XQ7gv#2v350>#A=UCU9lR<v?m$)z9trHXPp3jL7E&aW~TPLXxjwXZr#JDO>{r_^Hz*nEIe4GsO<4-kq+CTA;ubuGh!eo#iDSDMtpOXp;ymc7skW2>oq4v$3@6-N;0&krp%B)KU`Kg-y8IR8wc<Ur}VpTH8PjnjOi+9ftCf>a-HSzBG!Nj}wtHj4H?OWjO$LQf%$sk|P|LVKfYZLEYzlcvIPHpnmVSIM&!XQ6&#-Y>onVNZgleZ3I(<>GR`Ki)BosLgD^64gTKZaiYCmH0&=b!EL*SuYueBb|3=Xzv)y&i?j?)0^z^=W;r&v@aEP2M_*%>5=A=r6D89G`{DHhJqL{N9dakRQ9Xy%S&YKbyRD5*hqvGSE+T^2KYN*m&1B@meP~-t{&9`&pa3b)xrU)=zD{%@^;EQxoqVf8yg!S8ntkx5T&~lY#yR6@BsUdHA_^l0klK$u<7=^*n6i-TOcj@1BQEyn7#L;@!IKRIM<`Pn`IAkI&cf@=~M1AV2l=C%$<1I(YGO$w2?siT>}S=g*r@B!hh0j_dy)+KKNi@Avh*TD53lpnvM8WRM@8dr4qB;n8RMeLde6-<=Hf8%CV?S)b$w)u;8{dc(K%X?=|kpSLzYXgp^4j2HFoc+Bukyd94jKJlR^SLJ(;gPu>UujiBK;05{Kair&~44?Cr`u2QieLWv07CqrRZhF48zMgLrhiCfQ(erlv*w}pUc+u;E_4T?CUlq;wjU%o*)_1QvJ&OD4L9c7pcdu*s_Bv>N_qthQTb{Qb^tx<)_qvR4ulv@w@%FlJeT|RQ+MMSbFM8i%e7$dppL!tATMv3)WPQCairzIl&o_R#@3Ow$cSU0N=6R2sdtYaKy|0Vy8tH3C>n+-+bDp=q^#0TOdjF}uy<fGy#>YNunCGoG_x{=VdjA}HsbZeD-t_+5`tJRC{+GGldT{Umjql$7<7Yfy7~jTcJYN`J<0CB&<a+BtpO37s&qtBcFXnoWvp#=i_&k59Z=csPeB$E^9?$jGn?65UU!NaCpFEQ5t3!Q0HNHNd#s}Q*`@8!5YkhtGjnx?JYe%1>qyJX&^_M=UTVJ2k)wk~ftZ(D(djRXZ?*Xzd_8))VV`TWe$57wC_sH-yKIi;gZ~g0g8|%C8ZPd5#ZH%w)ZQ_rf+~6HA`X0&pdL4<~khj5G5Bi?U`ud(K_42w6-s7O}&8)BQ&D6K=*{rYe;ZbWhc<V&pvt{^PFA`&3^R=Vz2{U|sPuMiJ!CP1Q9@6^y9#Vb#p40j^-oEFwzWbiD#Z=#M)Azd8*Y~>W+xNiM*ZBC~lYPfc-}i<$Puk$EAAMh);q$&aku%KSzxqBLKVyFIVEGN+de-;t*4Ov#u@S}m{i5&ljqkqy$IqBAFusk?m@hEC#wT7X;;Vn1@36kkcZ9zV`Hr*Br&!;ePdWP6df&KazQ+1GUlYIS*Y)1xtn)$E*ZH9M_rI+7j(44JvcAqYg|=*2?>o*qpJjY^{tG{2zRdVGK4ZSj_!=LN<gWJ~H=WmuUcJVD+?Y4CzRnv)i!Swjf2~jT?R=&BcD^#w<r!c5uHPrN-dhhkuWEgrR}Ecvr|);^ysh<h-Zr*>ysv+CUfB9NFC6-&%X;tla<3Q0*Lmk?{kp#Isq@;_*Lm%5!<xSDsq^X9*ZFko>wJ26S_NMn>Usd{>w17_(~JFe&U%0hpY;IYP3QT(zuUhvO8LHz>u>vaowpr#UB{3$>%7NJ*Iig&*IlH3p0Un1zF60h;j^wIzO|399bGqKeRthRmqz~Yqvzpy75we9j>Y=AjwSWQpKE>bTF=-1y`r`FFVtKX=#M|<J8p?RIV)QSv=eI4a;3MOSZaTuuiwY@X+I+#U*i)^JNW;u{$As2d~E4d$2Z3<cG2@IgML?JZmut0`^EZhzvLYBwG-O+QJ^0id!^(5_OJi=tY!U=@ly{R+UxVR9UHI5hxk;ptW`n%82h8hD&KLVJ~Mn>cT~5Mubouy!hJ!0{JW-3`=hQ}<vY%d7wfy@<*Vk7Z^vV*^D6J}ihf-=8RUnr|Caf({=Rl}U6b{7T~nmT9lq}$YFa57<VX7c=-mJ8y5I5by#K5x1HXU#&1X;h_WTptw%C6>J5Ego`SD*D?DhHDzcwD<jc>EW_dWGInc;JuOvGOF^}D++%lLX8j{LpS_j}#-RL0lyf4uo>pRen(tgqLF)KwdN$4#$C*4OJ%{HJ}sy3*^N_4Rs}sBzeTJb50pek{iG;Ng?L<EGbN>+AJ5HY9ts@Aq<jx4vHAQ-jW2?fqSP|6qOh{$XIr)!sUZeK8^#<cEj6=Cprp*zwJMOZ0=<j&JXa@H6g<@a=t3s`FL8_Vs?u`g%VW?$pYE99YL?eZAj{?`Y@yo_gPCefPc*-`<y6-^SbfQtNActnn28@xLcG8RUlx`tJ4lT30q+&tt?#ex0`3JMQ$p-TLl2u}OEX_ST`hPR#i3bHUH|`umIL4(sc4N8-oXzJAf?8tdzGO?3G~zPi=tChNP;O*cR0>qmVqv%Wr;sc)bAtZ(D(bD#Cybz)z|oxf|>i5Xv?TT}5BzJ82Xdo3B{r_R5@iBInH)k$JZJQ?K2E01%IPsyXs?=sKb>f7s4V*8)|@y>I7hR<_-_>8~({m49y_4U0$qU|Z)_tEzc*4OtB>f84f*4Ox0R?#)Sdf@$u_4WOU`u6>d^=-U;KVyB3k4~(&#y5_5zm(zgekn1&*&6S0)Av^yzRq{7XuigK-1PmJ_4WOj`u2UA_1*Y7t=9O)9q;#27u>PNTW^soehBoV=Q!^PU7vc+h}Zix;v-K@cYO06()#Xtwh{~1c*mE!p3V6BUexu?dr|A_d(qIYxc_+Sds^%3ds_UA_qx_6K5^z!Uwyjw6~@>1%<9|s*w(l4_C2=sZM@rGeLhPD`rp=be(zn|eElBI+nWsXW3!q&@ePjn>e*c{XMBCn9~n_<t@pU;e1Y|Kz95<^yVl!|&PQ0^T`zZG&9%OMWPT*WXMRL|JD-x_Ykb?`YkhUa{Eqc?ekZhT%vx{1>->@Rb^b_wJ3nQ88*k^QtgrF$IxnvE_G7A2xxyene#!59e7;`4Y`k9YG=AC3YrW%I=kKhq^LMEu8`pZrwayP(U*`v-!?*eW?x^g-AU{>D1ozc@ef_TUmDbn!O7-phru8*GGVmk+@qF;NWRRa&bG~z(O&;^rt-C(T_&PtEnp1q8Z@e(iYki&PP2GR?I^TF<9@+Xjj~xE>>UG|_)p>2}>%4ZVey4Tby487e>+8I^`gUI4`ZnIq%UfULqy6Tt^Y){zE3m#^XVtgs5UlUcE8YI}I&VLQZ>v)n<VSXVvB&4@{k)CW^DXh={BPEI$AzxDu)eOlh@3pW&O0u2U5E8`T}Nc{N&nw{zkFekAKrSx8NU<$_5H3y?^1<9e(Jk_o$r6F#CmUC>3TxzyXy&;mS68X{<@yf_<BDOtyaO;j=O%w`0jeb=bNne)~&ARvA(Y7iC^4oy|-?4y-<eFdLi}gdZY~B#M|{q89woe?nBml>sIf>t*`5;)VJ%etgrErHdk&q-HurwsJ>kXXnkF$=eA?k0b1Y2+jW4}xAArzp!IbfpzE7;fY#S_fbRD+>i{!+*6+FPn00{Gx9!+<fY#S_fUd9SlOv4_gZ$8*vVneV-0ypW{AmA={l1<DZ2S6N;<-x${m_!{1KY`H->hTI@L9)beO<?x;j@m>_02lQ44-w3(O*mE28|=@>$p(gjw9=9e5`u?T<^Hhah>5auGP2ajSSz!+w(?-uko)m%=I1zJ?~jx&wJs6-JHK`)-h)ItYeH-=#lH~7d;PK-@R{nu9xq)>3QDz?s<Me)Ypz)N38E&NA``)_13vwr>w8nsrdU-a((sBb<p~H9gIG5yW^Ydto8Le8+&J_<D2Wa_1*Q8#qRfgPrXmDzTPLezPYckzI$I$^D|$a>wS*(-TzMw-`*ElU*qFFE9ZIZT<_DYulH%{+xtN4+jx5)Xnl=ObiX{$TjzQoYkj?sjZPn!=dE*HpJ{zvpBX9`l;^EO_y3DAzTQ_S{urL;J#Kp6ZhgIPkFLDi*N%IiV|;hrX7vSmzB=c*!}|K%5&HU>Ja512bB*=g|IY~DJ_lLf{r{L!ujYB{P@l`Jug_(nA*=Gd<4B+Ttgp{~sSkJLdB>4HS6W}6E92#M`j3x3w;JDlZdKnt=Nez*Q?aakZ=LINxApb8TYdXnZ+#nYpX;r!@zH;Z<$LQ~-%D8EeJ@e7O}@9^^}R=i&wCH`?R%08U;n?t!`J5f#u4jF<HN7Z_l+ao=U89g=Y&#&eeLV}BJ1n>qVT!1{q68R%KGmAzxmdy`QCca_g&W4_g&%UZ{>UILEook_`FX`-Lc(Q5Bk2&`ue_3efvJp`ZnIa5464;KW&%4e|evo;qyLIef$11!zVu8<b7Ygx$k3*ukT|cw|$WB9q;<S*ZS@{*kwQFd&j%JPqx0^SA=T);_F9!Uu}JTU+wzl{kHWrK2fgDMsJ<#`q*$`y^Y@Esqg2l@2+>nx9{_<pAm1@$68;n*L#}z+R^!o44?UnXq%B6z4fW{Bi484NAT_Zi}h{1oqw^u`|k#{yv29ibpFWtI)9|Too}*!M!cE-vcArL#b!*{=&fg+U(4|I-+7oi)8FqppN?<m@8T<-+32lLogcKmJ3qLjV57G_b^g)%I{z3MylbO(e7Wm#jj!{Y;g1ja>p|yFjqlF4;%Cgy8sEle%+DI%UB^5B3*WfYdF0f*BfkF9d1~wHJaw%1QD1+#|6Ypm-SxL0{N(E|cm1vLb)G%?=n2O+^Z3@+dHh7F-+cY6>jbQ?>jYfitShj-#>b~u-Q?>pUFTqYcU=U2#ySe)+xU!i6vlVg1OHijleb@V9f<XH9Y~@{!%e>aVx5Wgb)89kQY+u@a>p0GUEiX<UEh+pqN}fccOBQ!A)9>trR#8vuj_E4Uys=2ty^8s6FoB8_j`4{koDd5z>BAD^46QX9@zN09x2i9flc0eaOVw;uj`#6*FNp|W<8blbv;$Q;|BllVqI3K!zTalV%?YZb^Vz2b^Vz2b)8sj+uNJG<4D)7Szp(!rLx}f9Uom6m*KN6E}nSL*N?jH&icCU&h^bYJ?m?HYRg{VadYcx^GCkl>#noP{mS<}-F2!BkNdulyN=QLx{fh4`rHC<`?^lj`tHB~HauM5{r<WR)B3s&Gdj3#LD2V)epbK0TR*xk)cU$EG<06q0^jjx-Kq6;-D$kjr~+@l>$=tqpLMN?4r6`o=z3b~yXOJp>pEN4H|uh(ukoR*yL`T`6Slst6OL`1>pMQW4%zy;4mot?LSH*>o&2=YfBbbF(bqfu$A@*))_2#9zx1B}xUo*#`Wf+NUAOh!b=m{I^?x6&|9(FP_KWL#e{WCUzgD^D)4KDIbqs~%Q#@2QG-{aVpQ;p7{!<P9rz*!Z`oH?8D(g3H)cF7J->N+8qU=zpNcwX!E8SITeKGxc2)z$}IQ^NK{wzaZf+a_CKS009a`+)~qv$Yr8Mz;zZ^4oyxvSB=@CU^Fh#r7f6SEZE4F5>Xc{z^$4lgC<S#$#|`y{3wdUlS(&l2-0x&@Yf5_1)LDf}uiYtVi0Rm8MMYr_9c|E)jLpZ(}(@Kxzg^YrI>v_E`Z`qMA{X^J+3_mlf3x*fir+~MdAa8q(GLMy;;lKUe1GCZ8zndtrSMdTJii^4CGdmlOro=NUY=qqp$a;48jzoq~0BX<}&0)C0yx6mE1<a|plh$i8;h&g~Bg!dA&8QlsWAm(@UPk1vi8_-<%cVeU#L`zc_8;IG0CSciDnpzO83~wQ3A6f`sN=!|(7QBy`qv&^VO=806W$;mA&d7H3%xs5ce<@;w&tY5kNzBFQC2%QXq<%%EcK^%1OQ_#Vs9oVT{Ej{7QCMnYDSazC8<yIbL*I(N3QKJiqdr8xr=Mq$I|3aEze4T~bSEr1-_z%!AHq9`If#A%CyCjLz5yR3=1=r*cq=ivXde70G1BLvW$6E0ViM>!SoW2n&qb@k31SM-kKoG0)Iw{+g~WV^9)oKUa~WC%{*D;wbJ61T|7FCSgPse^zT)(`XeIa@Vx&Gq|H^jw5@MR8E#VRLT|aaHEIE?<8TvWgoZSBCK)4^d&CnL`XXI{2--i2>djmQOZbohev?9En+?Ua%@D1eNkIsRI@!PIL`@vE(C8-6`rm)n^z0`te43>ROsRhwqa2_$+(EH#r#8gFxz}txV2%QU8C8jnSg+C(Z82TT$HZfJu!SFF+q!vU!fvXU6F4_~8{gtR4;Ztm%ON{inXcJiWNlZ($I{hy-b0d8&+7Xr<$^9HH0ZUGG`dqXVJb>I5Xf;@JB=>FfYx;j6xuek0a0_xPqJL*OEID6OH=>*1QRL1+pN9YDd{+_vnC+$H&PJbt=aBm<S^!JV$DH#-UxR0pI}*JSewEyv=r{29<bH@g2Ja;13sh?Q3&xCm_o8SqSZZuIwIg~XEH(BpH6*$OjuJB%9R~l0m`~81@L*zkqJ7{`h&hG+1@|PT3EB!iMU2#lXjSTE4E1p%+@9?w<d#4$f+eRaH6q#p?nrJmv<h5;T&WS!qtr_W>Z22U6Wi6ul^PNKGs|JgIZBO)Zia87K1RdOvMo7(QX`^o!<)!`3VjBCn%n|(3;Z#;uc0r%Pmy~gItDHv_Z#$E_%(7LLmz^_Ax7#<^x_<cA0y^o^e$NTUCg;tv^9J$F){RZxG6Ec(7tetnETMX;a<cHL5IU1@_pYx?}eqte#&-gL^K6Ujn$$?L|emhoW@ckqJv<`Nl_!B@4{8d?SKx3+ml-bZ3RotyVQv2dbk6*H=#GfRmhbZ5v>UyC3iEr7`}<zXVDleIg<M}S{B|+?lb7!@U!G@LF2IGNbU=02!4j#G3Z!$3%TE-8(_(i+=tL#sH1O*k=hY`50-tuP&=ZBVc91!t<gj9UBuju9)x9|#PmgfhHoe4ZuAH&`y^&K`VV|JF%P51Vc91!H=<{79(|aYC1_T*!?N!T&YhyCvK?MR%uci%JdBt==uhx{eBZg~!?4s$gt`%}4NJ}B(&wTtz)~}}(C4D}!Zpb)i=GcJCiiai9ymsB99;sJB{zg-!*`QA799`A$=!hF!69;`7DP`_7aNFq4}Bk&eJ7{|(XZh5h&hBFh7S{S5d9oJM9k0VarhuHN6@d~pNaVg4N(_Ih&hh_3jafl)PiVH_&70A3!*vM4xd4c)Pm^0*$&IT9O_2&0$BF_OWlb60+%DE7Fq}XiI^1nC0vV`)@U1eEPXc!9RjDweHYygw<dQmIuss6ZYwkbzf10VG#8e!A-~}-v=-cx{Bh`bxB+eUM2Enovz_{GfJWdSvYdLA{pYh!_#Nu+2lRY+Id%39noaCt>S;N80)CphS&V)K$ElB}(a+%()I%Ko8s0^1tU!My_Qx!zUw5H7@VWG#?5{)L3pb=c&PD6Mz38KcXd8G!wsXGdg${-1W;^450(uL)D%%;)bJ2U@WVSPISD{Pb-?E+YnMCv8@;S~pl>LX<C)_B<8E@s$!*CnMRU`B`u^kylZO{-LVN7*IixS%~#~BY1^k4YG9H+h;qQAf=saM&*n=v4~j~YIS?uJ)pJLl7VXfFI%wsU@5iM{}jqqZMI?}1-R_vQNZXJeMb&#+x1{kL1BKNp}4;P=w|RuR979N{|YeI0U~ybk0Dr_%f0&vNqKCr7w>j+1kFj>8?;{#VY4Sx(;1<OtU%_WT@&o3mX${Tt59cJf3eM>r?FuPpIp$q{anj%l3j<TWN&xKH}iJN=n~-T@y;e@<jO?TJcT!hO?xZMM_iwX`MNh_<eTd$YZVw%&nHuzgqhb7!{G-kr21d|~=ihIY!(mhfxo&vM#XPFuncrazC;-lMc7{7?E={FLRiCt8NKAEB)W;N@)pC;eGLdn;&5_=|Mz?kuOh-Lxq@gJbmo`Ut!${n<-<dudDf-E_{%ET_Gdv?csidf%_){Ys8-etO@FSx(-I<Oml@_d&TFCr?yzgr$D-so`hHk?q_0e%;aDaCf*K+6b-(pN*D*&xQ|iEaf;H;v>8X-3@PoUq)BLFT+owFTzj4kE74PkHhoPm*DyEE9fft6}SL>A1;8uM1O|AgwJ6N$+$R&k8pjoF<c++fnE#ufTyE(!qed=&`04X;5Fz9cn$m^x)=Ts&dzc4S2&v*sE$faROchy5^Vstgu9|G;I42Fv;*7&?t(UlyTHxR`fxM28d?^v24|si9>`)_xG>w%J#Zns8eI;rh95^Cfggu&NAG~8U%Jq5qBUTt^UE0rqMhMS_+Eu@alWJU<88Ee8*TMqT%1LFXVF$YzGptaBcHYk>GuWH#RA$A{xr*JOU9G%S+p&`Yd-DGr!C=)w6z9az_yIL*BO_u)7Bx*15;^lDs4SZU42SBpVF4FjMFC=$4}6f@L4%dj?|s-r?esCcP8U|CON`VhgVXkSCS)q4`W`&_dVpuc6Vx5>a;sKvMu9%7V)#l5th0gMEoFfgylRikMqPla)gIc>r&T4$&qb2KP=<?v5Xwyfy7F^4<tvn_j68>^T&R2WLxUL8}Z%95iXJK#L9U^ct5!^E*dj#8k2K+3{k7+pe5k$)avc%RQLkMa}l&0JcXFHXlJ-Bd>MK<d>Q<EmZN9Ezf+UjQK_r#e1sRGufq%BIp`Dc9C$i96P^xFL+^p7!86cV@C^6?bRPTwya-(eFM@ZV`{5n%AE+GXKiC$o%(1TlSBBf6UEp@`H1sxj8oUTy055{Kp&Q|C@DJ#x@DFe$#+;0!N_>Rdp;yA~-~niNcmO;K9R!bp$Dl*uG4M!qAUqQ8k9LFm!)?*Va9g+{S{$wjALCpr=gDJygx^5(;Wyxg=zMq~JO!N!%QINrZ0DIvv>PnXv|Y2EXIRlI;4^ca=ZTZ>N7>GHFLEcKli&vAmPSj$k|Vh*(Y5dda_6E?!jdP?$ED!|S<bfPJw~qZJhtbOy9!+gOWr%=3a@4RF>=SD6X8|lCee@KcgS6iE`VkKZ^Q@}%W<}s6SEk71pbW}dBzm23oj<-Y4kz3JTZ;X&amu{6C?a6+l`26gI){AiCKX@1-BulBYHi&f|y<CI=CY-5wthFi<lqL&)^6#4be`p?3echKN4Fi+u3eN%!TL`u<R>E{g$G38`5VJso#mzuCTltl6MO?qqo3U6LTv%5e`$YSEF6w-?E(g3sZ+zz;9Adzo8|GeUAEg6FmUmPaQmmu7&TQzwbvEz_-z_cc72JchY~ip%22d>8Cr<N8#t`kJ;!`@LL@B=h1cWf9Z?2(9ejylw&UY>(U3p*D(GsMeD+o8PC_C-QedLpOeu^aDwsnJo+U3J>x2Yu7fXO{Cv-N`k2^j7$=vY#o&I7hilNf@D0>`KeRJEn)<#0y%rup9gjw@hp(evN1(motEu7Z&`xlL9Ory`HF^d79p}dioNLb{b}Q$*@6eCn=Qw|DMc2Z&Qrpj=^I*BA$URmT*O|s_%eA2`d2OkE<;&Q<jM^8zknb$lg)8_CCy9}JqcHlLhqtr6oiU-jknM$x3FSF#&tXg`PiK2NV?ucv+tU~m$}`xW!I)5ffb9nu6UvL&Uc{JC-of?`#)R@8Z2!UdQLfAwsmz#AZpU^z#)R@Twx=;BlozqRh%uqOjqPoW3FRNy{(&)}T#4~gi7}zvj_r1g3FQH74`56vk79ciV?uch+hZ6L$|Knx$(T^?&vt*tgmPQ9+cGAUE3#dYF`;~n@p6nYq5KBhZ!jj57qY#OF`+z#?J3m0@J;DH>zn=zL%YJ=Lh1Xw^yjLO!#A=$jF|pt3wR(glh8Zi{={63)`BMy^B6i0UYGuCNPk{I{{vr5?xpCt@MGjIMPG+sA@@=A3HVZS&qDtRIlPqI^=K~qD7h2SJK(d({VC+=H}HCLKSlS#6UiNbj)H$8_Y-sv{3*FVqeo%MYf7$gSGGSPcOAL`{+ZkoS&se-HzhZWHiKoK#9W4!$#OVM%!O!8SoU8-jBstXFC^w1v@(1RF$2(+@HxbkM{B_Yh#8J{gUb_hDcT$!PRvbcUs!6U4t*|q9xOF8pFS5|4ol4}qt8X3gwG{c`dl;wzfNv0nh!rg?j7iKSaKxy8}wWHKbPFSXcE4I+)?OgSaQCl&qepad&xbDeg}^tw=3Em-b3yNG!H&X?!Rajb<vgFW@roeUt**dM9ad>h^dLzhRYCB8@&RqNlaz5iZU@R(bjNfVrrpv;FiR6Lwmrrh-r?tgu4;b7rhQ{PE0qn2i%vKu4s3-8!<PcW8kjDv_M<IHxhFvIs<M&Of9qyd?zvU(E0GC{En;i_rOvc-_y6Eg|O7dhxD!JF<5HjCi+&iC%li`Jai-c9l6ryqB-<`cXC^xtzg-gL!XPD54RwuHhKkImY6HhdRi;QR6(mM6Vn=P16LuY4q6v(O-v887hH#!mS}73e`2mfuZLR_(*x}VUq?)Lv?ttym@(*BxH~be&<H$+m>KBZa4TZ!pmpIH#LP#Zg7fIRW#|gH4!P%{<>2|`E=O0w%gB8aT>zg)ZV1hWmy?^1Zi1gAcRG3(93ofhSM+;oIiK7l`XRi5-}WDL87wu^oLUf#Y7M3L6`>YHbKrW!v_Z$iRf(yKo&mQZrWZO9u1id7w7Av<G1sG$;MT<SLNA7|C#ENQE8L5iv1l8(CovIp9NdOF7)$I>wj;#UMTf$76Y~^$A1pOfK%a{)g6oo74s8ZMMea&;F}#A@1?atSGy1(8ZCuRuN^&=$o8blI-h~c<v&ogZ5&bjd@FsFUL{sox<lclvV9Al(Li7vxLvoLyf5A7A+Y`MAE+ls&S^ys-SI&i^6*w>UB)1h>46eX=P+}@j)3QCC-!K}z36>h0LhXo7g{8*Mq;^Elg(nenD>@mzn3y(befU;l#-X>sZHO6)4u;1OGZY;K4<+V4^d5K%^-%yn&-PGqo1vZI`^a64E`%46doLP;n~{4lS_xiAeJrMpt!&>*?htekd@;FFBcgv(FI%aP&G46O4<R>#)`KPIZ)!yJ5S$|SFZ2`~A@?G*H2ej*1?U#|FLI@JM8nk4MdTJki^8%mOr42#fr}AS1kHk*6B9*mgo_Z9gNEQJG2_t*a1JqNpxN+vVkV+f;8uL!E6^ga)L3O|MDzk!YHSuYBKiz0$0<RLh^~T1k=q$93g1KSLUc9!Jh?ISX}B}FmC)a)mxbhRMc;s9<PJh-!j;IC8WBAVZzcCjbT>SR+<NF__-}F#q3^+8l6wk00@owAG&&qUMD7+e0iPmQYDe_HaA|UjqJ3c5Cox^nGpVDZ#AKoEVcB;kwIg~VoJC9sy&Arem<ebVI7Cb~+5w(G%oMZ%oK4J`XkT~=F;mf|@R`J%i;jS&5;GaC51&g+eRK*unV4J9%J3O{-{R<*u++@6^ttH$u++@&^ttF)u++?3^ttE<@Jw<iqf_C-<i3Z#5AP=T2>LZVncU&%4e)#9CeSzGBjo-U{R19OZXfhI_`k$REr=GUF8UDD9_<LrzT(t^=tXdQVy;H7fiEPc3R(@mnwSn~C%6hR4bVn#2V(l7*TW5nX^LJ2_a$ZoIudS5OntN=Jc5`h=xtg<#8gJB!c&Nuh0ca66LSGt9-c+aGw5@0g1%dYu7NKgw<uZ+eumuD=vsIcxlg0d!bQoI`W5}1TCUIU8;s6^myo{=eG`6=HkY7l;PD}+z8^%Ng?m%4<I(%!2Gn0~bShkdI%|O50GFYjDxlZFrKp=SXh--w>Z25T4SWf8a30zTZb*M$f?f|_OTRWmN5Z$zf7hb7!4J_Nx1h7(7wMyi(C6UoA?JMYBDxkn7;?t{cJwXy*N`)w527Ey=P+(%{~zoVuF3d32mOQCPK?8vXmNN5<E;~V5j=)*H3Y2&-^}<KgEoRkGfr+suYw0N9!8@L;f~bzV6-Y+gSzdAmWR)#hHIe3h&>T<&Zn|p^mq8PkaK=Kfqn&VqqaXo--pjne=bXZs>5fq-6!4F4RRhr2f>Zg`zjG%i5%g6>3w6foV>B*2)9e`YZ7wunvf%Wt(=3hoV*d_2oFo|>mPFR`jaEvKD}>XmXkM-9O2v3`)&<6dAE`y+&0U}xiZV)fowmX-uFnz$$Nwx;aAh2m(rhI=-com>744cQ=PViUrX<MIpnnWGHnUZO@AJyy@zQ_xJWvuWR}xjN!k*AH@$CX$Z2mUZ3$1Ht!ePXZ2yq{{6c%8(w6YYX+98g+B-m7!cplP+UZAI!XKqS`)O}KZ3_RG{u~cE?H#8r;VWsYE!>aoT^y^A(EV_!ET^qAvK&56+ZAb}5qu@vmuES#6|)>J#dfvyzH-EuBS*N2)E4pW$Pt$Mtws%>O^$5u;QPhVm*6-&2Yncx1K*5JfNzF7qy6B{@a5>0@a1q>v?5#<E`gSVOTcHLXTxW~CDHTYlJEs+CHMlk2HFI!0e3<B!(HHU=&kTL_yP10_yPC@^kw)3_#Jd7{0{s%dI0_$K8YTOPr{|C9jS-Xe1sdLm&1+W-e^0xH#`y@1o!Ncm0dRHfB&JR@wN7qnUKCP%co@MfB%#J&o+J49yxLH82;rXo9X{2mb{rO(rvl_;8M>nXUH>3`sO?P^nv_Pu8g7o0XqLpUH'

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

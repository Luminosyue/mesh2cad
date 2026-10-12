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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/00790c705e4c4a1fbc0af9bf5c9e9525/part_008.stl', 'relative_path': '00790c705e4c4a1fbc0af9bf5c9e9525/part_008.stl', 'source_sha256': 'f205e935f63b04c4d9a04850ddf95f4287a786a4c29430b8b7c9e1c7c403fabc', 'input_faces': 760, 'input_vertices': 432, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15739694237709045, -0.20690949261188507, 0.15599174797534943], [-0.15188859403133392, -0.20051078498363495, 0.16092151403427124]]}
GEOMETRY_BASE85 = 'c$}r22ap!knudFZG~^*?XyTC5kYfW9BxfWyVTclk9Ge`5oP$7v<P0LBA~Xh2z<?lEl+Xy`1rb5?f`G96^FF_Oduz99YnNMH@AJQP{Q5hwPoJK;Et@1sn%U65{6<Wv*vm$-m-zBZV`Mf)#SI_PzgJv*>A^$CMi|kFe&RoLY4di?T6T;uMj7K{ddJ208Xi;4jH%J5N=!*Jrq7V!BZl`F+<nOK-f<znL66tt<6ipl{dx?Id-=O)h1l{X&Ddfk&57p!@n5Q!DOk%3e|-F<Iy+OGPSjClKCb;z-MfY4m(85$dl_mc`o@`piN0k-$!}9m<rl~|>plG}q;}){iN5n=fkfZ`E>mK8>xtsHb>$nio+Xxd9u!RUtta_azMbOx#bXnFGe*9#%G7-av`F;*o2JTF`Acz@6jA)E@~s)VulIwce2U3;b}7CQSyA!F<xBM4*yoB9TTJCg$TtiBn&|tPvLyOm3H){W6vt9N#?`!vQ-=DUsiS<($u~c_uQ<)Jt9%>z##8dSR7v$pCEtqsP333h(tVT4cS^rdo)=0ePOUsDzbS8G96P`AvC82m`(1HP<W;?X$gTVO8Pz^-)m5Go<U3^yjfat?6MY-sYnf8@+FwQOR!zRO;Sa@+D4;ys=1TPKZF$s>QRGudzE%5CVtJ!(Vfp{esq%A`kG-iLdEyt3P(INbZ{`~Ot>iPMn%W_keB*FQwdaQJil0)x>;0H`Uvqal)$3Uf)pyp7MBgotT5%r9x2`=_o>PmeUiam@fBr=N8P#s@$@i+<Q9InwI5CD3e`{{#|F7oqJ5hevUFEYRhx)xb_bnW$cG#uyZ$Heg@)guR=E_$T=NtL{{(Bk^4e}_@!}5)1v`_0AYPSROt;tUk%Ud66{J1lTlcj{(t#3EATM_)*8n;FY&1-vkHnqd9T*~vl>gBeU?-zKe_B>Tcah_*YKG!m6JS5at`N#78k;Rl}ov!jPW|9BKt;9Iqo~)|ZY5ddbFMo&H-#aGX+n+Pg&hA0^Zok{g|5#47+XDH<3t#Ki5se39C~>}tQJyhflz%tkR8xQ1zUGlpK)zY(s{CuIR6ZfI{LbGi|GX)b&%;d0|Lq)!@!e<2)B6R#dJ)Y>v$On<<Xa2BRh&^t<VVRj&TBlo8C5UqW=746aX+ZOZ)qHwljQp`*VJyqGB7^z*A`NJ3wKig{**y+zEu8Jy|gNyS-v+)`B+s`YMwrgmjASX+P`K;<+EJA9Zfs;RzEt?@~ynzD4#aTRQ_>#&6k>&mA|h%Eg!#46^;M1gVhcR^1aUa<@b0^@$<=dhbm8Jrt-H^5GQ9P<+<f`#krVH<v%&6dd-heeT&L>uE%PeuN)BY-PCFy`(-~Rwp$YU-nt9wuU2XwBR;L_8~=skKltmT#QQdvZ*MB6_{;k#PI39p>5Ga}KE3ihkVf%Of2DqJNV^S@Z}%^w`MbN1%HK>Kh+`GZ$T-1Y__h2?jN3)>t>UFL4lneUUr@gP=&agva0Kg2DwTgwT=$LcC4ZHCFIMr54QhYChkU2G+QHqQT<vo|rQ#1eukvHm@6JEuTStm2pRPTWPn>+C@Mp^Bq}tO;g}?4|`Ary~Z$|09nNBPI@krfwkbG~k^6_7!QT!J2{RoW*W1sTzN2XBx)}N@~+dWCVuN^DjPEJ16>6aw(ota;%{D(X*_9mDAwc@x*UuZmRm+#&=qw+17cW>e!P<-Q)D8<Pj-$<_b-j>W7KmC&h?rV0;rZ`=b@f=q>SmU+sxkco=Lq1mi{nWqC{iK0*urIRCoRsfgI;nh0sh$0`@||;vV||`f>(AVzf&TRh=F>QtM){Q|6o1y!#C9;p$Tv@`zShKO<&z<4U_2Xj3b9{J60BD{%|~l<l0bVpNz@L`xFo@TXMbf6mhb0OzgWXGFN`ko9p<}Ppt#Dvk|Z$B-Fv3WmzQr`uBLf$CO+U>(OSp6g2R+g3H(|WwT>;<`evBK*;`Z3$4R5)=ag>`FRwV+S;tb4|5!_L8jn?ceB0If;P36P@;4$?zDYf;KSd{~-LA;@zCN!0`dahLJr@~hf2Tx@@>wh2n5};I7N-gL_J=0|>%7w%|AFEg`83}Arjdd9>mJg6#<3y;&k^rXS@nCh$iTdCqqVQLD?|qSajMo&rzrWi|3Krd*<;P$0+E6B&}^u2^|#MB505MF=ZL^_$||pYvNsujfSx<XVfI&@BLeH5F+}?)vz~nG=i`C((5f5}SWnEQns>et5qQ4%_4S@&eq{vaoq0s-fVs>F>=P`%vg$QezS&gwb#7=q@y8p1b<)|#K4+*Ac<vZK6bbm@{xz<uo&EmYx5oR5Gf(TJ)71#<Pwbm||1ugFfp&22Y9H>`#y@aW^*W|;V&^vk`x);Z?}?9Ie3aOZtYg+9*1b#etqjV?JjC<&TlwLAj`2e87sh${;pd$-UE{%@D?hydanfrXI+Nsw*K;#6xBME!XPnz}d9IZuAND^+5se==ul(?H&8W)z)b;0z^Y(j+6U#pEOZnk_i(9v(+Gn-=@ci|6X*_uI<%iodJWs9u^26(})mQH$MlZ^<Z*k(Z?wK9rho6JqL#^jVRq|n<Y|gA5@U3X&?~dX57{h(3m$590{Vn;kZ?_88(tYpzrT96uo?El^Ugmx)Km5MnoUFlfO1`z_u<kqOQDVOvd*vHz-ckO;o+tYLHsbJp;q|Ys{HOmF7(dP|JvW_+#F=~|uwJ>N@p->6((3)x8;JkmDfzoJkGzKX;rEEcdcU?S$`7ws-qoxD-z-PHmN38a5QlkZ-eUipjq<#YxE-|)nAe}FUc6rzNp$|;?#KT?<I~z&LG@iC-`xE{;JN8I&jRh~Okm$NPQLR%>#Ea2^VDc5-<$Ea{1@8)*tegme6Dv@-@zKU#+9dm^5OAg9+z)@aY*^MVqdpWzCrug`&dsVJPnKoqc+clrt-}w-V3tnxojkrAAX;;hBTCa_le@qIjA@zwQq6Wmmhv#_TFir_DqoP`sA5S`#?LM^1Q#BhRU1xo?TVX{d6Pb_u#&*4k*5-@ocvU=3}kbbHp!89L^csMtbjdp8P4F^9p0J&J)~^<%iEVoJ%@~vGJXBitip}-EigmEf28nso%Y2@{N}J<!8})>)?maVT=NbZ!M5-zEwl@%{E%~9ZGr5XPlurr!sm6<J)W0?^aXtY;;}Y^PtY(>=^v?dR|yhbslKtl5Z{9r}iAKacHi5toBK*eUwvjoXRK1AGSy3Pig<)KYSGMjYnFajeGL_(Uk9|{iHcdzSUd%E~EKG^~<w=$>)5=AIiDnS@~wpU4i*x918m8IIRO-9C0|ma=Iyw(_OxQw1M`4Qyles8~Jwoojk{%DgO086o>OVtF_{oJ@GmBGaATu^U1ffG*-PnoTmHU{$1t6=a5xZ-kTub<ebxsC4N?X&P$yb%Ab0u{QEXjzhs`J`@Szfd`=ra|FrwcH)i~z{Bsc}FXey!S^1}@eeV6H@pihp_SJnf4*kr(5ntzWUb7C$Gy4OLt97-te?G2p;$@Q`KDTszm3MO9SNZVyYP`-X>@vT~51;F%(fNr{P`*7t<HXN4N&YMMlqcua_7;_QdjG<_)_J&HOXoROw0yf}L*+kViu{DTYM<~q{1wiBj{U6qa-Q!@(0P>m=#Kiak;bQ&U*}`qxA@UbRIlsP<u{Y>e5rY4&DHybQAxht>`#q{lZs<Bxvl)e=ggUV@SOdp;@@bl_)TZ4{NbOJKj-Iu)t>6FLGqpG`fC5Q8s}EgTk<*o_u_P3VLks*^*!8L@jpmVeD|it8{Z?G#X1l1y2^K&ysB}&SmWHgb3^%aPHT1OtN5L6us*j}oYD&wKf8RB?<v*?acci}ud97hDSvM~^K>~r=j7&tegQxH9ml+_^B=RIe0QGaixs8$V&?FbPiK`ka&hitU6apu0W(48UCz3zx^FVdH`Dv0_0<*i%Qm%xl}!C^9Fy;yYNa^wa~0?6WyZh0kNA1@-fGR2A3neJZVytP6TegZ@OPYp_{HSAQEE@`+<e8^e~IzTIGI3w=gBwwH)8&>E_J@dc;FoS(h&Jszg55U-O6bo-|ux%<?D4)eG4sC{9O2)^Lt0Nf3Wv{BcJbR)`g*p(?-5`LF3K;Lha+exS;!Tj%uvYxq-b!zV)j5(LFL#^{swh^>P&7?=f8YfAO{M%lDUX94{V!dN<X#_cE1FA>X>Bb=xmAgMH3d%7^n|`_M?m`CPs;umj(B7AVhC^1W}Ak8_**PWe*fr<m&NJ)R?fr2O!AE5Enmo4Y=j&$*)2VvO47-LuMvb8_o2>vIG7_Wc&RZ)>d&ek%D^RF^=1h5hjNJGYqPIAhPKUTvGo&!KiUi=LLBlKQ65cry=vs`#9j8l$xSyG!MVzgL<+kpB?*KHnFNtz+4rpHle^HuF*aVqZV0dU4JZKA*8)k?%ybQ~Y{bul(pw)c#9!9&XK6KKA2}SvNEvjij{yV)^dv&Wdx3bt#kl@OK$w;&`>sf{#>R&YAtutmpSm=)M)>)W5e@sC}l$cjp%f<nKkv51)6rHS}C_?|6ZIuTy!l;=eeqIN3Y#y-Drwt&$)9Zsk_jKFWA@OzoMWb)de^arxe7YG-Ty619Ib`QdYTv)v@-mweOHI^(ZbJG;4#2A=!QMxLi>-sd@}^Szf7lYOK7@OMe?d+Iy>J(Z_l?1>t;R)_b3`{7cGZ%leu`4{UhzwILR`>i9&Km45{LihC!%QtqaU#v$OSJnpkF3(4ErPf1Z+dC@XrbA#{xeMhx%rA4J)>XfPeD7C{ALFX}#n^l}@LVv<X+3dz$T!-TRzAIGpL&M_>zg-A^UnMEP+<S#3|F4+HTi#^uX<CMcW(vu?e_Vpx^FM};qN}i9F=!Y9#ot<y)}LYYdpB`9Srn)`1xf`!k;@paSE+eo|_LS&V9`b`)kGbpY9Lr6Resu*pJEg7qBknRJ*y4_o-hB_fVV@3z?_;0`uMN$ap@oH}JgkKjyix0H1SXqnO&wuevv|4!ij^-aK!Q;`4pYy{2|EX6y;<8^ilLYr}5!7w<1-+3D<)@dpf1`An-7=i6P%r*(hTE0*WZ(Vc<u<J{AD^K$P9>|5L^jE5Q96~A2{)wizJbE~F&@3h*@nx^NGl|z2`Jlt!}{v<-ayF}y1PEGzDwguK1W4-#_NZ1;9UOP7#{|~nWo(oo;Ijo0U0{da_9^-$C{P6o%cszLTZC3eSgH_+{%N2j>roeb`{+P$}2>%T0LvqD&CvQ}qoabAW<(p|Y2KHl46Xow*b~T<82FmZL@o!X<@2Bajb{L~^=>N1nu>QE6)n8^+`Qi7zaD9!~^?`kYw~+BxWPM;iZ>&-OI-}PqKF=e|=Q%Y{zCA8p{-=7rSRbxY`8>4eMedt#O<<gu6Ewf<l&e)QZ>YvkrlpE=epO&UX>C*cc&X)kjb2y#JXbr|XICf=@1br>=3TQDf%U{&mB4dEe)#>uzQTCkxje8xaSpNmpIN5(Jg5BU%=aIc^1RkQ)~v$*WbxuaKUz~&Uq7{c_x?!vT~%Ly@S?yz)}5{TT89>@zSD;(|D<}p7<J@3UQ7Aybzh_80^OJQn()5Vn>{};->p{}C(q{v_Bq~b)Yq67cuskXRA2k*>_C5c5v-H9W~pB6W4&K#|5fsh9BnnOo-!V4$@fl<QadkVJpVOA<-4dIynMvjJv}fV|9*cdH9fG;u}ATKk$qa=x!^CSUOAjV`#ZnW4oxSkJ&*Scj9YKVB$bbxp!Qs@b<8+2QF)e8eckM=C-008%nLIW>rX5B&RN<&h3e(!9v4`j!|#JmjnRrzWW3tJR(<`|qZH?f=8;`P>!f{nxcr1MfjDN*;emGhdtJ>kOz|6!Q2bwB`Yi*0J^7D>={L<nFGIY%QW}|!K0W^JPbWiW=wDd>`#+uRU*UiCr<0W{mHq$z>14eK!x;SX>WR*Rd&1+<W$<`-E?0;*pj+XP?t(YKo6$Y+W_UZg58e*%MEAlw;T`C1cn7=%-3D)gU35L{!Yk1w@Je_#IuV`?k3@UHBjHZyD{v>c7Frsv1s6rL!A0RLXfikp9Etv6h$G?O4e2%bclav$F?<z1fxZWyfDfV{!Uy3a=$G&j_#}E04(UJOlkidWG<+1^#TDXX=(q4O_%rkd{26>6{Rut~UqOF{ufRU~PuPbqp+CTv;Lp*o;m_d@&_nPC@M?4}yc!;g_JoJRUC|bBSGWmU18xFWMNPOWoDWR{=Y!LuN#OKwGSq;R!I5YL90?~yQ@}~#v}j&9EnEU^2$z5xqYm5{o`n7ePlE5E=_ADV;M5V);&5uX09p?&09QwQ!qwrn=y<p-JOrH!4}l%75U)Ttz#CY<R&a&*4RkyF2D}m732%hoM0db%!kf@7@FsX2>cZ>bRp?516+9oE4bO)sp(Ei*@IbT^JP>Yy)`DBWRnekwRk#qE1ug_<LL=c!a0D7!zasb@;)jOxD*O<>jGllm!ybAN_Tb&<5qLMe2R#Xg^eDUs-iq#mx568_Li{Fr41N>dfqn+>fZsvS!|%W!p;zFK;8Um%pMpO{FTtO}pP-+^pTKXUAHZ+J8_?D826zfO6rKXdp<UrPxC7b*?f}<EtHSl+Dri2q3S0n94;O$lpvmA2a1<H|N5RR_q;PULC7Kpa31>n}z?tB(Xk)l6+!UPzH-#sl_uvWe9W=Cl-QjnLQ$$D$z$xH7XmvObTmfwhSAZL%L*T}+jXJOm59bQ;Jah%Tg7s@2SBRIQ8{wt!YV=KbHM|zx1h0kHpzGi@@N#q&yc}ML&W9Jm)6hxqG<XC$5FP<{M_a(%;YMgxxDi|tEd*DD^P`#I{BSfH0Y}3I8d|>$euwyhA-xPgfWJdM_&fMGx*I+YZ%6mQA>9gZhqs^`;Vtkct`M(8--K7fE6^SA3V1#G4!j=TjD7@fhIgW;;GOV(^iz00ybt{Z-Un|(--frrZ=f6CH{coQ6nF+a5RHQe!rjphaCf*hS|4r=*F~$qb>WI=0k|Su5X}G=gfpX2aAr6)njB6Ir$ST0so->ICO93O11$^ZfGeR*;Yx5zbOPKG9*f?A$HG6Nq4n!Weup?ogftJF1kQn0fOEj5(8h2n*g|dCf?K1*;nr{;t`JW_=fU$>zou}7cn-Q6o&zsH*TM_n#poJ%F}w&}4ljZe(1maUJOiBu&w$6FBj9mxf3!Q?A8vy-g4@7#(28&!xGb6<E(_;Iqv70e8q|Q(z|Re7X#IN572^Bockq4qB6=LY2)~bRheNsrejk1p-2}f2ALa_Ni>`!ScnP`!UIH&f*TW0p#pq^uF}xJr2``0Lq5I)g@LF^qycS-LZiAP@i_kaVMeuZV20R@ej1Ghc!@bb%a4)zM+8XWzH%IHj&EYy|MYs-J9xVu$hYO>b;lglsG&P(Z&WNUhGs4kmIyf56g64p;z=hCCa3Q!l+7hk~w?W6kZQya}kMKD7IvQHPuJb#@FVGxt=n8RWyi#yxxG-wLh2hF*Yq&Dp5bXmugkR$daXdN&p2GSS&lTbc=mK~GJQZCGPlacqi{P2?bTk2;4o^mBz?0#z=s0*RJP7R%4}!a*ZQ!nO6SNN81g?gbg{#5E(A;n_I47D0&IzYNL+e*6euwxkLwX<n3;q?o2>%LygT4=k^j-KH_yT$uz5sv472>y07k&#~hc1EF!3)rZ@B%miT?{9{Gts5+On5fB3Z4zmL)XId;5q1Wcn&-bT?9{qN1@Z<QScyiFgytEi}r&1!rjnLa5uOe+8k~Nzlzp@UxjO<<>A_JIkYfb4lasjhl|2F(Ts3TI4c?rXN9w&S>SANF0>Gw3oeCLhfBd0+6K1Z_UJgcJv<)04v&YwM_<6-!_Uyr`t^+8Ax_JhRv1nT=S3^SdEqi>L%0lF6MYS?2{+{maU2>C$FqLLafNs&Iu#xYk3wg{qu?><ba)Ir8l4P}hKHeJ;bHLW=pguYxEtCP?glqUo50QCx@a}HE?gch2A78mqB-G$a8@)GoE45jL+e)*zeD`gkp2okg?~Z6fkS!${sq2^eg)r!Z*ztC3-m4c3-|!K4n6>{K^MSl;Q43*JRhEl&V;AJW6;^~7<eQ)4;~4RK<B_C;COTz91jmeN5RA30q7uj0Ne-d3-^I-v>R;09np4hN4ORGD%=WgfYyc^z_rkFa4on3S`@ATmqc^ICE@&NRyaSL8_fpihV!7g;5={)S_+PVV^Ir^h3ld1;d=0E=y>=wcp~~eJP|&JK7-G}kI~Tj^_brwPRW{<7fuOhN6Wz3;TW_g90SLqP2pI$Hdlz-qj7K?>sNcO5cfbw!9C!<=oq*!JOCXH4}klj!{B~!Z}fGzH{1p726us5q0Qk|aDB8cTpzB2mWQjrCDDR#N!UcQ!X}&%je;}6$<fgIm7L!pequ;}fkS#1egglA-iH5#A902F7WxHz3qFe;fX~8v(KYa1co{k$UIx!Xr^2(~(dZa>G&~#~2@i*dpd;WR@at$i{5sqp9R~M@`=JBiesFKJ58NB>f!c5nxHH-j?hLm@TfuGNW@rPr8T<-b3w{NziB^DX!j;jIaAmkOnjbC=7e{l$#o;1o9=Hfx42^+{!DY}`xC~qktp`_w8=<ekjo>cmM7Rq)89fJ2hR>jn;WO~R(9rtzFMfwODQjAGI4PU~je#@3`OsK6A6x>h4VQo`afSF*v_0IO_3Krx5Vu78!Y$zr=m59_+!^f$cZNHnz2S~<JG2Yj4sM3Ff}6n&(E4x#xCUAUt^t=rOTy*gBB%)$fpei5;aqS!G&$U|NknAkB>&U@HQRsw3w^&a0{=&C|MkBN{#nw$|ChC1#`^n@lv*}P7CKipB47S5v;eFQ%|PQn0LLx)V*'

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

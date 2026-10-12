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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f121301624174b179ca4d50158797b03/part_005.stl', 'relative_path': 'f121301624174b179ca4d50158797b03/part_005.stl', 'source_sha256': 'fbca0a5025076ce581b7bc4d6bdf33e0d31a5760d1038d8cf5249a164d07b628', 'input_faces': 980, 'input_vertices': 699, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10926476120948792, -0.2119203507900238, -0.5000009536743164], [0.0920889750123024, 0.08035174012184143, 0.1825210154056549]]}
GEOMETRY_BASE85 = 'c$}rZ1#}e28};22+$~7Z!FACrwn*b{fyHHj;O-7ha1WlK10*Ckgb*AW2`<axJ}fMYyTh{YJkN7y(%t`j=X~dVIp?1H%cWCYU0qdO)7=A28ze~RtH__+%FQnie<rQ2D5R8%uQI&b;Gw;`b{kT>|G-f;B`xRl$Kwkd|K6x+8=Ep*8B;K@+mNn<3s$rjtkk`H!D9A;-3JUFI=FNHP6Gx9cB8y@=e|R_x$_}CI}hyU{<%=u3Kfdk%M>nVA7}r+{FB^W1?|L_{fDV8*QXz2FFt%@RYUIbnaa6pkKSy|^#(0u`(&LWjk#L3A?JFDV_S{6cK6Lua%cV{>y5e7ub<@aZ-yIl`^vjVxV*I&Ou6fFE6!aDSDMOE8#a*b>t)$)+VA_<I_J-dnd^D)AI@D{7ntg4FBl_vyNafE&;xdIuDlq<?O+d|#kpfb+E{i!#|BeAAUWsS_>^0XxfZ+bIQz_m;l|t^xPWtYa^W4u+;#biwDTY9*O<1SyHDD=$H^#TuADi_?WxtCv)YuW50m`1bEm1CEFs)(dTe{s_IAf8Y0v$OOxrvBCvrPD>vuNSr)3XmpYSkKebiaa53_Gu6=ux!QzbdqzkJwks^_q-hj>2~{*E+lKcyw-+N$|mD0e=*yqC*u`k33<mFrZbG1n{Jll=Vgt;XCnye;QSqf+aPxno^T&eaKdqD<RAZOZ4x`PZS9#$4-ALe5v{uhGWbx%n-(v%39xh^d}w&v34cYq-mlM-7s8R=1kBA6K7qC7_aNdskpeY5xn!O!ZN<YtqgwlA7wHq<Vdj>$`XJTGRGRk8<u@dT)p6xYF!Dz~^&oVN-i*J2y%Gt)TShyKSTS_cQi5!R=l7{m#RNT#2g5xnoR3lqrvR!tHFocs1IXYj@Ui?yOnKw7ug>9XVgC`kJ=a`{k4EZ`*ml`i2nM|N0!<&i2i-b{lg?_3zTppH_`A<>gj$?x@^<k1<#Jwc*?ub!C?^*8_jbe3CMeX?y$6TQYCd+soxE_8L-7-8b{7y<8(NUgqOGP+szs^X5|Sm=|@G^Y*zVU!Qh9=VQYDFy$*6g>oMI2bZJI_mlj`3hp;bP&AjLCP>1$x-gTR_d_>!8FS^tMLCZ@W=9)yeU~5St|t3qOy%UBE93HPUi0?JukB;c8DQF8t1+K*wS8h~w~+t%d@9+yFXMWi3YX(beogW#9l3q<J$JA3@6|XW`S@>qT#m8-ajvxQF8PU^3n*6?e>}rKcWo$n{~@M!u%D?Xc@XBo>3gqn`5`qWuQYTyZ(sZimt!CKbBDBlR+$&JIeEWM-w%>!eZ%FuO8k_1zC0;;o(d6MpH@X~@Nu<>m3+?$Ij-ujZgRW6*(Z6VpPa|>KRH)g?~#1pNU7(OkvF9O^_F~mo`qb_1i5Z_^XSJso|SA#xEy_82b8mM6W6E7a4yH0wzlN0gH~`kS=LKAjq*wUU^8Dwm4dyv9QEkS?Z$e#O8qN&$xD(~%*ORpy87SZyw?HA7sv4R(y@QzO&M3aCGXign2#&#h1=XdiJ~NTbm8)yRj!)zkDs@3IcdVV{`O?ylJ^@b$9s2_?00;B$z%TH>!|WLhI8d-TFIvl<?FFF>!~?^yi2b4V{S_OS9-rqj;p{Tu214f9tZlC)7y;oR2p99dg_m(CEr+f73UeAaIQ8Bmpp0=&&z80EnJSXz*NacPvPsOD=gt1F2_GW@^eGEeO#*+-8JP&^Mx97b#-;gGxy-@sD3dom*d!ynse>1b3Bi00}jY}pK*07Z=bU$UoX}3>A0TGrE4TlxQ6?!J!4faN4>s#OT7E_<YRofe6`0%>2E`}NM5?N)3kl&8Im83T5HU;7ri7OnUnjc_OzMow{J?x&rA+CwL_XGn>oLBjn9j{u8YU5E8jB7qon;^>7Q`!xY$ner<Hg;;mTE1&ez^on`Hc+=Ifc`%R;H=-ZGqPhm-O8MsppPc3b>yBX3`Ki}Z(4f6IQmew6%TUG6{X`}T4kH*S{vkPp{KyZf5ASKmf%;PU6xi!zRPebM9%(hfIeoCZjJT(b*B^7bWrb340&%W(Z2g(BB;o~a2Rm!q_U_v>_x4(D=SUE}&I6{Y_AtJ;!RI=__jo&{vy&s9tEsY&_#YWw%xH|1>(aevTjO0GRnB@eB{=TV<7x&E=3<l%*79k6+UoZtRW!#MxYpW98xdGY2s4=*w1t{1VAr>-OQ$#VL>DX+d(>a*sQ>^Jyun5jNjB)9hrl{_FJAFp<9k2w!K%;#P4$MGi3Ecq*0FDmn;9OsvelJEP<_0$SWeUz>Ltz$osX{Yf#s*RUQer3~QIqy=wH;?MO!L;8kGuCo@bSf8RJiqo;b=DZqm#e{CS(gkcBzdjuJB;UD`TM8S*v`&RO?H~{pwml?x$9cUYR-L*Z!?}RCF<x3_Vbmvo@)BD($4=xuZXXm)k#s3r~eUY+}@jy8)YiT-eRrfj!V*>3$cCv1(N%;jz7N<u+*44K24Oo-!apEy?OB%(|)y(&XVtWyx3TdH_vn2RK7DsDaju!FqQAk_dhn3uf}GPeCjw;`QE%z{t#oXzrDDe^FF;z<$LpdDK?tgZP7N#qy0_gd-DRrP31c_bd<bQOLO~p@;-UZ<@?o=Ja=Wep8k9&<E~sa&b87l`SXKkK5;atg8e2m)yJD}UvH|9vZt8jw@&eTLrZenoOj5?>kT~$<GR${Wt^w3Z*Ct?j{d2YxN6RWikgng@%*^tU*0b=)zg!sA1XVpnsZl-ss7rfuFK+UPj7B%Pv?*t%i?PvZ*FNHZP2sO`1*r4xAX^P`c27?w%~PzQtFX8Z*x)BKX>Fj+Kc`f8gKvc<d*)Uw4M<fU;p>!mj1709Vxl8#55mj=>~<yH!i%nWn5^J)zJ9HwKunnYrTLyG`?}|&8_45a~jDl^OZNZ%vY{c|AiR)n|HsVuO+w4SKiz*U%7hU4>9&PZ#y49wv>HcjA{ONM*X=&+Pk{xy5r5~wwCJ%u2U}me4J}<LQK~M`@?gKdHb^U<htKn`iVD>xhCzfPx^`4?cO5JF%M{OK1rTz9_QMoj&fhdbG^9nY9V{T>DAIcpYNOU+)H>}s@<1zls2{JvqxRv&sl2T&*ofPB=_$Q%Jz<qc_p7Yia+0J4NjZ$L{)gbq))*0sC2_%sm~MsysW+2W6rZomF@Fj-Lf@k9_K;7$>*uAkIZ@ST^V;9Fdqho&g8s$L0+Gz{-4cx`6m&^`s>4+1aZ6BR+`$)o7cK-I$xe#alAA22k-U=E}6!cH-9zXG(W5Lt54)|d^-i3+QF0iT;lf8hdwgr>&u21kIS2Hz;(e#ahdYh9p(P%=1=DB+booIY{)}%zPCQ#Csop8{j++(fcV<en_JpbDW0ZveCNxXTh5oFc4!=5fAHp({-8JyW{a=Cd2>sDb046>$7Ai!p4`%(l~Efy^Uv0CbZ=ZY-rhQnJh^oo-E{Sp+&oT|%K`o6XY)Lu+$%kpx3|m#-rO<|C=n6EIJeA8O1s9xIk(J9-rO=Txes_O|7^J~D6cw9;M_VNdh&l8n&w+&(<;d=^Q||x%(vdWQQG*+*)zwS4=AZgZoZCqbIWzan@3)cjJKQ)C(Pw%Ix4y4I_S+U*FkTdW?f{w<vjajF8_xAM9!`20Z(pO4=D8}OKw>YcysG|z>}{ZZ?2Cg@082DKG}bPbL+ZMOFAM*$~Uizyt#E<<jFgAH?Idgd3ZVVeoyzB#JOd?=glqaJ#TJV?|Jij9V6o{AN|v_{`BSts+#Jf`Q4P<vhMZfmUXZ8HN|A(xc02WwLN_&$J=h6+}duQ+}duQ+}dvSn@owfKX`I$fAHki{@}?i{XrX-Zfbn}-<w<4fu7vb|Gl}T|7!s|r^Yvay}4!ldUMP8_2!oGtHr#O-17NXshn^c=hk`2lUwH{Pi~!;Jh^pVI^#dh*l)e%cyjAJ`E}e(sgL<{z4q?4<g<Kv9(Hvsb%K9hS!5QM8-AYWd8No<$^BmOeQN7{2DM-kUQZ}39P<2c<e^yp{UTUre2tWHZj?O9KTj#f*Igy+N4XCERzbGkU0ia@{R(exxnH5&sV8~gE?kZ?@yS@JuP(XeK8boNh_ByD+A8vVVaS0CT>iY-l3)46{X}j3l5>5+Ub)^|?!)M<U&;12LgYSP@I&5S$^Aw0I~^8Ef9!gZw@)%rejd1!_p8nhKF+>$k>qW5@O@D|Q48K)%O5HEkIAy0dHK$q9~vmn1#;$)c6+fy@}W!QKG>X-T)wh91Gl46%2(Psx;&ppZFx<}6X~+wWDli$<l5X2=?}vfaQS+d#<G3tTGIZFO7n9W<(KWUed%4?KI+Z(e16prdu96@tEHXQTD-kC_x*?4&3V3<Jl~lZ&h2i!Z>IO%D*0>|UpE|$?;qpxXI_>3jXIvoiRjJ8t7)$#x7=s*=GOac0}{);AC-*fVaL6kQjRiM@;$mdS6Vnn+WG1W$u0N&yt(B*p&s^5)>W4Kjo#dPzp>C)$)6^c`_Hi}q@Scy<aw3lKB|7DjO4|ldH#0X>@V%}sfy&5c}ZVYUvkU+QssOj$u0L+HLbto>x#+sXjdTjAGO<R$s<dT;r7pd`?x7T6=t3X>dSS=djDDL`B~=oelJb)gMKD~JV&wIANJ;!`@?EXjZo9^;{LOiyMg4E``F&xavxhgdq{H2{cv?-Bk9LoK5#!#GJW87R?eQ2JoP<!9=~X>jF;h`IJe%1S4MT>&jU(!%{1TYOQv$Jm8~G{gZWl_*If2DGHax1T-O~WdG?iZ{Yh7o>!W|zBzb0e-^KB=f|TQYEP2``Jm0HLZ=L7*l>8>S63OS$l_QDNzsV?BFODqC*KOB;#yr2NRX=lXeeR&Pnkdh=TDOtwK*otu{;){N_oZ8D9A9dc<nmllKP8{<&drs6lGs=B%ID<s-O!3MpXd8c^11T-)HBcPyMIcaGK|-KdWG#=PiI6cr_|s4+(b>*UGh`cry9qLQg$Ne*5@zEpUY)?*Qg1`ey$YSD|t+3Za>d_Zohm|a-Up$K0WiZy6lqV4VUrt!TC8*+GqA?e$Hoo9^@=>MDj0pcs;24+?MOn@KcgopDTSjBY9X;K3|@BQj0t<x#jtkbILu*gM+!<JoBe|F0p)Wv^?k1X3mv$=eJ^fol&RF<@)RAj!15OUiMdUelBi(zNY33klfXAI-jpi2j#eItvJ^%59ap(>=PgGb7#F=KiS^${7%iYUvkUyKCQ|n$!kC3>%VixTWRMB_a(PHH`Eqq<<HN`n;!grg+4G))&u9uNp5-msJxI|t^1Jcsay^`Zpugh!|y$~(zllPP>Qsda;(ocr)rX0o`)*WW=d{(uIkOL&sA$D;^Wb?$oqBr=pXxdyS+I$cm6w>bI1O)2lzNP4wcV)mgl+Jib%;V&wsUBr{sOQ7a8UKsOGcw^55$ZB)2?AR!TjV_6=z&@9mslEcJ=XDDMqeo=0nS@=I=cuI<e&?Vx|F!@28QZaH3`oLs(Ip^a>Bd2X)FXeZaLx?lNxISUjyZp^iIi{w3(+d*=^0!K<Ymgn+nM3C&a`C8tuR_3*|=htbnz4iHi|Jj_|Z;j^nnzZf(_HaG)6|%kcJ%L#}r9P#O%l7_xxSf?ICuDoe`vyuHSvUXBdkfXRNp5*>LED&^&$lDVEk1rnsc5NB%WCpI%Iv8pdAr0LV)*xcn#%k;Zn(TR^}6qV{yEnO={GH(@b>z$pxvBT+r_!{{R+KptXyA%O7U?iuRHMe%K5uepJBC6aeMW-EB6EP=aBV~<^2t%S{}Kdc=tV*<DB=J+egb+P~JOxc7)4OV#n_?=8mHorJqbHeVYG1XSqmY`+MFe@#dEIN%V=;B)7bmqWs-Ja?5)x>dW?$KR?Iyah{vQ*Ap#TK5x59`^fv5kIqQ_L;A>ji|Y$>d#Xde?=t32+k5G6YXZ6c+K^#VzV*GD8l&a&YLWFaFTHMY+?XrvH_E(Jye^+l-LXd26H#|%Jk&41<*Q4#%J!D`d9>HjQhth7QjdJHUi0LRm-#ri_kF(Am@C=VaQ*E8)erLTcR4Tnov=mTgH736&i|fgQjW8_^#8~Cq<<}cE$xPJWKZ8H)|jh3s&VexpOxRQQ?w7V-_}LATrJ(N+|RYHU#0&j*G@`1bmji06-mJ3N1v%mJ?m_d`n*fYxwBpde&5TvzR)^juBS~e@00Dk$?sw4SJTP+ymjwL`*hE^)tEcp?&RDNP?!6cC)Z0qkoRoY?cl%HH)oU2CzkiDl!<n!587WnChuu!f%#?ppWiLl%k-W3c-6W^B;P(m`eDJkvW_iQLh2JcR>u3xGV<PC8h_4Rk6v&)I0LUpJN(j4?jxLEBJ)O(2y=cZtIVs~S-B4Scar*B-XGI$^pfLkw3gdVyPtENDfe9??HrwGgE4niYRdbw534DkFAwyW<66^0+JCyv?X30~C);a($~Zse+F{J?1<Ol+i_R$XM1vq{hnNx4pH>{?`AtbbTk8MEJKoM!EVaCcid@@tQ`#*!jl8${LGH^~-=kAL1<QWx?3U|_&wt!c)q~6Ac+<R;dG$c8SYxhsjgt4kSLfpXtiFtp@-6T6d2`EqeM-Zv(hkY8OZkmfOMfh}Q_8QNN!sVM56|=J=L2$Fi^8OxGp?0&WvTnpKKl~O`?^bgcguNtB>PS0C&#mQAOD`-+a~j%enj#G^<+LPEzhT&_kKz_#hb?(bNkn$vVHdqe7xFMU(Q|QgSnorex=tLbEWn?&Yg>+<o&0+eo{{7j&ht=#_{`MdYC+S*DwAf^FZ(Y{63%Fq_n)JkNLs5eQ}gAclIm9^|oi|Bj^2C4cV{deM{{_UCAx)XR1f*%l*w2yJfszs?6(XeMSq(r+=1qsHF0`Mc>~+%CWrvspaY^x#fLPWtJxO&-78Qrzds3Ug&;{WczQ5X<eku-Yo6Y-A~5XoFzQ}D3$ih_LlclwM%Ctx4hS?Z@4VyC19dlkB+?H^^ZO`q4azI<Y)PKzx(m|^5)-@a&CWBaDyrTD@4Z8>IyOs4^Ad|*cq80T))bDiaD}y?wC}Bb60D5e^-B$Tegp=Eyvq=kjzV`3UF=@ts>W>siD!vT-#Dg#(%HzGEZ(U%DHoBR_VuyH_NzgRZ;TZM~+JWcp&rh-;Jc491mr`%NI&{X9A?2iT9e;S6Yqso20$X?++^x-6glYhwRNQ?;-2C2FmlrZ3DP`*X#b$uM-TDd`KGkd1!H&Cl^eYeDuGv{gPMQ-b$i1Qvb_?WgKpPal)88YqT)0_kM&)eJt-$Yfr+Zor|oO`LlkFSYz&t=_}<-$|vJG&nd|lbdh#mJA>yLMSU&h6p;0YV_0RLm-J`<%6@0$GJmdFl9HbjtKE{zI<RIpnU^|b;@s7*sa(J6rRM&rR?8;ezZut9=DmP&avk^NH5<wGH19IGj_0#WekrHqyNd99qP-|A`QmMIT}VHe=M!~ldCr|fzRG-erhJq!cZB~d<GowLXk+eb@?6$A30ukURj(sC)`7b7_gG`@IPy};`H)tw3!%Tu^K$EZ?~eYG>*r)%{reNIGxdTKB)7gl|L0W6i=LJ7GOmlvSC^xtK4DUSEoX8*FWUGcvi<XW(y#D&P^<Z;<d*mLm8<up{!9H#p9fX#CFgqg67oL%sXa0;l}*f_Kds+W(9dR+-12<~Z*KX%gS!7W&RseFmG(SPL&iID$D9Zm54Q%%{PSBi`P^&y9)u^ieh<QvTfYb4Eywab2=Dfm??HHS>-Qj(*)?Uq*6)1;)sk}j?K0nH&bZE)D?f6|eEVmy4aVGYzkq!1NWDhptM2useZpKaA2n~x^R1e$4d?dsRXErG=@ezmRs9sthptj#G9Ly={=eT_=^@)=+}ZEM$o16OSH6#xtFT;u)eG`{kOpI9zw>U%^`+=3nJ0>CQck*x(*IYNmd~v{*Gf4(C&~K%d(pkdTsx=9dbG$2IbPo#lKbS9>x8|ze117}SlV+;PFbfFNG02sx*>U&71D2Wev@(V<$;v*?hn)Y&6B&vFO@u99{D`d=bIc?(x)<S{GCD8U73=}I&0xb&K>%8{#h?mlHJv>ip&d(55yRAXOnmGy|ChTS??UJA<qNute5)zQ%kO^Ga7O3IP#aw@1L5*8gtz@(zNc<{o70V<K%Ouns{|&e7R@-)UtGz{F1-aqh=MECx3L4^2<4;9)*|4{Jf~A)YJNXE9C$4eJf9H{k|3Q|M|WZ^8fk1m1n=!?_0TgOFQR1CjBhKbeYd*jgrr=!O11Jw~R97nN!GlNmp3L^}q9_{4O(PT{^a*+`r#=PU@Lc<{xL1FEY=Zd@uVAd@1YO^5NTzxgL~F&exfoGCytlBJFUnxqLtFW`kH`uBY`geg0K*q?7v>ZAVDI+7Qa?L*;R8$<Ixe{(pWQ_kaC#1DSWr+~e`?UB7wqZ+B$fRoze4Z(Evj?!xCaz07z1{H3+-#JTf&BAL&FGs!wFL4VFwTu=3nZR9%m&tRz!+DA{=Th9BFRZ{-WR5EYmPayZ9&#jX@$vru)??0t|-#n51TE184$*tcj^yZfD6?$^(_X<6^^?QY$-1@yj<@qN$UR+O|>Jb@77rx7L_rP<K&-i7XF?XftC++i~o$RlTBF~Ldh01u;_VD;}RZ1jzfoxJv*n9b0V^7Yx-lnC@tD_#s{qO}T<@?Qkjkuj1(_-cOkWUJ8uB>S<>$#(O*BNuQXFJZ-YA@w;R@-7y{x5lD`$HZ1yxX^z;oP}=iPW>)EdJcBC;Cm^V;gl?&ew#9oyOdGB2wmu|JKR)O*~%mDsOq5>g_9UGv<zEd*u7V+ak6bbG7<1&b2%Pw-|H%YauBo{Tb8tT38BvzdPEry{4=`%;h{kVcM_WCoAXrrin|9xsoG-zhA6x4PS1`hxC>29oz3OG?nvU#zE<yC03aBTdI-d+j=fCmGktr+~+;Bh~E!(oW=KyQ&yAvMVo_$R5j#k&!lo)NW8d?DNp-MzW-kNlV;4dGxB|HMVnpNm^%lzlkXQ-Ju$&l&V@WOKX>oT?-4rlEtGkE(^y%DU#PIjm^(uY$@Qh(`|ZYD?OIUA>EyX#rg9pVljjSOCwCfi#pN%bFH&7xY0T|&&dYNR*QQ;@T(h5*e}CX%oh7FI=E=+L<4{}0nD+ZPm;8GI8N(Kuwtq5$`-#2LR#W+^?=b0ai<_CschB4MJ@lPtP4(9{WRm_c<S$eGwFc$*{Avlln%YOd=P&uyP*eM;&+)zagS9tRZEE^gB+^zc-+f?lMIj|qe3kB<4gZ7$h4jbc@&6MNz5M@w{Sy)u%9s3q{U;=T*c5tKSh-;n5#NN{z$D^ZHW9H8{=Pie2V4Q(9b5t213n7e13Vhu2|OC?aH}Z15WEw(5V#<`Be)<qKfFCSKiCd$1Ga;+!2`hAz)?04@g;aSFp2m%{C6;k_)mB)Fo}34{Gm;lM7#!m61)Z+YNKZk;`iVu!S}#V;TOSA!O!5A!Oy_&;5WeUz@Ona!Jolj;J3hEz+WNa+i>a!xA8M^0`!dv-~`}`@E+ib;GXc&;GW<ya0hq{xU-?JbcTqF`AFT!zrc(7#MPhpGrW*b-0>2>gBSFPYailg@cce;?MeI;Zug06f8u-aY(8=4i`WT|!nsx5T-~j<@OI#~;6Qj^a3FXDd@OhbcpQ8(cpP{Nd@gtjcn*9acn)|rd=YpycpiK)cpf+yB3|OwM7RcD4A#IC;ETW$z~kWy!Q;Ur;d8+w!NcK`!Nb8_;A6pEz;)n#!F9lu;O)Sbz=h$}!G*yYA>vYS6<i8j!mV`h+;A0~8(b3J7F-fs6&?t#3a$$u0j>+~03QeL0PYH(0`3a#4W9$<4ekY>4ekZ*1D^-(10Dho1`h!bg^1_Fmw@Mkm-@u@m8B4IkXx<bE#MQuEx^s;8n`*Q8GHh`8MrBYJh&;i27DyA2Dl1*IJgS9IJ^tEI5-Eq4mbxm6}%ES75KePyfBzVd>x(<Od=j{6A{mZmjaWB7s5+`NyPJQaea}Pe7a4TL_7;34svT4d<=X#cntVFoXR?npNSvCbAw65|G`UwNyKT9RRyO7XMxuRX8{+0cK{av{{rs{{smkb-WyyRTn63?Tn6k9?*sM+{|X-h{uNvnJ``LQTn-{02A>Ze23`PP3SIyXfd_#@z>|F9#>OOwxV2k3;o0G>z}dlB;Vr;f!G7@OU_WqXcr$Qja3*+Da3*kicnxrRa7uU;a7ysMHu2(M67d~)4ls#07M==BB0dbK@pBj=-UYu7-UaRh9}n&W?gSAJhtC8L2Ty`81Wy9bhR+Aj$5@&T5l?}LC&Pollfk16V{bG>9Ozavct`j!a7S==_!w|^@OJol@OJP)_+#)v@KN}G;G^IRa2lT%@H6pUcor~;_%*x$m_+;&{tK8yoDf-Qa6)h*co}daaALSWI59X0{8w-ia8h_#a8htGcsXz~@I;%4cn*9Rm_)o7z5q-jUI7mQlZaQrCxJ=CA@J5<67f7++}I{25l?md1e^FrIOQMlGw}y_b})(fEj%ljMEnNs2PP4}f@cPkh+o1pfl0)F!PA3D#8=@d!6f1na2o$7AYvVU2dsnl!ehaE!JFZS!JEMm@Lk{ta65P(a652QcqedEaBYY<06rWX0PYQ+1nvzU3!e=pp8_5W?hg@<f=>pI0*{1`29E^yg$IKBf?L?)=8hH+aW%K9z-z#pfop&p!8?K*f!o5ngWH1F!?%OigEzttf;WP9!;gY@gAc(kfDeI>!S8~PfzQETgU^Al!GD6Uf$zg<ez}jIiCyqSU=r~Icw#V#_-}X;Fp2mdcv3Kl_z652m_$4dPIJvTh`1g^To*nETo>E`z8Ks9+!($B+!)*(z6#tN+!`JNZVhe)p9gLQ{vAFQ{5!abEpBdV0ueXFu{6Z-HAL<?-U(<A@{hK-_W6kRBmZEFYtIj8Z}PXcxb}aG^F#i|7I(hh;Czz5vc;X>S2+LVFKu!C;U)SD`Co?qLwpW?)fU&^h>yWf*y8#p@gcZwi|fzCyWx9nas8ioBYd+hZoCk$hez1r#uss0cspC%cqDEFZ)%Ghzr;1*wQX_Zowy1_TooPwt_rRW?+vaFZV4X?Chrg4=GG~<wnD^bAmY?M;wgND$$tZ<23LlNo47UCz5N2Wmcf^Umw}_<`@qrQ7w~W37vMZT;zfLfNyOFQwZPTDwc#znwZS#vO~6f1XX5UPqI7esExZkwyfL^fxCumD8(s@M(yhU64Tp#a!MlP7fgSJ`U<bGvygs-YxDLD~xDNO?cqQ;};0o}{;0oZ1@Y>+os6X*{cRL?<>k<42n0!C@5%?@bd;q=yOuiI+02~ex&wy)S^7`Nz;5HC(0*F|Fi2qeY#41EQ0<M8I>~91_91Ib!hHn6G!11hxh$A85E$}1YBWSNJ5b+L(I0hpA10qiDBmNzn&qv%BPPs4q5tu}r#z#c_34ebUd=~Bg2_ilX5pRNrgTvA8n;_yv5OF_v8*m$(kA4tw7Kr#CMMV5q5fT3lSHKF+;olJPBZ&ARMEn&Zu8iNK^IaL|eFV5NxEn+~4IT^*#(A9v5ify=SHdH~kvOj_A>y?V@jCbp@D7~sbr5kFM7#$gz5@RP{0I8N75q$`0V2-p6W3RWTe;hzy<1%%;y{SF2fPEAyd$^=xHm*R0Nx8sJ_I}fJOUyf3m*d}p9dZbo(~cK2@zj}h>t?VvmxS9@G;;q*xx9KxGzN93Em6b3&+z5B5n;4{|@f}?tu3C9U=~Zh?~M&fg8eG!drn`;e51&h&w~XeIVj~@IY`N&P_jvxIaWZ5Z)Wy8|P*qL_8EC9t|G>9)WW+8X^vYh!?@<gXiO%ErN)zLByVMO6(cG#DBvtf-mA6d&WDlXMP~|%p1g;AmVZG+2GkY_v0YqVGwaocwcZ|oco>-aXW~(IlMKvHO_r=h`13%+yEW`4#2r@01?-Ni0dkGeT8_Sdt482s}{T_c&JVOt`58wc!B$OCb_i`J{i0a91I^1{?+|Ex!o!S5&r@a7lw%QK*ZT0;>-|nI*2$GM4SvFP6QDrg@{u^#AzYoOb~H4h}aGh7lMe3LBu5?Vt<IZ0z_O1BCZJk6<o%xoNkqXh>JqR1tH>G5OG$BI3q-y1|m)Y5hsC&6GFs^A>!l^acYRz7b5n9h;u;11t8)g5OHycxHLpu4kG>yA}$Xv13u;ML(y&>hlmeD#Csv)T@djWh&TcwUI!7chKQF##Gw%JGKhE;M7$OvUJns(hKP4U#Css(LlE&Xi1;K#d=4VM01=;up8}t7YlmA$AmaTH@otDX3L@SB5r;#>Yars45OD}Zyci;03K6e>h@B8|7(^Ti5pRcxV<6&v5U~ys$3n!XA>y+T@fr9DFujLU&8;eKsqpIXYGCpjV1KvDx>d%lU*YB8Wx?d-!SsqwNw<D+s|36hyd;>sG`O*Qoz&2+Ms78L*Mm0%lh+3ic59$pgWMVb?*|_UChrfP<<<<hX1X;UJ{3L#Og;^~!L10lHo6rFUk{G}lZS)XxwXcvFt^sio$xha^3~v#ZY_6fm0K&|%iznw<e}gv?l$`9)_aJ!y-nO<6DARNfrtmgdw~ao2f=%Q2Z4vcdxD36yTUtzyMjAF#2*y#Pl_=4D=^j5hPsgF1v|jK;AO#OQ4bI2!_WCp4-fm`=bqrs@K31A8@Io6>kIrp@E7oRx8Az-+O41P&)}cn^fvKtU=neD_zy6NI0O7U_&fGROd`&Q`V;%W-+@W*4DCn$68;WM{s#OK`~o6=4*vrFg8Dp%{{a8MaXp8B27g9dJco#%!QX<PfuBOePoTFr=Wo%DAEBS<2S3r4HYh#Le|ofIUMN4#e}1%GS$IA$?dz^vx8ZZZx52aE)4}8uz_Y+p;1j`9z|-Iwcp7*rd<J+bcqV)<nEW1iCio8g75Fyl@dre_6+Q*L6}$vK4ZH-r4L%jT4SWec6Fd|9B);#~Ww#zc#5dswz&F9y;Tyr%!B^e-%dJ~(xgg>z@EhPO;Dhk1;HxO-AhgkNTpMxR8?kRsI~+he9Y9?@?RFV$c^Sv%=>x=`K1uB9tHjUX50tq6O#B>v6MPfL{2YE2d=<y@9DWOY3+>_=JH(!`N&FJ-0>6UafxEzWz?a}xz?Z<=;0M76(RSPi+}Dg9Zf${xH@Ow#R<v7t;8EZ`;C=Az;C<k|@U7sz;N9@e;N9R|@J--d;GOUt;6m=Y7I7;pM4TO744fUD4PF$S4eSRm4E6(Oh8F~924{rl2WJFlfae8g0H=fJ2B!n3f#(9J0jGlJ0H*?{hUWyQ2B(GF!D+$i;d#L6!M^Z(U|(=1cmZ%Ga29wWa3QpH7Kk`0M4TL+9h@AT5}pm55}X3=2TlP_2G0ym22KLc2u=b{49@^g3{C`32TlY|2u}k}2=;-e0{eg!cxol?53voNR`K4tW=;T44{qAP=Hr{-|LeazjQd0PvK7;RfN1?q^K0(L->mH}%lp!M(*}vC4crId!w)6i(w!sa{{Z#T#X|'

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

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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/29e480b958df44a2ac3a4ed12b7ee1a0/part_003.stl', 'relative_path': '29e480b958df44a2ac3a4ed12b7ee1a0/part_003.stl', 'source_sha256': '415c02a9922129070a2cd3edfda29f887b904fbfbd3579a8505e2ad59a4fc916', 'input_faces': 835, 'input_vertices': 537, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.04571608453989029, -0.0747910737991333, 0.008328026160597801], [0.16069935262203217, 0.31029370427131653, 0.2025488317012787]]}
GEOMETRY_BASE85 = 'c$}r22Xswa`|ei=qD1e6o#@@siL&()y$fM0iE^Svjk=EB1<~6MAxiWTQJ3C@aFl2pN9W)uNB8%>&*S^J<K8juxYswH@%;9ix#yZ|uG!Z<UsJ!t?imgI^ER5LU$x_EDZ>z@GBO&2149P(>>4<rc%OcuZbn*-%fBB!r*W%BP20H{gN@+@x&;pC8d9K=tw80V3I&SV3Iz2H85q*JPp7^i-2x?Er*rUt!0+(^Jv#Rb{QkLM+0x~U+DaEHY8z?$fBcu?dlBr}dPE)g?pC&dbJf1P^YhEy;<i+FjoTM2IH8}%q}eNOHOq_iUZH2@v+I)EPW}7xd#g45t>ee#vwiru7|pNi(MU~ytLbU^Y;-)jMcnb&j`)GZ$Mkcfr`t6Dtglu`+!o#Eg63Phu$ISFAWGv_k;+;gmwo>M&9B`g#DlkMc^vI-?iV*-4b`}-|NHY=p8lzKXnEoqA^q2MhxGHnDf=|PO`9V${-DW0Eyv=iv6}z*P^ZREhU#@4d;4wB?@eo|aeKXGahm=}ug!YhA<@e<efnL8^}4Tm==~ZMLY8Uzxj8Mp-r`YOZ${-AOEtbMvzEvFvy1-S?*DO#)<YvV)Wg1FdS6DlQwubG=^1A<eay|Zn!eGlc@j74)YSVi7PQ)~9&kEb(_fr&RLkFa$2!d~#Q}|*2PW%%I+9(`{GE|ikUqYl)`QW>2lv%3mBwA|&cy5YAMDldIaB1EqxrlVqV2;L*I3JM1SUqjW8PgFpEh)l#y=mLrT29)K=ZM$+^OZXa{o15(}(QSdU3sarr$HiIHpM4`EN^2Z$3Jx_h*(bp>eZuI&B~3@g!(JvodSkexmzHji-!Ut?}1aCu{k))YAI2zbLQwWmGc8Xg<{|YWpxwrO<Y3)_Xfz<GvZRUL5|-HtFA2Rve}IUps~8bu@|Ar<G>SAdSCYjP`K1zdjdZ<BlNBr)x6J*Oj@&R*k<Y<gf8b!?fJS?De?5y`hh`pV7hEFKlV8Ra)MJW4-ix|8&v&H6CQs@;Lu#)nC2OxQlw-Q>*Yi7xvM(Wgmm*Q7qFseE)rj=9g=#wjW0~f6d=@_`p!q_hGcxw)^$D*k2YHuJIC6^|K?y4dvfDceIvoYd*cM>&PAbyE8n?AL_YNYTP+#x;`(*h`tlFJacbpzp#eH>2)pV@+q2b@^5&)_s`+E+{`{zKi6!kpKT}0A^%P95kJ{P>(g<_q4i*8xiLfIZu#|k_K&OdevOuGX6olBv$Z`K$3s_YKF{64H2vs4dOzl!r+VLZ-wNTHZ^`=@H&W(UuYT%)#*I8FHtOe!kMz0O=N_7?K5PxfjSQo;y_p%yFHrYcqUAO#-`8^5!#x)2=au8ougsTvUDuV48n?>4)aP#WwP`tR#S1UebfpjKb2S48YI&@oUl(h-LSs?B#p}?H<}_ZSpC^CT@!S~GQ_JJ3n9-@<_YTr=(;N~KrGJm=r*Y@kc(k9BxAZ#pbB~;;udX`Y*)M)ZIS05!pd7ih-mG_idLP!svKqJ6%{!v`t+cfKM$>v4cQtH>{4b5y=VM)nia`F))~FBo9rc;C-U`h>CPK#n>&fhBjkjy5aeL*G+HPGJBQ$@@>Z);9{A9GZ+QYOTxgr)tYQAUZ>3zDAt<$*W7N>Dnw*A`Pti|W>+-v94_Gl#Aq5anO=o|V$-y#|}r|rY|b?u6l*EXUB(ibbJ^=s71s^xcFibgzn0NQ257PRNbo6wKzkI-?$w&0|e!wh(c^!e6BqTl93JFi$A<JQ)t7{^+k*ZZ{QU&8f1WkUb?oJQ}<7Hrr1G_!_jIm{Dir^aU7zhkdc$35#$OP{B!{w~yecvsY;|626xZXRoYzAv-JL#+qr?u#0?y4KYB-O;@^p6|BzNWXRq`dh!`n%;bzALC8#92m!IU%|ZdwUD~~#s~}jEI_YgtAzgQy4hL#of*_g^EEro)b?%oUqt&&oCWPJ^tQ&${fp6$O6)^@@9@|5V!XJDc9dil$}`uY_ia_orSqW6tG3p+m1v*FjjpY=91j0#n%>sy4AQqRul>mWV;&h5hx!}R4ehy2H0C4cN95yiO8cLgG#KrteP(?QwuI{#CzJT=_-$2Qr*U)WQ_P#8E77h7Tt)n^*_ao5bwfFl`(pk%6~0`{v!@c;Z4LwN%WtFBhi&u$e2z<|?wGy`{le8n`;+<J6Mrw9O2;Q_=z9HZAJ!Y`Pq=BnaK21>0R4CX{yzEw)^BSzqrILDMZa&FO2>28>pN)QDaRuJ!RW8H4SuMH>30!-^AE<kESvHDG-xkI{(5ut`>AK+J}aidbC~@N>x5mI(Z75~;dyR<q3y~FS%P-(Z7Slgec{*3;Ccm5vmcK_dmcCwpXdFJ`pbuT!TH-$^rv;N@b{p8OZC256v2A+%NNAoZ<(f_*Y?IbFd-%S&5TJpKiI-vY5C3Hy*2LWH$vO9#rm|~`e@uXDmCuw^eD97qRljJ-|`6Szk>PJpxy%zUyugtTi<TlUhKKLpdVz<tL@Y3Qw8(hrXh$|e6G*Sd>Xw6{bDNec~&V7?Y$1x$qP3io-+EB#zPZpdgtXAh=&Gh{W!`E)OPC}^al6)`SuufuM6n6-rkshJW}dBY)_UE^W@}`h&K+Or=Rzo(ED{}D24I<c`032+Z!c8{*iSx?i%+_>&<r95B;h{edO~T^M+aaH<aUCBjmGmxQ<Kamc5woI(9|++}SZ6G&qFzGz{x4Grte!1Fq|=86%O8ue;`Bi;u<nHeIB~ou8U%KXN?$i2cH%TUc*?I;rD{^IACO&7E&?-K!sTo#k@dfbsXR7uEsgu^uu97REe2wIJ5%FAI%T4?c+bd`EGO+hRP>PL5U7_G62xhV*+!=(@&vE*1Liq1G5Ljt$iL*YWp!l>cULr0<hN*AYhYZdmV>9ES7{R-iouB|>=$E=N3TUyPFl&<-7)&LVy-E!tZ|G{&ug=dn)oevWZ+OsL+U^ZIREH{}<M3*PxrzcU{qeN%63&-N0Dv9H|q9P#z9b$)bgI<Don)qH{ZaAYL<QBz;+`^p-4evv1%{N|OB+MccYiLs70-&WOpYJSE1HZc{_zxKfTp+c~>b9=FTNZ%t?*UOI9Pu8IS7Dqg|t+sRfNzAAJiGRGU>qq;p`)F6W%OU@_ceEdwAuqH&JN8%Ff%?X{We;*<d^+6)`7~cYOTYK#6xvg(ZW_0bKc@Z8ni-D$_@;4)FYT=BOxtTO#O;fa&!j~o^mC63=>IL3BK_u7*uUopz`mj1cEq#y)%rK8XT>~S;Q;c<JI+*Z^$+^#;1ei+l0MiEuStvk@=pTNhnHQZzH9}a(_c?f510CBKQfj#z<lTP7V#5}4x^rP=ye_C-y<JubNd7GdH71KGruLme6?k}K5s|%c^DtIrNF+~v95=vJB#(NZFerl=l7I+%-TbAo;2dT5jW11l(;oujJ8Kx_7+%QX3CEBc1Z{7Gqw%W_pGCSe=5fF0Rs>}^X(7G$6m7*>SxOclyga>wqxhR{MxQupEn@=m%q`UeFy9FwI%F9{75?V$2EiW{vB`QHEzE@SNpH6_X^b8zMClLu9iBU+eUlidBwYskF}<Y-dD{*=%<N3A^!5*V2RuQiqY}Uwlk6LmyAn=vClTUV_n}0`%?4na6I3f$5H+Yg^<2S#r~TAqOm&e+O8HuyyWwt8oyFh$93aWRqSt@eZ@NS^aOow_Lg?+)4CPZ@zdV^cbqfas;+VCTOMuC=A`pj=fAF{aeGx0`{>XsIM48?hjJF_i*uaf>$m(Iw~EGNzjGx6#-Bad9~zH5XY2POI-?!;ZG-&te#ZHaD?P@6Je?4)luGk)#0<vxR-g;wb;EGpva2Na!JT{He5*-T9hY2T@t9Am4n}z{XT|uo>^bJ&6GJp^o3QUZt~(jy*o2YDe<03t9IY3j{kNNr@>h<XE%j`adx`aMpD^U_l?LgnnVP?2*COPT<Cw;sb&uj)ZrcXrvw8b?ZMQwKuKp3XhI*h~9Vvr)2-}17FOTc~-slvMejR%d@ih~MYd#y#VE>Zp9P(+_Q=g-&YAo8%yf~y^H5}{3>wjVXYj6eW_q@S=JSG+PRexSZ`5U&ve&@syZRgHiACb?Q6?3)SJ}83ueRm?P|B5Bxxts~o@!2)k1N#mCPuK^Zwd-?qwMeINdy^~}_fi%|d%uLZakVne&(_{p@k=~1llFIK)VE1`y+;`luXkV1feiNwi++yVcOS+%;fmyV?h~^iy(6)XOZNDy7zc9KL^;1iV_mp*qL$MU&=Bdj@7I26)Qr&jb5!z2eB6t1+VAS6)^iqDqCi}?TrkdEClo>bzZr!5*L^{MaQDSJv+fw=v-jOp&Btvr)~OxFBc8Rnwi8>9t=Ru>nuUDkPsco0)WUk`>U^Z1_67S9o?kgLM<6~hE6x$qm(g{!8MPDf2ha8V&sAh0#*@9VD1V8zm@lS1!+x*dL8LEvPw&?}@H*`0xS4Gf)(!0j;5;GEN#qlBPuDHhRGc?Dx8FiOn?FvHd>n7;j??=sdJpX<%QS5dw&sOUZzW$Ly)9XomVdZi#}A|LN5n(i7HU5I&treFAu-xf$-Y{jj&&P!UuE3%Lj2ZHJs&b}-oQBjzKq7LAiIw9X4qG>f6ody-<jE0-L-Lujwi0K^$@T84C}$|{umD%3`73?K4INhaVqBZNn;ToTuaZn%`Nq?UtKZ*`K&#F>$mKHb;66;h_BnK<Au|lfpz9Eu4hZt)cQ1rOw)W!_j$<Qa}}P`gHbqtXtM(OHeZDEjsB<6?>_HF{zVq+^<1R_^}g)+ah_$^jgDH*e-B~3_&d&@%zfE0&X#V8^YTxxajrS=rOq#AqX(E@CcH)b%xxW49bF!4+;!Cr>zzYhYqTFtX{Ym}_1qotm#=Y7Tw@CM0}-h(-zI*m*K-D5LcbZ69p}rJi(<cepd-fZy7>^V{Rh@_8?NF!<3fI{Q>y$OkMh33b95HbxcyKO%r6gyVSdS63+0&`j`N7O%dnoPhINy%YxHKVAKxbEFD)A(e#}$bp_%Otu79gB%5w<&2B+^wT<>)=q|Y&Hqo!ZK59`p`tr6e*WP`TbO@(xwZ1(MjddTUGbJ{Q0ac()TJJOeLjQv<SydU@xH}i&L9ak_C>-a<c5RY1e=e;U5&K(<uAfEwmab7geOY6<nVglk#p01bjxGHVJdU)&<lqcmXtcOGIqMh!Zi}ZeZw0?{a0T}<^FGKu-#}<h@GYnhtOMG5my#L`jgKPdul(Tg__H7ZvF%SBzLi$!toVTsS`L6xoTEvf5)c0V9|BD^J#LLyz=VH_xk9PQHG~#a$YB}xKR!993?>1e>d1u!?Xm?LGA)er)@1vZXtK$8`x2=f#48ghY#-dnPEsH_?d;y21_w>X$bkHH(SHcLrA9Hgt<Ujl<(pT=VN}v1myV?$oq{k7DJ%Dr5=>yT8XPiJgdV=>U#;j&|zF~+PwE}S--*GD57p*#tc&`$=FEBr!z`7tI4*7&9)BTaFL~D#M-nWqcgCF{7hXkAtT6Yn*M`}H|HuF7F2JEYhH2-S5bq2h`xlMt85N~#Qtv=t;O)>u-dxv^RJQ(Bm{j+*sR^TV3H(gqOSLZTVXGFSVJPy04^=z)6i}RS`NfGb-Sf9J?QE9AWcO^r-VO+F6--mdA;W(QD@foLdU15bq?E57?ZHB&&vb8*k_j-3d5jWp8(tIl2JMeSdG`is&DqpO&e@Ac{#672>KTn*C@#K&6EKe7G4{1w3U*l%VjEG;VukTyz6CCJwwk(J{3|(j1+y8;}czrMA|9LvrQGr2-Kk`QU%WGF^`>7kwbq@ADhOLj@uMvUwa{r0jBWvsRLbmMuId0v2k9OH$GS>6y3nKl}>sp^ybSBL6`LV7sN^jQZZasT}@x#3$;^!~-({>VE;t=|46~qVn>%8x*wjBMmST)3Z9zp-jk$&4R@yxq4?%Ia&$nkqU)I(ki=S}TiWB+aXA${TX`aafH$`k9`daV)PT|?WmnP)D>&wzG_bNsRUroy^waTmmowm^IC@CN4|n*$Ml+DOMW=Z%GEKb5*;y`S7i=RxP*^H@I~>4Ee|=IHZv^xvWNV0G<{_^#`CpP6XLo?qhgD`TDA%Z~o_cOS$JPplsv*2cPJXg|aQdScv+>#h0QXM|$BOl)eucGeiFpKYVZA^i|*oz`<}7v}XfQxIQV0Ou@4E@(ckQqvG$vQ5{Mu8wbU4)kdr;unkSb!|O!qFs$&fag-C9mdrz)zP2RE<*a*ljm!FUMUsxbKG%nCf;8kH*l`7Xfe`%n23GK!%j$7(TVu`k-86Z1^tHp)p#Y}W5?nB)fitqujf(h7x#4iXLERAT)nss^>ZiSB<kxj`fHIbNIx3yTU>{S={R8XI)u2#hq2lYr$*{?ah*Sjc&}x8PVRiW9_z%u=THyJm*D(2W)kMHjaS$&oc+<CM`L|<D1p!Y(k87p_cd6jEq}!45~|P3elQ=#pK92@+6rI5`_OkSeu+EJ-_Ukw)Qv|wob>_uq<6=A);|kkJ?Za``sg@O=N;Rp`51pbcwpaiVm{9IhSbM=x4;wWhgQ_*Xcg#;ali+^Low3+uKm>6>t5_H@kh(?`->mHH`tIC@#vL0UYYaPpq(_txMI}1uIoTs&R$x7wx`(;kISa(5Jxlr*q`IBgf^&$TK!PpQ*vQ^-TwvajY8w`dzEG0$cOW?y)@Rnt}6M_jy@&Dd#*YAknU#Ty}z`d%KcH#BT67{^uq5=yoO>NPKx$ud~Trc)eRqS)N_t9ct22~w4R^XD;GgJ&)V?drMeEZ&#xN$bKJU6R@bHGiQTBT==!)X?}l90U&s2+uQB4+U*bG?`#No(&J694Pm3bDpE92fK>K(Zg!_%yfqpk50sEKXJy0IYL-+NLXMXrS#a;Z4#43(+S}O|Usr6+B($D#Z{+^@@%D+Dh_nR^q-gh+e!uk5jD8#Q=IxblsG0vKIHY1;=TSK)y6fkt1YkRj1_mwRM=Xe({;dc{{j^MdxI*8wmoH&kio^;sXn2j55)%Np+`^Uv+5Z@e&eR4F`yRJ$XaNTXb+OEt__0g_k?xCFZ{jk1WfN|$X+*Laa@2S6{f11_rBmX+dw7t28-bVeleuTJ%-}4xp#~tw>aowm@DCe<RSa;=1hW$<C9LytCI-ortNr~q(Vv(MA*l&#0`f)x_hj{+wI<GmJ&OttjGNHcLhhkm6!wdVrR^Eu8uaEPr&g)VBQ3Y_F^UHO=@0yn${l8xY<bSfS&ijtDI6pMg;Judd>@?>65+!hddF^-)Q^gPGjZKTA9uL<-`WDai_hmLG_EA6L=JB!ESFBlw`KwwRq<8nw^A7v<y?Vb!&j8d<rV41cgRoC?j&vaXmYljSwFP5c^`CgY1=uIYA45CZ(-YUt(E#TK>++*MKZGFtKnwf0oA37g5+CHk``{8`XrJQ-V*amr5BuEbmC)W63_*QP{!{nq<{As_=CX-=#^l>3`5WVcQ4hvMmcJav&qLQS4sV}<xO4qXEzg<{Xiqo85x-Ir?<2iqQ17)O;agkdJag$-)X(!Ml;_MjJy$oqBC(G0+{AO-=6arNYkMD`eYV204#z$&wkP)U%Z?!4!5zPQco2;7Gbj%6up@f@WsjKjOWgK&Gx}-lzZjQ>$D=%-gLOP~HN<;HW7SpU(>YF`qdnc3gFnaZGZN!>EO$5H`6aoIb0+_$IA=R~4fR~}Ci2O(P0ztynJmoXTMfLAx{dd<whnvHUmB!hJW%V$xw;0<p=xBtxN_0Ze(Fef81=9-C-%>S!}0z-WfJ87M{cCA5{P-H<4ioSN5zr<h0}P?Wsk)8J(2sB0blUElBdGDB3)Ue_b7?=;`=+8f0vZQz9eUJoqz4&QCO#StB&hlZKUP2lFq^Nt=ARhY}*dy?7tuPJKaQlK__izW|LBAZ=LYm?ALE-eOeW^Bi~*#P|oCK(9Saq!uqYla+K3{P{&D^;fd$ie+9~!wWq1=HoODgFJ<0?_`5O~H==#;dxjkcaGibC*)Kn1|1s_s%9Hdm=E1S~aZY{cA+B5S1Kux3&c}YT2iA{ffPwXBjxA_EIXw`skQL9xc#Lt+Cnx4}_x$)Boc}eH^I~qCW7W=s{^Iit`z=3|*9xzS_x`K1V!z)V?}3e}FR%~IunPOxuxhyOyL;GQB{V<ubKE+X1;4Ys&;jE{gZ9jSG3L!}cu(UjJ`(xFoW;J#>n_I0nkKG$sjsfjZD*3={IcVGl)uPrJeLCz$Y;w+#Fv%TbgqdVFg_n!jr=F$_a?SJ4*Y&3VJ-5X%k!Bf;Rk<-`z7f3<IH&;<Kek2$ltv;en0Ra5zZ^pT}Aricd#F?Ujpsv@B2u<?IYUTD4f4r9q~Q;vu1c7l*EbtU%(UdfBN>izq9`8hx#n$jr8N)wLV?Pa$`RFtq9_SdgFVOOQL=QeDQhCDg2%~I4#oUuY-8ED){~B+&q|fZ1wT?kCpKr{|?%Rm9Y`}j~C`cD?>2aZMEij{<q>Zy%mAqds@?5As;iN#_g%gqQ9)g_sq91c@A9+>q)=iC{NoUt$)M)1=4LY5g&0`&zYTG^R=92!O6HzlKhzOJ*Hya@{sYCm`9y=QlY$Cry#$CGk8CF;wJXdX_q4X=s=v?pQ?lM{2PVz^H!i8hTwN|#^tq0pYn}9cO#$~KDXb1a@KR#b0=%+Zk%6U+JShb&UlXX4&r=l;ZA(-DaIqCC4M*RIJ_6vEng7x_4Q<UE>{mA-O*y0mxqo*J+!%j^nshO&f0So<Hd(3NdN4yK3^jx_REgWACZ1?dyJ1&E8;nw$$<OzFN5>n5&t5dFB{GsCt+N(4E#RFe2ciTU^(6c&Ag2ES&q;1ih+IL$w++vnlI89Pp7|6vo-h!^|`GY;@cAAoZ@38^n(aI2V>zooPR#thH>CGob%ZOW03B_G0Y3krz4(V!)L=l{-ckfzN4F>Jv`}xaj$(m(uXcZKfj(IpTpYVK9W?z^`E01+iuOq_3xy^{k=_u-=~~kiug*jd%Is(ygxsB1Nk&aj&b2g4C-%p6FfKHK#UWvyeQ9r?uf@=AM2|8Rr|NqWB}s!ix@{<h2r-DqgElF8uPKM=u4Ex;f`_f0oH5Az2zFW^-7I+ZOotc?orx)t^DZ_Z{G*=lPenkeZz<Jh;PEW*mlbA_|I|srv_-hE1Myo$yt!TQ4rRxgK{Ijx+l`_t$=nHcShsR*Zq+G#(1n#=dH*5_F_EZ9`i9zPT!9AvCXF;UbZy)bFSwY?@!M{JaZ`4ALEOitk(3G|0<?cu6*+&3mAqdxslNb>ipAx5+gzR_rw49|4B^GGXGcqNlb;(W&eNwlNh_(_aWrF@=?MCDdA%D7G(eL^8T*&^y1{={Cj(P3$pk;a(l9q623wS$5Fy3=u^nz<H;w;2Pxql^but7zT_R`b(HX8`tRh~^j`Ge$>Qb7y~uSa;nMWN<fim?l&~KqT!UViES{fSgItvou1L>A&co+akrJ*%3H#Cuk_+;A_)@~vDB*JS;^g9duH`7<B9w4;dKR*{CpkMg6(#IW2`8n5t5d=aDd9HsEaWV_UK_eUIg-Ab?oSqPPZoEQ#jlW8lW$PM|5C!QDdA`III{Q&@-y;%O85@_AX$6|`40IyB^*y*M;2d9jwhd_g!j4qx4rJ8gs0Pck*AY~Qo;fBI%M(E<R5KUcp`l?y(w9|9eFf)FeMy9_alqfAcv3#Qo;l1RmtKN$pgs!Dd9o%N@Q_g@*r|3B|MT|jVxY{Jd!+|67EAULKe?X?n4fwgqzV*k;UD~&B#?KVH+j<*?@!%#*&i7tCPjcki`p;4e}=g68?vtjVzv$EE2wNK*Cq)iOJ$04X{Y~6eYZe{+cZQh`fiqgA(3Izeg5NAa5kErG!`0|0IjYlUI{hQo_sW=g8ux$;-)$DB=0^6J+sY<oV<Ul<-peS+aN>c`11bB|M7~K1>NGbAx-hfyJAXlaYH<!qe!%WbuCFY2>+-@KX8^viLCaQgRd}yn#N7EN+rFkhfF9vGlQI@d@Nu@_tJAFnuyvJdAvpe4G+KLtjJ|Uqe1azC;OMqwge(TjXnG7bSd;euON3ihPg!kP?1E37@5e=g_B;#S4+e%aFyZljo2ZP{PaU4awqd$Uo*b;mh;{dL&tVHCg-yS^Qse0{I;!Y$Sq&-4a2<-}v{}WbtR@Z{#nO@CW*RviKeH2l5+A_$mE5Sv;Qnl>8SZe2adPEWVF?i+qj}K12zxrB5fXC5O|8lEnkaKjyq}rVsxqPvJe3@Mii%viNB7X7UnBcqV-?Sv-V1lRTdiUPd2C79T)fMqWV)ucG%Siw`2NBCn@}H_=1M;v>nM$XhAlUG(8(@jm2T<SmqNG(C_k-i#bgUP%crq*oz}+sF&aGbrIPlyC-0_?7{eIrSFjR)cZzPmF)!TzHETwkY9U^!w!doC|kR!doceDEcY#Db9sal<;Cocn*CBc?ajhIh62pN_Z-LEqN{H!l{(-cuM#W`bzRj&V_$a!X_m=ioS@vh;!j6N_Ye%Jd(bEynu7zNJ@A#B^*j$LSDi-GL#bjof7Us2~VShkI)a3#bxe1!q38~DdA4^-emD<<WA&ql<+M2T(bC5@+@)$CA^IuMHb&c-bOw^2_K_xCyU3DkC9JP!WZcK$>N8}7s!87!dL0X$>L|oSIM_2;k)!pWbtd{yX41|@N>G0EPjvtocxv&eouc$7Jov1PyR>=f1-q6P{J4KXUXDo$l?pg;>*cD=FW?h@GE)(S^OPYT;|1B^skJ6Wtm>lUyy5lPgdc(eCZ{~;`zzG<T8|SVR|mIczSYSavn-JHzn*z3A<CmsVL!$^jzdzyk161*oP7>L@z-u!TTvh374jXD^tSNDB&jbn&eLOHuRe0nyi;LlyEajxGud6xeV*2E+t%*5-vy2L(aqcDn|*Iq=bu6!r3X|<aAH6C+jyk<!=0E>7<;P5>7%1r>3VOr((UQri3$7!rpWrvJdOsn-VTS374XmCYR>(C`AcZq=aiw!gVO&hV*LWYJ5%&DPey~xc5)bRrs3Jh4g!RTC#WnvPk%Y0SSMhmnDnWB8!BRP{Jwb^~vIm$SKI_DdF7oCS>u(<lN+vlyE6ZxGp7Jff8;&3Ad&<AvfXmT2sOuDd8Y`eR6%?PY@;ClM?PuFH0`V`s_{#ccFw^(bJN}6OmhyD^tQ*>CX(X_;IpG_!}ksm>x|QpGkg9K1vC1q7NqzXM5R13D2X1C(%2R#oLf4kq1%2!SrTi@w((-a%W1oJ-sSfyd1ebxg{msfL@X;UX0v;T#pjAQ^Ex);Vks*Wbx$WEaaq=ut85m7Ef&a_n)vEC7gm1PDu%;p(i1WrzWQ%XP|_==$Xml-efOwUP`zqy#QIf6uBt5EG1ltUXd(bgItMRof7t=Hztd>CHs+EQ^FnT4zhS3az}D^O1Lk5Fj;&Yxi5JrB|Mfsn=Bqd9!n0Rgq`%QWbu7uCwV(1e2{*HEdG>ykbIXCenkntr-WZn!Vf6nOY|$`E4<z%N_amdypz6_yp{K}lM-G}39q2fCeLPlt)PU%DdCCq!Q{bw9uq0yfs}9$x`Qm<mfV9JKnb^?HzteMAdA-_i#H^<Ah)B01L^)`@!n+d;bifd<Un!=B|L>5O%^{+o<feKgk$N?$l@|y$I`DczL36wevK^toV<a&n-V@r|3DW1LOw~pObP!*m-+ZFdJ3{g_=y1t|4UC#PS1H)SS0+_fP|Ct?<L74IUgsdgfmgX=_uh`lyF{pU2<K{-+3uvFG@HgC7gp2_MtZ*H{iVPLka&z3D=}|BzNSzUXv1TNeOqR_ayh^yxy4-?n((e=v~NNIIlY>;SQAW7<y%LWzOqA&P;^=poDwSWxnr0e@qq$*LH)1Gt-Zf#W#^f!ftMm@Js%E9$9=6`6c-}CA^nDh%6pV-b-Fb3D2c>CX2Tx&m~Wwgon{vlEoX4hmreJ!aeEr$l`W#PjWX(_{Z6Wa4kx>IK3cQJPWxvIVUBYj-He(ZjjTFJt+B?jP6DjPeD#bPD=@ArGzt4!rAC4$>M3q*~mF4VH-UIS=@_kBj=-pi_r6u#fy@Qkbk3u%hSt}#Ve7^ldDj|wdvK#;(p}X<VKWmD|&0Pct>(8atBJdE4@2eyf3*cxfdnek3N(vK9<~%JcJS+Lk}a1JIQ0nGbrI@^zCHvgXCr8ZItjK`dza4EAk=o9ZL8iCH#gGen)>#7Jos0NB)}<c2UANDB%nA2W0U}<O}2jlyD4vKUsVyIflHM5?(`JPZnQ6UPE3*32&f>lf@?*|D8{T7gEBL=>y5)J;;;E11RAjdH`9x1zEfuSv-&|9zqtMLJlJT$bSm2DIQ4{k0t+DHwep_n4DwDc~<@JpPPPH^Y6;=edCepyV6m@o|JHMx(8W2F*!Lo2_^iu8~lMASbQV-Z}M(RxF{u@lM*gL3CB>vkLVA`4|u&t{4AV^5>7_<AbaqBl2O7bDd9Bq4CIX8mHxXj)6<gE^6!}`;VhJJR(b|<2G(y@N;nfGoSN=Q_GJC0ri4>a!b#~#$VpiDN%>j$GbMbUzMH(8^?sfb?nVjUG$2i5K*DF}ImtQsoP<Tf7Y#`GHoYxbd=gnC{MLYk(@?^DDdB%8;hU83QF>c)TbAc2J%${^_HmRFen|<tvkghR5pL?|mMCN5|I`2N^?(1#J96Wf{}b&0^_#!`H1OwdW-e{~_lJT_{gUXMpXmGlWHItqb|A+809lgMHv'

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

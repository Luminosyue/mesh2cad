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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/844fc9a82f46421c9f10804bd8055212/part_010.stl', 'relative_path': '844fc9a82f46421c9f10804bd8055212/part_010.stl', 'source_sha256': 'c222d17623f4ff0448daa636d7933e3d5c384bbb54e2f27a383b216507883301', 'input_faces': 1200, 'input_vertices': 675, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1611166000366211, -0.16163022816181183, -0.053180545568466187], [-0.1313687264919281, -0.05414854735136032, 0.1717357486486435]]}
GEOMETRY_BASE85 = 'c$}r33Al|_8~2~RiAbSDB5h=z$&d`2Q06%^TZX92LMYojXCBJ5m4ql2=Qs!1By*9W(wp8xgXTe#((pZNuitvw>)y|MUElS6y4Lmot^a+Wwbx$vde*atL+x5-%U;0Ie~LTzlx`3{($H~K%i|Pq#taxadT_r1qbd&_{zSmZm+;jeqf6R!Zr!e1z!~FADARwysD2~M)D4xXH?U5bilH(Chm9OPvhUD7!$$TWp!{Zi9~(8m^+yfrJA8oKFI%g2&5EHK<tm1r4E;a;$*txvZr#Csu7u_c$yDkTxaF;eNq+3wfP^2Zn&0+|f0V8?+UMAt$$q5!2MOPqcqHM6m#)!%`w`aoo=<*c<sqG4VyS;VzMQA=<vcxK%+nkHe?6|4ztgQ%!jFI3X-`7;{(3Okcit(mE8%Z@?||~7kGDwp;mUpYCdQlh`&)i~*05`qADY-RF@AXc)q}~tv$L!9xSr4BMm|4nJ+8a!(h}nxYL)Pv%Z+{KBYiU;<IDLNU(Uz)DeGhM#XO~N*3I~l=W_baUp}vJ(P9Zd+HKA5#5mU%+m*<lRYd2v{Wjq{kzt$nCHdht-}>f9OMjvLU!Jq_jqm&vw)}W0?T1h2u*UKHhBYleeC~oCzwQZpKKRazo9)LvtNrMz@6#Ll`0>YES>s0zAJ_R0{$Pz`{P5zRHYNM9L-_MASmPT%KDD<seyCKsp6Bn`x9s!rV~5XM<45k&ez@KlYkcE7=LXs9)15jt&ufiud}rNRYkX68XVWQreelDBAGOAhm7L)_f8)o+{Ig2T@SVT$<@_U)NBFNle#-hsNBFNlzFhyvs6M{?$M|yp#76e<-9N^c`zLFD2jBf~e7XNa_;UYyzS#e<-`o0Lk6BmSTGwNAb0K~G)~c{4Ip6r<n%bB7;Tucq{F@Kk`S{V73t4_NkM`qLuB12g@uL@;+w*xezdjE~7TB`S$B(x@w#j<jN64Ra+#28b(M7|p@nd7J=yjOf#TwuESp(-;<2(4#-!@z0XN}Q*c=`fs{7{Xf+Fv`to<DxHL_cf%NOkSUzg%IBZ~SPP4fgtTokk1IwZ;$O$2N7e#`mt@N(=4v$B%yck~O|}9f|pe&2=Z{?_Eb?{>GQ{ciwHG*IBH8)~Oc0>mSCK>u-Fy{;>-ccKhug<IDY%^%41E{}^BHpYXkf5`IYTfBcx-|8=#Wvj6er{*OGB*Sdba`9GQ0zJB`@)cKdYzv1UQ!8X2r^mwg=AB{9kx5mMbZ~xWG509^?{aG#2{d{NEkM{US&L&>xgukDf=I1*lc4b(PJNDRKy`N`W`C;S#{+g8^oicu}-}8!J|ERC;wCbnllYOo=|E!kUcW!*ue!izW?zOHL{1Co(y_osutg9cl(w94}aqy#`bjY;k-=ezC|LTXGetx)gOFO?_Nc*2<x9f!;uTa}sAE(PL`f+RJP51Mi|5UW{;}g^Lxms#fnx7y2I%cnbg{}I$UAHC8&v!;HvhxFD^f=3>?ez2G<I}C@8y+%Bk27)6PG5i77Arq=rMmVDcD3f?82{QQ_I!?3(vQ2~;WR%#Jo&7hZ(jG_)NiMs??i_9`qBS})BOB!w|15vG2@r~GQ-c0R=eiw$BUlG^z)tIdCT|C4f%ZW<?{`7&b`}rJ&iBc)A{gdreD3X&f|-E#hM<@^xY5maz8|7KAq{e-@^DQ`|a3_Ouzjc!I%3v^h3E!zw5>L@_LEoz9ZA`dNjVg9^-%J&h)$9WBBrV&uW-W=Zo_sjxWy>=kYHy5-QFs<ID5PdHDT=FV92c%kwbO;B>-Ix$jhs`}*;dBlY8o^E_sJah}JX8l>kV?-%&;evx$|pMG3%KQeyG{pfNw{kY<OXZ)1=UDNLq@0X+UdG)zu`A+TpzV~0_%loXCFYdEmzPN8n->ic-j=1j_U*31Tal|<+eRJJ;zBu>1#}(&{@#S^xjU%pW<I8<+e7VoP@x?yz#uxj<^F`gIFV|nzH~vjt-`5q!m#-6yFJC7ZU*4CcZ_XLx%loYK&AI2z^YRqyeVjKwzMOw_`M881IrWc~Z~Uy=KHZe;$Cqh8-v0w@{>Be)?PsssO<lCl`v~cq_YvN@;hXmn-uz8I?<2f<iu<_q&3(-q=ZTVfoTHbl`FQ@X*IrEaBjdF1bn0)-CyXE7`@S`w(BjYZ{d#-orF}krINuxA_|Zk=vp>DZ#W(xYdtCGR%!Io3`1qlw8|?AL>ka8U6Y8Y<`pdIf>n2~Hc=>5ve4lRwUq0XX&Mv;s*ZA`JhIl_E>tfzF$+{R{)<wSl@$$v%A8$VQe4gpMKk?=MG``%Qq1O&-UtC|tcM99rSL9Xg%j?Vd^7?Z6W+wcQxZcAN?aS+3zK-(p#p@_<p5k?p^yPUaUx!Fvo`>>vMf|fI`o54aV~?M2&b|19htmE0aOUGyzIX2R9h2_oJ4N2K^PQ%9tm{Jh=DNTS-|&mxpU3iB`62vpv+`EHcYU=Fru+Hf_&rvB{Kcle;~QU&AG-f)rr-QMU(Vm`6R|$Vm+KQNvMAGU{f#fzKU8a)wGYG2A8#i5JO19|>u>x<pTj#|O;7e?`0<`|to-l`yLJAnZPR`IKHu2mHyNtO+4E1DH9mf{Q@so;zfm5&uXewa=I6&d53%yS`fl4}<$LF6ze!ep<hp9R{l*XDr;Hywndvuw<IDMHt)HCfw?3XP)+dywO{U-a8(*$}ba4Z#zRrN}^!kX`OU9S4my9o8FBxCHUXs2!e~d3*FG=5=Z=Nq+KS<x)7d&6wPmM3{kH(kx9d8_Q-|@x~=d-tN;(YejO`Oltm+K?XXX(rJPkG-r<11a?kMG{==bO)|q8rzxC;R4es^}xDt^Ckam-RZoQPs+KjNkEw3@g9ReC>~WFU`s~{xbut{OIl?y6%~4()|2rm$i1j`MkxvZ#DBbzIoq@ADdfzx9|A)a(pN6_DtXT8(+-dIodhXcYTa6*2jGQAlKjX#rj7EU2k8%y+8B6e({|JJ$(I?>l#1hy2g)oZKB`jc3x)XNATmjH`<RY&jI0k`y4+uB8MJlW??HoYW&$Hto)R7L-^ixXVz!v2EBiN*kR?z@Wb<_+2hM|M)=-2V4m0dvU>bnW3BwG7=F&T?D6HfB>jgUvV8Bn+I&94*Ei>wsqe-DyZz=9GQOBk%DHFeBhNkKf3PysZ#^UUay?VdNi$D*PMZ0gtCi`uA3R^|hm><w_;SBRy8oKtyPxq>_Om>Pg)gs{(5{QtIqZ!u&S$6be(lT8qwrHck23l4^C*)qKaUc=_j!vMM}8iKpYnN>8ApB|C4BGmBIC=?qs-&V&!g~DK94fv$j_tjQ$CNvPx(B`j4wZrGULn7ql_;<j}pFIfBAV-wD2CCe`#DixxU5^{rZrvpVhrf!gtm_k(TVo@x!AIWLV?xYOMXKGt&Hg=jokRez?iE`}F!;+hNTIKVB)k+Zt!j@q{0K`PQA*IQUM#(pG-_seO8X-to@s);Rd#pN8zQ@?U>J=ihV1%8%iP-*0Z^N1KhczbC~{`CiqGQ@*3Vj-IcdZjEF7A%ENTlHa$Q@#XieW*z?dT3=rmM_B70!VgzHX4gx8-zt3X^K*P>a&ztXJGs-(55N3arZo=t<>=Nt)_R7`{kngZz1H)R--nuf`F*H)UZZO3{2yvs<2(4_P!4PSc!#JyH);>E#*g90&!4g9FTZ~jzW05T8ONM6tB=0s=R0G5v3&17TcpWOKi~V_(5#RAo=*7jUw-rT!>gL@_4P-OwEUFs*UWt6_iM)gc~7R_dPeZ&dWOzkm+4zCd|9uQ@3TxD<@Z^}|L$sr-+qhY%l#Iw_G5<MevaYG{hacBlXsqo@0-l?dZ2xV-}RVvzxGqENBMn|@a6R$EBaO9oDYlh#Ph{@@;~nj&LLml`Ddy2#d(<ZxAq-*9v*p8=Zo_;g71j)Ha2I3{ykoCo=5TH583CrldWCC4~zRnR#5v<aleQ++L`!$R7c#8V)*g-;(qkkT<x#1?{^`5N8ImXheoIQuG^HBmLD##>p)_B@%z2fH^1L&eEIvm#+Sd}Ykc|py~a=ZJ#90-{5@^_l;6`fk1KvpSo-GoguQX(?{%B`$lvQ0zW00S#uvYD>^-jhed7+j^m^6^>d#+uvHtk6(>wIO_`3OyWIt;BQdf3c`6bWjc>QzRt$h6O*@644{GOxtC+1VD{MKYYV*ClW>`(Tya*s~DZizhc{3dIB{BZeSto%6VcIdYuFIvynod0tgTk8<3cQmn{Au)c)_+tF<)17uC=2O$2f7X2MJ7WGJXT_@tU#w5oKg$z-{EWRm@%vtUCGj|N{f#fyKe~U!%gNVKyg+^ZyjpFy>T7)Gvu@g7dExbBKkHNN$DioEC)tn0s``(!<91&^`cjrYpRShQ;paQkZ?eV@=Q^SNk#(*75Pp1Jz|P;<N00w`j_uZb@MFtvk0<-_*;n<?O<HZ`$MB<z*X^^`;jPPhycTIzejGo3c)FGEH25&FZ?nGtZL^hMA3slQzxB8y7HEIX(wD4t#t&btW95hEO-cBXb01mxj`7cww({f0F6ir}YTk|3IQY?e&mOSGd1PV2&${*J7p-{?*1nUixRoE9HdT+muGuDQeEfJMkCkt($JnBs8~pr8;~g9Q{H&jDu;yc~-`EX34*2=b)#1K=c*75tpLHNZU)N&(5&W2#fAqpu?Thts@Uw#U`ozEJsmGV=j~@~1AF5I(ac;!U+VzcB)_z#jH`Kpa!Vii46YqyF_D}5itk)C1*q>qixZIz+ha}FWXmfl2NASa9|Hsxf*XP(%_VpFPcf|GOTzGPOLdEqP`$+o{as4`tnkLS@=m`6Kh=;Ww7Ux4W{mRRFKiKC_7(Y7AK7ZoNa{Hd2&Zn<!^Yf#B+^qc-_W2pc4~z3N-Xr6s<Z;3um-0QIjW5q<<ID5e`0_mT#u4YC=Zo{o`0~8+d~u$5k1Ng-FJD~mUcR^<y?k-Kc=_Ub@zzc3XD?suXYcun{pO7$_M7o#eZBETeZBdM`o_nP+3#0h<EPwz@l)=<_$l{0GmgC98DHLy@Kf$b#+UaC^SJVUVe;j9Zt~@MYx3oJX!7NGXx2@hS0-PcSLXT3^TdoJ&lCKV>(`7guU|8NS>IQB`qvjfrM~zn^~F!AuNg<y*Z8u&_$l=@zO1i#Tv=a}FY9aaWqnP)tgp$J^)>4z>ud65ea-Wg^)=(j`r@b5*NiXgYvwQO+o+Px7w<!*Z{CL*U%n4DzI-2QeEB}q%NOq-rElIpdgJ8CpYXGS?^?cmKj@7k-w(cC%J=z7-+SMUpYpyNKjnS5@#Xtsd^vyPr@Wsv<B0jkPnPswPyCd>*PP>{#OLht{l4+#`+eif_xqkN-oJa}i}&x+H}Bu0OHcdH$M|BL`1Vu2^EAGkr{{}#8sC~vJL_KoXg{~u>UbSD)or=lbsyL_>7M{lrut*l|DOODeE0v=KLJp!dey4`fByzR?nObzndP>{=p1-4yab&KFM*fR6wgC{322@N|4LI_)X`eR(X8|q_$Sx@*=_3IBT!B84d@kEHO0Bm?_t#xUyptVtEM<7`Yo)Q;vBBt=4kzfzVa2%3~F70ehaIncqRHBteWCy(C=Z@6hDhzfmKty8vPkoP4O!9Cs;MbvxB-R{*k8mcGgg>o#LC(8)=HKLvzEqS<~xiinF1);B0UZy&ew20W>EZfE_f4^Y0(U*`0saJv&Wt9=GL33!%5ch2XCPT2(#1PO8(_^cBx=+d_01Iul+7uR&M9Yv6V0N_ZU{L!W_T@Ot!Fcs=|ax*C2CUW=}RS5eEgG{wtliWkvlb6qM`^`1pv@eee`g&nP`#)Xsif#Rud{ugd+dQdmTU(pm7bhN4?tRS^enhz}i=Ywx@TVC{5v;cf7{3YY5alhno)I7eVuXvi<o<`@RQ{nmW0(3gO0A5I&PMwvi=QD%;SAl=`hGMmkzT&wSN_w7(hq&z#w>3o@!;ccX4{ZuROspY#AKZ`Fy=X&N`L*5F2fmkn54;*^ZMX}uDrgN@`4!yO5w4QdFXOhhaD}9PNw>9x%Ov&hbld%K$)tV>x3z%pOzM|*TN}6p{SJ8L(bDjP#44lZ;qJt$qm|*_#A>0{Vdd9#+e2`zq<#ap4TS3^^&3;efq1H)-K~2dplhh~5$YKX=-8v=456ONSM~cFew2Ftj@J);82+95{R;P^|07-xv=96v_4@|yLH`T9j%XM760x>uNB9!;`xtIZ|3kd{(U$N9VlB}7;S1F7BHV)hWxNh(8~AHt52795ABc5FAB2A))*I~(|3dw)!oBJLg*Om=2v)WGi~9bBr}z%)cxOO!fPOK&AetR6N=((T7@p$WiK!YE#Z!D+K*xS1=XdH^FrZ^UlJhI|RKBWTfq>>8spriB?R`P)8|s-apktTF`GR`h6wtAc$+<*5^8|G4LvlW*p2}DCyD^~oL+Y6~puLO4E>O?>0Uf(c&PD2ZOF+lICg(EsyfvU>Kale^^(++7v0upffqE)m)vs_s^Dor1NI-jk5xYt~RqcvUzaqpH*Kk`kYFLdLE3Qtg7<wmMl~_@<7+jgy?PyWBGIgv7-%h_gUP1IWxIA?%3l~i4tNN9O3(&s{FCTg{T!Pq5Xg)YZEDw4UT%6dAXdbvEvApPwa4BN>(Y$aOVz;3A;c~=oMQ?#C5G#b<3Rj?xmEc13tKbzu3&Yij-GLT?d$_F|HS9*7;_k$%qcz~J#Hymz;RlITMytXPQol}cW%?cP%A*zGcErk}<>5BON~2}rR>bZ?OT(?GUkmsy`VZiR&=T+i)UP=lqTdp)Bw8G9O{^4J5^hcX+QOyix5q1omVrAGtALh+J5s;Sa0U8Z@T#Dd;4ajz8(f9{Q`Bz?+%2iE>Ng4Qk<?f9n*euD>Z|&Vg}Wy8RsBZ657Hlw*8%MW52t=Z;0{TBRlmV-JNg6gTA^*=0o1QA+$yQB>emZyk<?f9i@*;g^;P})!_AZWs(ypumPvh8zsKO#NqtqnVQ|}|zN+6yxIO(bc%9LX@EGbh9`2mf??w&B<C(syUzDbJDmn?C3QtBSz?0!8-Sz}J7M%b;PHYr979K%tI64Y`l-Lk-IQ%fN!RQcpF!g(wrnn#47w!l5aa&Kc7upx@O)P@;f*&H*AC15Ri48*g!-J^bK$_x5+%^;)hCT+5CN>fs29F~)1|12Hqka?NF-iTWsNqCB)xY0uO{rm1;)<IQn~Y9{n-F^voeVc7_5^Bb9wzoU`UKp7*a-A-xUSpkQLB2?QgIz({m_TuTEzOG{ouQa^+Zi=YZB{?_JnH_dkF0f-$QI5`Vf3Cu}9E>aD8G!QB&K7#73h-;YP&9p`+pZh)qPt!A*%p(TVU4Zp%fja*?MvH?d~u{csMqT~AG}r)G+;IXV_5r!joR(Xj^PgsI`Dj*iu%evjfmO8pw3SNPcv9Q`wO`Pq8Z^F2q$>X1{HdY*RqtfOnCv=((c<LFpTa_**X@4I}?(KS(8oBDj>=-9pF+(Ui7cXX^iIrmbZKO7xvNKSp~a~-ipXhZ6glh}P|BltBp=VeE)z0zFN;T1>6a+7ldwNk#S$BT}xQxp6q)G0Um3P1b2qjPicGuKnMRgR8bLvv8K<&KVBL9fA!h<%D)foBu@0R0r6PV7DO1Ncc|XQ^c^YFmr?y+>?1`~*L98a)e7Bz6Wp4NoI>j@s8|FVv>qXNXONXYn)dqvzm-#6CgahZj=!W$-6SeO2#g;qU1`ho@@(ES}<x#MHic4lgHuF80EGT&FqFTyQS(6mMt$s6Fz!qwD@EP1Sod{0jXS@SaCsgx3&Tg+33jAhsM`1ur1B2we^@px!g#Mf9iQO-E<LQ>p6&czRO*NoqTedX2|7-Z)sro_5;|YBGbGDPBr!8M+W&P3&288N7-0+zxM~pW(JWtmPioTJcU|o6%R{mx#T9Zid$pTZ6s;uOzktT?5Z2wg6oLPbM}KT>y_IHWi%-k0Le!oeB>lHV&NtFLB#E)@B}Sr+6)~)#y@qH_tO2&Y-`O=b27ZybWCkZ-dvn?HP0>x(=R8Y(BaYo<wXiIv<|I^L!khoYYs(a|Aq={&2UAaocEkWKuuswx?K!C~NUFJcBmH(R*$dY|bI2<IySbIMl5DFy=D?9?BesGLND7Bhm5jc*Yz_o5Gx@FsCtS6pr$I#_)WiJSX$q=D2M!x&)mE$B3;(m%wRm+v>I*=oVP*fxV922O01lG!s_33*G~pGfe4g&cEl{c61lKi^thcQ@jb?0xR7BZ-O_{6q~bI>1uQXyc%AMZh_arF?1`O#+)+Y9rWLI+ex1HN#cr65!;RKh2J5Tj_!s}5Zi{P!^eoNN4LR8h&_XvYwHlPx#%<SL1L58xv=upb#efnL_dx<0(~5QgV<1X1iX*faMbMa{lrG2!(rvCefcIln*LjObI_;Y!^9S&W-lKl7DE@q$BAu4WAJh6_cpwh{z<${G!0(i-h-C~bPbiBq@K$II(CYjcd6&nfR4RG&ME4-IG|%E$a#l)E)3|{F>+2&&!+=Ac7&W`)N@`y#}1KmgnG^i=-5GW4pGlp0UbL)&Oz!qBcNk(at=_>X#pL3gPb_^oF34zedN4BJ!b}VY(F{ssORi}j=f3Fe(E_lpkr^5^CtD2AJDPG<h(^a7X)<dC^?6z=c0g)9Vh1~^;{CrvA4-NPCZramQcSX#1(&_UYAnKv(#Ggxqyx>M_0h_5?hKchmR9mj4p-WBDN4+49AH*jV^?D6Pt%V4eum22b~AMLTnZ~2Y!jz40IO!BC%=c40sE%>F6~0WnweY>F^F>v(cIG4(gZ*&!)c*Z$3H~K1gf<Iv+kr9go2a=%2z{f-Zv35?h8Yf!}xAd1`f@TAssKbvgr|qkq_KC#lIvYW5Z_PW&*uAKeY_hcnQfa0dLU+qR*vpgZAh)MGRJN>X3dV<Y?${Y`jV&==t?)MFD(@m9BOM|Yqv!@G!OqC4PB>amNa_zkxmLJy+*;CF}}Ll45IiJd}^!KbO&d+;gx2i$g)wLHpND^4etf$oQ2AoePn0k0>v4K-^YbK7dxU^Q!`cmuKRs9Cc#V!P1o@LpnXpu6A?-FAfMdW5x5{4uf9=sWQ1ZhMotzsYk`{5-K2&~$hmvGwQ+uzD`fB-LH<Msy9l5jJ~lGe5f-e?4stkFyS5g+2qXf>)xe;g#^SXbgT9UW;yk*TT=a?KLzF-2m?)wiiu<PY^p2_;+9KMUTKo$Wi<eKl34a1kQ5XCAWQwehz;MUq(NHFT<aq|Ajw;FQWf}FTxk7@7vV)0DKg^0AC>gC{3|Ba}=LM{|l=#OPx_?(39{<a?YTiz-Qq1(a+)c;q&MvSY4Cq%zO_$51%K;T)#>`MlZpaSYNaEKc)^J<14;CsMj=iQ1hpOfBR}pa|JbDW{q<OwRe%&XRPscK^?n5&PCQTTTsW|Cg%d{9SG{!o8-Jref}Z#I;uRye-V2geI33=Y#sVM{5!E#=sNf}Vk^;A@Ks{ZqATG)h^<ARh5sb>9J&_%o7iipxwh0V_Nmw&a$bXjK^;3mj`9>|59-)Q<eZ>hIf6QtMb1amQq?X8^~*tAabuSoP{Rh)SaD<O*bvT5{~o-YXfC)0vFp&Ba3x~d(Cc93tNN9Lv(Ybwr)pRZPw}0^R1HhvDJ~q;v1{b~MLll`>e%n(T%(?OgF5ybIloiSn}a%bm7L$G=WRh9`-7aT)U#Mn$NnVe59)bWP{;lz=TGWcHmG9``Zx6~OC2l14*lwQ+0h_ehgc3YJKTWS^=J<GF}DqMTNIs=#6##Sot(sv(pNeui3ihH`eYJ6Oke4QBpyIt=@UuZkG|5eN!*vd(#Mmy4}GPhlDHRrr6b@TZtLl`Vd(HA?oD6m$Rv)?S2{Y0AEK{xOcM8}uXJ1z52UYjJUqy4kGO3j`cx7>M*lHtqPVNuy5n`HPKLYD??#;rccI^fIvMUvzcY0*+>w4q>SVY*{r1$!a9jFqsgvQ>^jlLW!!7Bzq)vvL({E1A4Bt<G7<KG{_JVtn(*u0~et^0fZb82Vbv4|Iek<x~xDEX_)YWi1`t7Kz;STgWP-DZL=uf2XgV2HSKyn7555h_xN#d^byHaz-_qwf7P@kzv8^Yz?Rwby<NTrqFlEg}(<={Jr-HDch3lS@f-U;U?b_-e<F6g#=L4D>ay%{d<whD}0fyY)Ha@*~0D}fe;tGcbU+bW}F;9A7)Mk~X0-4=FRJ(}Vs=zVY#xS8APyRD|%YBQf|%&9zF1+5L&Ccg@;CTm&=Hutw0)T9Rfy=Z+{X;b)KxDnb6ZpJ(t(e9(J4dKRU7;X$VK<mN{;5yWxSW<m%qBb|f=DwGg+UCX2Po3_dhQ;9`Xd$==d@GtCz7@U^y$QY%z5&e#-vH-93&MHe0zth`lomw`!UcJbMbW$9qHqbcEUfmG+J9xx5^xD}%AghDGH_+II$RmP8?6J^Vg2t8{<}wOq4nU#?k)WeNB{nMQ}{lb;)XQE_tF&CrYWvLQ(T3nxB^Xa8JgmfG{tw)6qleWE=^Nho~F1mO>uRa;#xGtb!mzl&=jlZ`k31WxvdErh6fXCgf@YdU*By5;70WO;@yMRhm~K`ZN1=o=y$`bhSr2T6RU()gOy*-ZSCPo^jqVVLd(I*FYdPHaH*tzF}F2?izoF%ZhHVOM!yx_U1$hyN31M*7u<<hMYJre{Hkv23Rg_(-|e=Za8>#dygKOJu=4A<tv_5RsUN0>{qa;kn|gmm4gVpoSp5Yg6&p;>W7P9cVgt~@)blrDebE8%&%}D6ec|tjbwhi>UlHq!c7s1B)*kH)XAx_Swue6=)*NjOpC{G~Z4Up3*aK)Y_`k$jp%1{H5o?FGg1;oz32g^|OROu}3I3M){iJeR27(2${jdK8^1px7?;knV{}5UJr2W?>lYcTt*!lM_QMPM&UE=SR1>OJD7fS*4?Z5MX0Fq+zod'

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

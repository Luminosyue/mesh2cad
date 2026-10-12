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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/245af7dde0cd4add9f7e11db3bbbccba/part_004.stl', 'relative_path': '245af7dde0cd4add9f7e11db3bbbccba/part_004.stl', 'source_sha256': '241ae190d3bc5cdf077bc5479c6089bfba6b21c233c451e0d54165ec90d688dc', 'input_faces': 700, 'input_vertices': 420, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.31793519854545593, -0.4143713116645813, -0.41288459300994873], [0.07777296006679535, 0.16377437114715576, 0.4879724979400635]]}
GEOMETRY_BASE85 = 'c$}r22Xqz1zsEOJ=^#x+;8LW84${j7BnqK~A{YYUQbKP6(iB)Jp@Y&vflCzxsZvweBs76gLPy1m4HZ#A#Xn+s+4+4o&fb@I&O7gM&YbV(elnSzot>R6H;0Jutl5ef@~^CMxA#vw0+kHIE_sb2#`u^q<A(H)8CzrI=t&_)LFMg#PA={EN{5KZ5M#XYMx_BUWBZS()Ywz0>A;4Ss(C6695rU#n7$+Xj2bf_#`a--hmVa(_hSe59UYVYxpKWawW@jQR;lKh;`u-R%WZchZ{(F@c3*ByzF?=>xoT_+&09scpHn~o{#NWUz5Y|reXQyixU*XK){@W@>gQLltkb>uPqQTD=U#QyH^1x~r~GFr?)IA|9Z)~-)l&7x*X>p116_Z+Xs54}wO98>pDoIJ&m?Yg`Eh0Usa$y6?Kj-nqqpOEuZQ%f_*T`9(RjlV-3Qvesm8}wvX7;EZ|nzZe5}uFrRd(6R7%Dt#W>+=e^FC44uLNJ9C!IFebhKuBWnh=6Q{<(YShcMU2{okwO^iB*QtK`zw9o)#9`O?INnMero6Sb+h*N+bBOni?CNUA^W`&Ye~mLs=Vj_Q7PWM5OzkK0WNw;yOmBbbqtnV4k6xjBXP%fT<=@TJH(h_iwO?8LC1uu*QTvCu%(iO`nszX={%82${@2N}KeO?1eDL@fr!MZ*$Jra|9tUsEbIH1Q#=*B?-f`V$oG(4fpU}OtzrppL{mp3qx2976>JB-7ON7kSy;UMrj?41PbB}4>Tep^)pT_)+@9N(Cx~A%ncT6w8`u(P~v#jtXHNGPf)c!i&TQgbCm%!LfE?==mlHR`K4YORF-XGu0Cd&KoN;}@v6gAF{_Z-@#_AAiLv~+Ji6>~t}-@w_%;-6el`)fXqPSL&b`~JOpKQrq4M()w~%PcJ3yScU+AK&x_Cv@+OkJaIp+aIWwlxh8h=i>DKWcW6H4(R*kc%$gvz4|zK@;tn(>W`}-^Q6V%i>m*HzZSpo=t)(-z)rUh+nAzz>$9`2cC0b`FR1N)lc>BgxwM*}-s*o}boo)ulXdS+h<CMP7P)gt)o&js^{*8>rH)(fKQ8FrdO9pc_x_d#rGCL5WxtO9cuDtG+tJ5$@0q<x>YJ-&fBO|nbNL}DDZ00k<}2?leM#+?^;zGGy0@AvOwzq^C{}#0a;pEvE8Ws`Z!Tz@;_{_tNc%S$$~s?a+9ll^g(@WJKJe^o?&EmpZmJs3^+R1g5N({#%$xVSD(^2pK-%wKTY3NHRjM6pUqA89C#(MZJsZ<>@7?i5vhD*d`%3%XN-`hLRXnWfUFzfV-tF0rsNegkmyA!>nbLlssq_c$&2cMP_tw-XS3AZCpK9Ows)zKmc7N4QV9jQ!@A$)ylXY*5>+aewGx`;mclOKio~*C9#?3n?`(@>abe8^?nWEb9F21Jv<KGh@?fexbe%r1ix;JJ%OwP=E`(9Gs8hul><NHr1sb8+D>~HZ!hg5p;(^kp2J$j&ym*c(F&&dAH`dRtFmT>83uCcPeH4CckI^H|slVsg{-)<>>Q>`<qAKeW#-yClptZwPv7}P?>CvJ(fKQ&CoVOMi$=W%kf?!CPlyZUdoeXQnBh97!7S@(fD4Q0E%f0XsJR#}%f=8v>=?=4kBdC&0^a{aowaE9)UN#Dx#>w4I{W12U!c982==%?@M-g}_EoG;VH`d#%0wNJ{dzH{I8-`XF(`GDRZBc{6aXMsmu2Ys!!@729o@q*l6weP&iRln(@y_x#sAMVlHF?Uvzal0+;c&wdATz<=GH9r2Zv6k-5ZR-wX=8dRd_Ui3;ehrm&dft=!lPq0QbZ?I9$o)Xo6S{ZC)7L%K<*i5Uk}|7rdV0m_?fY|9kotc_s`kCBm#d#U-W&U?rF&ne^3qP(^{T#qM?H1D2&^b4{{BkoXT+_e$29M4cud-PuD)D%ZkLsD$aYwHqt0ilzEM%URim%8KXS3E?|38hFU#c@loEeqq11n=o!i%)rMwlMN9K{^r(d)(t>5uuORsO$C?fq?aa`K}?Ps-)1rnZ?{f%93>E7F+kZV0Oj&{1NduKg#e4u;*@s|^2{O3lgaqthzFYVu1Vd>szdp}L}hwGp@YprU>@y>P7@t)0JiI1qJ)*tiA<uu)UbJekQZ{7P+c_Z!Vv+C!!PhHZzSz}qE?gN3_Qh(4f<;~WM<mdl<BEDuzxo$owrq)k?shi@Pw^8j|b^cB`ru(+fNIOMBRQhLJmF;#4RrQT+<=y_pwu!nAOuQ)VIQJnFKap{EymKFdH%6Y7@eFyS#>e__>P6ifdoCvG-nZbiY&Rra^~d*YFPAr#RFQt9i8rpClJ<LSll!jEMyBfCxn5-W#>b`oM&nicX3y1Xd>n7hs3YT+W57jM{WIMXb?^N+S$xs>1ic;Kt4Y$&Cyits{^5dp-tr|Ti06JUa6apm7MgeN_Z)AvIwb8o_din$Des+kQ0o8rhU%w3i&yS@FCCEj(Wwc#_ng`ze%VGfK33N`>bmTBZ(3Ti?yb~!r2d=tWSyx!TOCKoTf<+obZ_QfAoc%FQ}sQcjySJ-<KiAm_nyPE#g};~{l8sNt)q@NQx3=L-k51hKbxdVf2OQCqI)xRo8|J~zbXCvy}MfH{V)7s>E5{ZtE{tIpGdzZy&>)A?<ePDmMwDr;*A5pCFnk2O_uE*Y$(@}@NDuv!|}^P<8|+^5F`D0YKf}v*?3)TH?Y6Iv>!QJo{wr@6JNq7zUyP@&)pbV2k>U-sd(M{<GbUd=}&~q8_l!E>)yAtoAl@V7E=G~t}bu<)hJ%~)|X+@{-YOU{4ZC!qI>T{juYPJX({cTTPfo|sEItk4EBoOxGGNf{yX)gKO1Js`qS}-9DlsI?RJ9h&C)fc{?+-ae&F7pa=pWw4}VI~y-}x<Z1=Tr)t^AlM)DkkH_POR*S+6gOzP)5D9_OatGRvDicGy3J~}Sb`U@MmeU8F1ZWW5l{;r&%&LhVg!(@HW@M(FZ{Z%F9JyM=+S6n`#WwP!)`~Fn-XV#*J@?P%bvueA(mQR#7+n<!{T=x>nTe06N@7>Zx>aUBD>lEIcT_j%j-Ys8C`_>_~{+pv8U(vl$c}t4!ja@gyw@i@vU%pS8?*DyGDSA~M$KS3?{l#l#{tS&y)4jQWYFuXC`0b@Qz5T$<YvPUdsvX~s*X8_j{14mXTz<z%@y@!mLGJq;pRq1Ee!?*shvdgHZlPUdzj7u@{g193)xH0tBhr4otuha9J-+Dj_2c4nZ*Bibj?2LM>bmJ)-2RI0t?3ml-Fr^&mF==FnPIP}er9;qCC6I@#5?Px?_O`0ch*V&<X+Ow?4{yYy?svizG6$nH=ZZ=bGf2qe0~`%o^{NZf1una;GK2M@y3i%(w|=U<v!tlRk^>z8!sm(>fVYRA@v^_sj7c{4khc}2z+}~_r9D%WIXR&llMH6evtJFZ{>_l(!IY&lz7%j<LAMbb?>Z`jt_hj$$rT?Z2d99<(+ldY$e{G&_n8T-xWxBNuIy6<NJjr>fZRYoA}h$GCy-hx_#A>Qh!Ac8J}X!r2kD<%kkYdM8<h*6X{QqJa0Jt_a1L3^(&W@cHiiFRrjXVGDY`h*9Ou~=u>L^{ofQwbNQElKdSq{YxTr`JWlra?-;qiK2lfOf0US@dvC9*(jT6iJgwh9t$XLW$?-<r%C7aqIyqkYf1rSDcXO<2CvfkwwBvZ5M>2fLywVQOS)MuHxxDi{<tzTJ^8WSNrJvm2I_IO~jSH!Xx)0RI=31BhGyahKKF6Qm8K-;yu)pQKFz;u4ace%-z4Ly?@t*LXly}}cdE$N&zxSRzpL2g3h>etW18?r^k*NE??C+%hgE-mV_^i@S@o%L+W7^Aoa%ewk2XA&+Wo1_1*jrJaTgLX4>%x}-X`lBzp2?Tw{sNzI-|qOfpGke*U-<{$b9v`JHt_p*@|>6Zl4~4%QB`DJIdsnD18rN&ar^b8_}f$EzAImh>{nCq#*{N^ep=lI$U6Mu5%J;gNdN!LC(nNi<ohS*J(6dBUhxk<lKyXgU)F~YD$4yc-spBXPWS%1yQMzQ>1Ok6S9Nb3mHSu6d!M{7p7(Eo#KCI2Mw)ytXw{k_`?WI5Dczg%?j*Q;pC!`&K?`KNdyA{~9q&BXJKo!Ep|r#M3h&S5UEX;wVKfwPj-Dv(@cz@gZIavb{?qYB#1LsG=SgXQc{Le_m4juwMb}xnHx9;#cb=OLZ501)Pw{8Y$~utWFY5;0cyGI<d(VVO@y>gOic3^Gj?Z|{fDi2ND(x@7A=ja+>t(;5bdmAry|H(ZU&bd}n5&=0)_B>kIW5G8EtK=CK)EX}@6^wK)>YpqbU#6_Z^l-a`ai9f{-^Gg{-3WV{pY=_;{%(kO8xR1WSuF$UB(ITZG9zK_x{4q%656q_4LRt=hwz(#PfdM7=Kg7zY*^@M_u9l)%RCizRzw;_nxgC#Gl?S{hu@Rs_vcl?T+`~E-&B9@;=0zxI*?TvEDJ&uTC@Ny3lgpr)vD;cgl17g{U)`dE??v%jG-PSI?K$e~z4&`MclcjSg!M>)u)!wNKx!ky`Aw>VNGv;$w=-b)(EjpX%OxU%sbvyisPH`fQHxd0KBL!&lywtb6ay-5;vYyS_V<nfE>@ZMpjM#nLUR9skegGWCDejMsf2uFxi#2X*CnrNDttb#L5y`vcv3bL~>!S6j!MpLg{KZ+^7&i0=KN+tl~iMw{3T>gORxt{=<9`x@Um>++x8SgGoloOeU_X6FL(y<>w`w_N`D2IBY5y6N)sUl(7u!(~_dcel#-&>NTD%*-3J8p-#j{;pG%Uq5uCjBCpE%)D>S^s_EsA$66??VE4t-dyTY{jrMqZn^5`eNX&``j=gP`)%pZcmA81d23;9`98Z{)CA@0pHcnszIW<+W<HP<eb(jUtEs<VF<#z%!{r-Pl5yKV{Fd&`KX!=kF7N#_>Mwqz`eQcSdNVWcZCXRV5B_5Gcg^k3Z|!r<AIE2$Uk@68u6y(M-G^QC?P8sl>gQog<^925GCzIgUW`&dFEC5>+Z;asy7Eb36Ix_4KEd7@p9~)~J{dk}d>kJ<J{k3c#wXZ2;}cjiWNM2{=3B6L=39mjns1H|o^KiTgXUX?51Mbm-kER4-L<CjLFaX_ch2h!A9P+jKKQ)O@ImKwh7UTgGujV2uY<jFUR#4cTA}tQXdQF>e_O|HEmhxlnS*#=^~oWbZ-rKFQ9fwB&G13%t?|je4^;-O=Z+6v&&`9c%lBzP*NY4vbiJ^~M($G?be;0%dqa8STp@WLI&)b1?}^{9>fe)jX+(vo^ToRVt@1`0>t@Dz6yf^o!1B-4$sJKP{R*F6av4R8fqk_<4YZ~G&&kaHG;m10|J9!cHmLRg{?ovi5X0!7Uiy+za9_9&`6}E8?oD=wd&7}rH#idRMZN;}f}_bEa5U^Ad%`|=0ND>70KZ92gWrT#lB?mB@EURhZ0CFM8h8r14z|+|+qoXLb1iJ=yRe<BU^}P6cE-RljP(?<58Q__okB*!k&N9GG8&F%jHZwS-~o)q6mliJhO|F#3bEHI!`PT!MyHq8(#r&j%@fJ7@I-hrIS!r-zd??H-+(8Pqu@#Kcyc5>9)6u14UeWzuTyNEK~98cz%wZ}$C8ub$@D3fV)JZ@&9lf!@Fe;)i(>P1@^yGR{1!O_ehZ#Mv3VXj6P^dpCu8CH@IrDnybxYQ&Vm=g3&`p40(dU@7W@`{n#;D{p)a<38^4I(UqP{X895i8OZ{aOn-`OF;5oFtn0yCb3@;()!}HnCB@~;NlZ)U*^l3T8=B4B^cp2MRN-lxzc{?IR=Bb^-;BoL6au7TQw&$rm5AAt5m}2ulauhs@`UA;f@IZJd#pdDU2zUhj8&19k4~K`4qv6r?V+c7A9>_L^@Vi6!yqqzx$KtE>YtZTRa-U-Jd2%a!9^OaB!u#O2$sX|A@Bp$CJOJ)Oz6y7NW5_vh4EzrHKKu^6pZpl!4__d^g)hKAlG#Fpe}r>~NLGMz!_~+}a5cCY*&1#Jw<BMI+rb?vHour&T9R$Zm*6&VE3!4*3T{9)f*ZgdvI6XZvyj=~Ebv|S+a8O%6r0bIAH!$io#gxQPIwVH2VMmCCSQen!x3aBI0EiP_JDiA3&>b_0lb6U3h#i=kf-4@@HgaF@HcQs`WTc6k<3ckJ}aMX&PCpbYlcYXBW<6L&o=)=-ShBIa2mM}PJ<7VZ^MV-ZR7xW8@!h60<VR)lQHmi_z3w9d<4Es?uReKKa&^WpW*x=l0U-vIfrVI_Bm6FV)M&nHTY#Xf@}syz+K38a2L2M*%9svcTO*z$hKrhxFhFPTZ+vMwR5i_Ss!i)mm|x-Wta!$C^m<ZxnO5bgpy%!DBP6n1b3oOP05CEL$+b_we<1)Exp{P*!(-0Ger1zxIl<xF}MI+maGJqg{zZQ;p%W*vNBv3u0a-uYry5nr{MB%LGqCyToC?`A$b%25BxcK4E`KGL9T~Sz#o!x;Sb^EWIuR0JdAt=9tQWP*xV<*3?w7TSKvr^5ZMnN1TQA%!i(Vz<a&4moI)OhQ{WrqP51`<EBOfi70$u9+GCxAVslZlI9wF2NLGd`!d1wsa25D@vJ(6}T!btJ7lE^rIpOT^FU(VW?*2lt`8s(Gz78j+7eARuUV{_i<K%7lJMu5`HvAX-Y>4FV@Uxsl^+@}isYkK71z8qu0f&>-;c&PESr_gAw<l}B?O`uj9`?d7kOkov;F6?$&XnY{&3|(qeGdN(e@~u(zlSf8AHtX51adi?03RTS!3W@7WPf-U{84&|Cx?>#;r^UgLn$`THvT>LW|Iry+3-5j5Br%1>nJvVKpuykIq?B`5&i&PM#jVO^l2G68=lQJY|fcpo=Pv(C^lCo4Y)d7nGAs|!&S&Ea22>JnH8=IhmzUgP`Cz}9j*b_By+$u;W}h4xDH&8%njFrUm%}`Ux1sCh2SP|W3nLJ7;Z!sfE&RL$&zqGxB<oH{OP3v`8-(?ejct!7Jw_lmB@l{CAbV(2rdJcC7*`N!sW=^a5>mR=7K$NX)*^~8ZJd<hfBfFk=fwq;AhFK@Uw6UG7DS+eufNzpMi^!23!nwUR6E?7l8|tIpM-^(ezTB%tPjc^T4&pYVaH61hN`D0iH-!hbO|L$;$9(_%*T${2DxltO}2T$C9D&Sa=*+10DyzPS%89hsTq3;PLPzvK~AMo=m;~Pll(GP2j2U6tXcq1)f1Rf@i?f$%gQB_${&l{1$AcmuX~uvH@&oez-oI&-nM;%SV=n^TBz^;;@~0;Jk2cvKH*jiQ43waBa9QISrmhpX!qN;CyUD`4G8}uT8PJG1&%g3^ylR!Oh_&WCOSfT!-|)b>I?Y7PtibhaqV{OaDQ!`3`v&z5|~kcfzOOE#xA23p}6f4bO+8$Ot$J?o9TAJHtK61#nMz9=QXa2X7|Nz?<Qd<Tvn1I6&IZ(g8l({Mh*SdD~{Y*!&ExK3tz;`3%M8e+(%$=fO3G^T374=5S#+FWCgn3maq|*nl4zk|kif*!&4;AJ<PPHYbsH;3W86@)Z0oJcQf=4}sf}^Wk>zi)0l1BHV)P47Y$=lRe?qa9eU7+!h{8ZiWZLYsi!E8rUKOum#^DAH%oc2c&&0ACUjxA8=ehrP%xhX&=`w_-ymnWMSAYHh)Rxh3#VVXQTn!#pYDfKCY=0n-7tnz=z<~WD>j@9!0(jkAgdrL*R~ZOR^o@5^heu2sekDk}cq-a5J(s+zj@TZDB9mfgB8XfJc&R;F0hu(t=mP2gzITLHHc`0Di!+JV&v4BgN+3<QMR6crW=iycga>ehKe^H<6#go8XmXD!dY2N*;oj!XwDl@CdjYISTFuw<kNo?ctZnmhj7P7}*>SgIkeJ;Z|@PvKib4eu?zLFTvqt2RIz=N{)oP!o$f`@Njquc@SO#uOQFC=Qx%tC^kovyW!m&zi4s~yociyO|FDjay+8R5%37cJ(_F}w`Y8#$uKyKaf~M0z-<_>XfhlQXI!Gm;qY+w-)8&S(|#_UNwL{SM#4V0J2?pM4)-M&!+qgd<OX;a{2rMCzX!*WH{dw<D)}pX75;&=-wpl1XPf^di^6uX`Dt85_-VKlSp_ZymnNTwOT*8RMd0V)LS%Nh5d6fDwBHRqq1b$nybj-kuaL>`75Hd+i3ktLQY7pD^j|go`_KNq+i?BIO~JqE{xc5!H%q5Kh-CaxM?`pb``Ir20W6DpDA{hWw#I(}Rt`@s'

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

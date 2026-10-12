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

PART_NAME = 'part_012'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8512669067e448a9b1d3fb78bf0c61c6/part_012.stl', 'relative_path': '8512669067e448a9b1d3fb78bf0c61c6/part_012.stl', 'source_sha256': '79dda11572ccf1e3bbcee713e3342aa4f512470d485634e6df1486f8a0d53785', 'input_faces': 668, 'input_vertices': 361, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.22283361852169037, 0.08488866686820984, -0.3859137296676636], [0.3383801579475403, 0.4999997615814209, 0.3859369158744812]]}
GEOMETRY_BASE85 = 'c$}r23AjyV+sD^2hJ>8R*se^KA(>@Z<}tHysJ7v7WXK$)w`GhHAwvpV38iF8Qn3;hnWvm{sI4@Sx1y0Z-u>M7@7dPb`L64`zVBSuef@vyf1drUXIl4q_H!LNw8@?$+0ma{op%=$DBt}y$1!oelkAL19WiQP-_((nhYlN;<P;R&{8*jauIqgrdL%hxoX5-eOC8yFMESa*^7Z=HE?+TJzW*a5Mvdq_^r1&a^h-5<^WK9;rpEk{X}yP~#;z+=t68;TsM;MBLr;YMk3V^1O^EKFvS(XNy`Eb)HH>NGy=`xp>qv_(;ya5=y<>dmrIM@7wVU2j{TBJ8ykG6TH_dhE)YqR$J-c>^@5~?ny15RgWT@Zdy|<-&r4mx!JF`N3XG(D?AG%?z)bDJcxJ2qp`6k`?-sEiSrF_R-i=@7>IWwgE&}EyXJic@0u=wG}F0V7!eh2ma=t-%^ZBRn%ua&Yu>U;8ADeq5gD)qQE)pri>)_O*7mGa)|s?SM1pOg{b{cg<`@n2WpExt2T{M&L!JN?%v|Lb3J-{_`JuSod^N<Jgy-@YXEL@OsrJr2HeX^+$s+TQqWoe%ZB2HV6B5BXHbEk*tC@;%zl$gbt$4{APE?wff;$~)7GZkBons2|?{p7?%;wX4LBZm%xm+`WeO>xLm8h`&(%@Y4^Ukn&#?l72ZI@Gt2&IDhAUQT)7*bd>&#$*1?NHvN6^Z&p9z50ZMKc|O}9erffcE(67nWbe0D{5#cmH|acj$4@Smem%crl=SnR3~m44I&R*4^`pNJmU`TWTgtfk3)Oe0q=_G{onwuZU!;EMg)Q37X}w>S`N%$Ws?@u4h_>gi*0LU=In;N~4AA=X)s*KVI^&@^y1wh^I6T>RYtZ*P6_WZr#?yTk|NRrXPBy(I?T_Gx|I+(<Emr7yo~eFl!YkrCn~UiB#}9AP_IL&6%lh>3y;SX2C{KM^520D=M`wJl^ZQ$im!v(jvbNv7bLxD#Z?S1F1joT=9DIB`4j$v+u3fY=I4{m+ofjY9&P$ki39nP%&Wq2y`1p2SJm$qqKC&#hu3WpWZc^W_t59BDS0Q}6uA;0f4?n)H(sf;h);|4m!@&Bt^X22)_3wPC>)&06Z`c22UH@K6+N;tZo;#Q4F4R+f``o!5dF~olculU!18x-^Hy7XL0ng?Ee47VCLp2Zh_%;uOmT4aF`;2{E+C#qb$X9M(^=-cL$yX74o3H$LG+#wmUB5;?Po8uqktbhMKb|MYXr7E7-uaeXlb<8x=g<-LZGMiDpI!WTer~Aw*=>Gst@MZdADW{1-)ZyJdTGzTx%;HP(Uq6Tb=#sF<bH!@9Tflk^p`|06cgW_IZk|UY7Hsx^cttWzeel%YtCZ1t~p!%^$WFp#+nzUKdB4E_x>2H_0Py7>(yy=TFaL`bU?1XM;A)DBIm?+p1*Ow=+MniN<Z<#%T8+fe8c8T`H%B&l<Tjb(fdXxO8edRg~X5K9CI+(U+1Ql8+AQpXgyo6=ySWLqn6K??U48bDlHeC-C2CEbaC<h1A||Y&%c}^ez?^yQjd4!=Xp|o`orS;<!{yY*DpIs`}Ks@Q)QsmpZvoLDfg%PPW~swcY78WKN5Lc+xgcyZD+yBnn%WL)%%YAOZ^weFOch}c53|xf0q9G9}m^`7u+R&=#P-L|L9qH4!wEjX=g9>H#c7?_kHw&wx`52@x6&F<v9$MsjK^sul~^S+;dLG!TbJR@gu(#(0&cSOZ-T3n)u<Nsp>}$YrlS1-*5A{`hByDANq5#`n~c?zuZ2zYkL~}B)(TEw~q7KTvFaGFi!S8(Vb;<9Oi70^%LqcPke95UFx^*rt75XN9s?jqrN|Ik+g5$CH0e9X#H=!Df8%Wy+ikHWx8tl)gS3P$=+Q2(2kz!4;Y~1KYXM3(UckLM_%Y9?L4wye6QCy^`}-JCgmRadb8-j#V4iS8OIKp=QMgY>0POR;B@tu|L~DK*CVTm?>;*<Yx(J2#P=)ztm9Uxsf@qhDOLRNkb=4%ZY?D1A-bvA7STKI(0O#G>HE(aF1~x9z4~WP&6dxft^K~t!|T0{%J0)g%f8e4{vQQ0gMOsaLh+rd{iVFqblDqO{NcGWgTC8*tN781)Ajx6=aGJeE*ux%%RN@#cTIkgad1)|-zM$pdQk5>(%&xiOxP&Cb0Aam^TnOpWPG-^^u-^$Ld!cThmG&;n<T!Uk}2)<HdJ38^xe+SWd!|j^o9@R`rm&@`RF~>_6Ggvwvib@KYFUB_|BCpUrK!+9Fl%Ta<^3f@>%ht=f2kY-OxvTx5ydsL+cJpd9UwY@xwpga!fw=XPY-027G6I+l(xJf$z1Rm1U*8*JH}MpdY>1JR^%AExcX)I+eBl8BaYD^h2ZSX9RseIV`?6sDYGs2hV*i=tpW+&ItP99lOPMx^$89e)+i@f_^xqXhzU?zP$M(seej8ZGYkI2et)#ze4VepdXF8;z#mb{6aqeO)eQXr&c?y=lpl-zpBqsc-`<FQvUbV+Wxss4+eezoo(qs-=8&2{dd=D`41oaykWqP{JJGQi@#@q`0l(7+TYrzKMeYzVw=;0zB6gD_~Gh}rJe5kTVy?ZotB9o?bqN7ecrdodiFQ{AilR{htwZo9IPL`up&L^yWNWIl==_k*LuoyllAZX84^EQ;efXD$X7=iUd#Wx$<b^2^N(NCcQ@2M7WBhYUQEAM{c%5`{<xn|zx8eX(P0hMKUz}1=Vq=uF7uf84fWsuQQI?Zq1^W$e(RY>ujTt!CLas>&iQ|(U#p(DpHPqW<Mo8!72jX*liv5y;m3o%TV#BC(D$CN^s!u*=%V`>@~ZWnxkbMW`p(O)_}(86Yn~^s#{Essmq9=LdQ|-I%!;~R@7|#8!FNIp(}RBGw>v+P_I&b`ystwWH6L2v|Mu&XK|fTopZdM_==;5z=0od8IxamK^uy0C5Z_zXN!k<f)=B=gel%yX^q?P_nYFw-Y1r|gZ_8WXKeb%%o8w0<-?`OMX;0c3@tyvs#rIaP{anU5v{C&fcOBMoC9mR#3%VzRzCUxDw&%M#Qr;!6#{G}0o(%fV#sfN@C)!DQXR_v1>pO=^o(%e-qQ7W8XGTkTe~{)?>pPo&KN0l9-<SMUe&2Ytw%_Jke0Q*aB8%U;zWTimN_m?%tRL#M=tR(uJkn15$o8?ie(vvcDCqlV&mRx^PQ^XqJMaEWo*$c6<NgolGK0Ri@#v@8zNfW3dDZ&Ssi!i7ex%b$ZRf|crM%6n)_1>8&kXwR#=o`w?`=5}?3eY!=htRt>F=E6UE=pVruCD@{^66y{^66y5`CM;tnYW4mwB!F<9<T@aX+Dc>)ZOhW$nd}oGzjJH}cp&eDYYLZ}XV-{ax)duT@XnPpHTGww~y)&f<HsZqxgc_u_u(R+&NHd2p}RQ+<=RhrDF{@Q_UzK|egZ*lww3MImjs%_sPgODP#aKQt$6`FK8=leN6{-G@r4e|ox}GuZdej#Tm8n}-|=u7B%?=3h<^`qA~dKa<bzsj2PsUCB#sokHTr_hV&ON?!7dr0l&`{nk&c-+BCH@%^JwU5DSTm3BI9SM0sk_*g%2eEfv+j?JqH<*gs}&hHJ*m&d$V-_DoyouPyG1=oXP=iU0O2kS@6jM#Ur^_=KCtiwd#v+EE)aXlyciS=0D*5kBYy)Vo2ZudC}zGwG2iN4+EB>3@t6n<iUNc0oykNXMr|06$?+pgn7KJ>|Z*0=f4`r#3$#kcv^Bd=QD=3DEBZv0W_F(IE@{~!5${%?A&#QP%5dm--gzOa6H&~Q0tvG1d(eeUq>`^fs<*vaDC_g%cd`1XBgegD^&)#rWc@ZPk(eV<z2d-H(!_I>T}Uben{Ut2#?;U}%f?gvKcd*Ax;{Q$mGB1z9F*l+mV*;iPf{YKnBluOSY?0)8V-M3gjzMrvv$(ytu_E%w>AMow|%KC0Xd7B5^g!0z+zN{p^-5<K_1FdiOht>~|Y^~=S>_45i`96+s_n+1e%^arvVt;G%jP>pQHlBZG``Ui?&(UV=pRLdS+4^qL-P#`Z=RW&z>)ZXg^+VNiXgT)(Hji1~?*HTdnLOeret${yZC*<BZC<i|;`f(CKd~O`+j@Mrp|<mvwmP2s*UNjv9jWI;iQgX+eVdp5;ggpVeVdo8pZNVT(NC;D?kCir`28_bL+8)=;sHJXyt%u4FAm)}NWXXS{o3XM>)Y?w@w`#{IW6C+lAf17tKZYZ6=!SxL+@0d@Acv9p4ai@d?21b@$LD5^}UrZ>iS7If3SYy`Ga@eD)l+vuzAw@_I$(o?xEV+|Mw>8IB`xA9p-Ag=a10#a;_2`-bH=RXY4pw-=5FJ-xo6;)92Qn|CHl<2Y&qg2jBmEt=4bPmmcPP2|s?mgdhFonE3Ji(qPS#){mcG;YTul)VyQQ$H<e`kDrfO|L%+0PJ8}Fp0s}a{LT7LRgpX!S~x-T5a)RQ$$H|4*FLHKzxCWNJie)ZZ+vTz<{Qol-QhhnUvu6VCLdbgo;O-Qa&d{i4>-^C$%odr=b6?IC-2nnd!O#r_qaV5-Fsf!`Nb^V4_wl7)KI=`dfk1I?vprob=JM6{)!8FpQd_F8)?5z>z(kGwwH5V@0jj0?D=q{x#rcl&-t+RBkK?9_aV-ooq?P)<J<FR>w5*~YX3vu==?m(Ir)gCnh%<NrR$4z?&e&j`@*LCu9okR<*!nHxN`Bs1GhMii9AlS)4zA%Pg0C&eym>mPf`X}|6lz{O3j+J|G$5dGCtOZmtrv%eGWD{8y*XfLl?qEAA@@*IZpprJdmXIOrnnGVEZ|vFA#<&qLbi>@C5WFcmjL|HTOBgwc+Z7;WV^AY_vCQGz_P~1JH+HqYuKSp89;wXe-!gOSm^2MjOG6sLOD-Sll0r?y)!*YxBQj@e5)2RrCY+@mLIHd>@0yp+n$t@L2Sbz<e1Vj}C!{Q1^KB1K8;M@Oaqt)#y3+9Bnmhv^(R`oqp9P?q_UT!7b5luu&Iw86(3lF!zrW6Y1+j=6)zKfqqP2?uQU(=+mq4FKBhzTb=o~W1dFa)0pS(!~ohjfHlw!b>VkopM5VDo6#-sX82q5d-z-UJo+nq9xk1v8cI?&VfYsGR`?e90{1oT_yPS6{sI0Cy#O0EpEcYfrUhb=hcJBDQQhk(n=t$$VR&vVK0|**_rgEIKcl9upSd<%i2JmF3&91^=5RsyCr9-L*o5J;=pIMegyG%j9C$bU88L_UzKAYD=fI2LL+Bp(5PTi?H21!aFx&ub4mW@sqAlPSjJ4r5u_zpi+X=((II6oGWfO)y!tgBGKa2U9g>UD}a31O?9GKt2+_y0IZWw4s1GIIZ{jKSr(HjH(HEhPi=%<14`IPZ9Ix{eyGXv{qChhgmC()Vklkg_=Q+N}68}~H#zKt;418oiWfK$*ma2v)tg*>y)x%%!h`WCtleha=UN%f8-WfO)|$q6R6_ahA7i8g}A#6CMJ7HiQp@LIS+lBy|NfzLF88<BG=5Qh7p55f;}?>>a#zGy0(N}Kx<hRYI$-==@2pKlX}|3w&n6nz0U`Z)Y3JQ{rrevEM(&Ag9hU601M>)f!Jo3|Km`&`_`eBDJKQixRMIhB6edGE)%=*KwPbz*oEW4tD?uGX;b)-X4A9gYe-ccW;p(J}C7_)*5k=o9D|_z8F;x)$CDmq}7J^IC>5+!O5s_k??)ec`^$pW%+NC>D#NgyEfz>PL>U3B%72hNsj1>CE|be7gn=m!*zkfi+W%`xfKgy#np%iFOFIzXSa<dUK$^hRt{w-5wa9?Tnw%X@T*a7Fd(hXzw%V)95t#X?O>^9o_*K;hyH+MF_*~&<=1rxINkt?#Ngh_G9%-jm1{N@MQEUcrrW%{Scl4Z$nEYDQ|;I#iC0ry2hdtVYo9|3N~5-?hM~Y7`_QL_qd5`!=G^9r{GWEXVIzfv+xYmhiAYa$09jNwK(d-#TlcL=vLT_xzQb5Zw<`RR_1UkV`t}dGIKtev9s%W3Tu1{V`taA;i8ObslYQ*in%MrIJPIcGUr_xce@6<1lCCx+FcSZj&@4A+F!%TgyFVmXSg$SW4K8y^2OqBN5k-!=s`!>gyGlF1@LR|3Uofa0zQErfKR{|3B!45XI|#b=mF;RW6I1x=LhC}KI>vW_qOX~0qbZ1ZMEy_AZza+eY5K@A7hb^v9Rm5Nnm^$!);+ZwvB1`McQ4N>&9?pxGLHNZo+sQJ{r>{u{c5)UW~pBFNT+)>F_f6IGQs_`8b>-7Byl~Cl)mc!*$Udu+f}wUHBft@MY>V_qa?Lj-oHaQTTOq3H&;|5<Lp9gipre5}K5xdK6A#j2!d`d=Wi?9to_mBdozAjGbMRi&?Xa89Td%m$Al|F?M#%8~z*35qL&&FpoJH$Erjf=DZH$Zr4DKq^oP*utU_Ke>IpJ+h4<%7!$))@an>KnH$5O$I3)vaf~p$6kQH4g<nB4;aA`cG<TA62AnGvwPJB^ENT;m>!G<|qq*UFa5cj473wqhxI!2{g)WCr!K={-yc%AGeh#mKzlg<u(CkU7pTpT1qipCg_!4>&J;wSwNtu=C(!g3>%35B^*x9vhIErRCSDyvLm(g5FSD&3+%wI0X(LQVUGN<=4?p26df%RZG8&Qk?)naaJe+~bKF)@5MUOl)Tb7R<i-#6dw&3S-1D==!#65d6>L(juTP5JN83;6qD@l`CIN8f;-hv%Vh!t>z$=-2RmIDeArU$6<o&0<<H7ENPO32g>9qf8~P4gWzH{s#RT{s!KFz6o!D*Q0O1>*3SrSMX{0cf#<W=sx&Q_<H8%de*7YeXQLtD6<NE-nqKY4X;M$Iai+x!>7>w&eiA0@D((F($(iKKXad-@v_fpGuA^h#`JEYX<#iGz8<e4d_DXpeK%T;YvY$A43|eM!A8y87&d1w=A6Zx&HRj-a~*SjVstlZ{N3nJ_(spdG26-R=#SAHu+eM*KPR5~mzh;#Q3I_D*MJ+Kjo=1w6SOJZ1a6KthMU99(E4yQ*hQ<uE?f(}1Fi+%iI#xxgo~m#!bRa5(0uR>aGqG?La#&f!Pmk03B!fZ8{tB5GFk#ohHpXdfNy~-pw;0D@ZD&A_-?ok+8C|_*F&4a_27nRBe)@aFIpGA7p{#~g=@o=2*bCdx4}klf^Ua!Mz4o&h6|v%;R0}8G#8wUanDN_E{Nub3&O<+!$r_Sa1ppTnhY0*OQW~IrQuuA3h=FPdGv0$JX{g216PErp!MJ?a5c0cTn(;?-V4`+??G$B_rR6WN^oWPF2Zmb^mh1m=A#T@xFlKtE(sS#^TK%<_riqXQfM)_6kHB10vBQ2%b}&=(u{98v^-p%aV&>cfvYfH<<OdNO~$1hS{bg)Sd=3Smqp9KW$1HR!f*&J3>T(vA+#J^7B$xo#-e*H`k>ulqYuDFdk5J3t|!_V?n9X{`Vbt3JD?rm2l-4dGz=SU6W|V9cjq%*&|YvCxFy;K?#5?2qg~+6a4WPW+>_t6MO(qW>GMNqPxv9YBia^Dq0JqM9(e7!R~w=$UMu|j(DrZ-KHrw;6sXJS!{|V`4fpMerodg{H1uJ(J-_RZros2|yHvD4+?KX>Lhpk+!2{4#xCg%*hz@|$Xu}A?@Gx{BJPhuK4uJc?t<hAtHGDtXAHE+RjHbb9+<P!#cqCzXI64d-4);a-!F}NtXlu9y+z!1TZU+xS2g8H8x8V+LlCmXd|DXPgimN}K*(hcC4=WNsnf1>If}flpt1JFT1s&StH1Dq1<|><XbeVZ8JO2e}^Iu8'

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

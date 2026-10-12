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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4ff841231d7d4c54ac917e63c678c9fc/part_002.stl', 'relative_path': '4ff841231d7d4c54ac917e63c678c9fc/part_002.stl', 'source_sha256': '260aefde5ae3933e20bdc4cbeac9fd23268f8dee20db7d5fd5a19afa7d51f8bb', 'input_faces': 404, 'input_vertices': 306, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.28463509678840637, -0.4359937310218811, -0.19928377866744995], [0.05324359983205795, 0.23930072784423828, 0.2253219485282898]]}
GEOMETRY_BASE85 = 'c$}r12Xsx@zsGk(^r$gvxY1%FjLs-=)KNy{uLU!>8Hp|uGCFe*Q4%G{C=*;nkBA;M7ZJUeAYtwxOfpIs{B`e~@9#Tr%v<lR_11gV`mOKhezWgB`|SPO<(#|tb#l(_rsSW88r<RAzO~(zGNX`kQ)7Zgg$)@HG`d!B$ap7J6u$ZIFJ0u@qqARcCpAV*^b8CdJz$h)6N_iFfsH-AEuI5MjtUzU5Zr&{sK6l8Zx=9pbdceX9vl!7WPGk(uXaOkOT90>Et4(($A1NkCRoNax}0okg#Rs5)q-WQrfRd^Tr$;>e(fecx654C!u)L64`20J4BsAEaw-0vF$%sm%9>`X%`4MpmbdTg3*T0twA6q8^bXUvWj2JbAIZ25zkTi~e1CpXDgRY-l(+d@-wA#2>qT6zQX=YCb&KpmdnT+Fztw1Ik6-g0`1=PNd{yb`72HS5;_J=w);ELTYb{#AS2-IS;QlAo6#q=Lw5P%N1bnZxyVM`m`YQfz*|;0`)oJ{Bw7*na{N1tk#b)?!#o^n3ZiV)1V~-_6-HXCkZ8uzi7JN6?EU&rR&f)u)CZisG_Vzuduc}+&>)jSg|A!nrgnF+;p2hcv3{S`BIrmaf{^89t@V{Iu{d~Qj_#VB*|E~B+^y9c)TTNe2Yz$vt;&B6ht9B@_AANfo<s&Ygz;$ExEk`|-w}`*GCF)U*6=<j3#Rt9?w-o(jDPI!x*jN5`3iWR}c^36HX*eI{JW|9j+w45*?QnZHK96q(Uj>hZuU&e*9QQXkkCcDsKt0xobr@fLdMew|3-{~Dx{w0@;WqIz$Dcquf|BN;o)_`rcZ@h7`8X;b*WWc&{0Dm_Uv{)ThP=8y9=<-MnzVDQ^`PWeKk*k1Mm_fWGgcs<mv@G*<voS*vUu5!;qN^vOZ`2UC8HmPlvo6vQCj@$JyOr;hmy|@XQ|)U?HsOq@4-BjulEe&p(Z{@Jt|MaD17dk4PTFLhx^rC4@97!LhecV9UsweT1ZL~t`j;^{J;pgFW-VgO|^^(7Jo{H)U$8zHk6+-T>MV$ab4TGx9jk|omTOEwjvK5i@Z;vo;q#Bw<m2uJ1#X@i~D+5R{ZKGmn5To(>G##s<?`Oxdp~UzfyHR>QB3$itFe6D&w0p<|MA4D;>USR}S^qn>Lnp=~<lkdNa9h@oL*}-`XPa-)=mEdfyDkd{hG>#UB%c^-JaWVqMbWCdqZPyJKExeM;lH)-$8w>)DYqK2u*FL3?ej#eZKK{prX|w&VLF(vKt0E+k`K*dBzVUoAhS!Pi?B#rWzkS7KgkMJ9{i;H~8C+upm-PqmuCSMA%OyzS{W^uOkNMDjgz5w2@@>|F_s*d>0m%gATz#agK--z`G?`R>SL+o#rc+*eNZ6v@Nh$P>%kB5QCR{XFtl#k|4y9rG_Fpq|4K;^$r{{W*H(5sXi2xcF(;52GE|R$+b6B6`Eun--ULzMXv(<!-i<^6xgIKdmPNWc|tAT>N}*mqFiGIfU=ccNhO+xU91aBlbf#m6G~*mqGt%cO%gMmYwOijy|*i#!qF<+>3rLbsWAUBUIMs8AWB@mY)OPUN=YP@3%)K4+=SOf66@#d9H81jr+FvUV^W?wL^beql1p3Jp;~4c@>EE*h6CzabKP`@lWNIdivy({(BKB^{80%k7eo++@IAYSo-z5v9dnz&`+bjULNqZYPXPAs?83}JI6gIseg9|StkqM$9%HBJ&OKN@eeSLYSj>|Gxma#r|NzP)>)gr9QmN)V#Ob^2ji$mHaLKOy|Dnke&(L+lN<BMeALEEd20u>TV)?QEcxaneuJ5~Ppz6R{a)uD=AS;Zh^+Gme!}=!tH#T`JmxO*;<EIM+Bi?jH&4bm*;V#&^i!E1#jjBe?XY+E*@wS(U55Fj2lkUZADfExT%}|mkoJU0{hjv6di&t6_)peLKTLXsd97`kBz|F=tdprB+fn{dZt?ro!u{&AE~DSHthf8&|I$*{Th$5ciKSSQ_~C2OFUohs;eYsd(q&xk{d+I&L+gtBum*gTJoNCyeLKS1!PhHBAa8Y#Y1kL-*A8M`*P^m9F1F1((I1Ydd*JKe+?RbhVJh-RtFk5OAN@9c1nRXl*Z|*lI~@6@9|@Fk^I4bl`MB7F=1BfcTms+vuTtsKudh*Fk6I+<YZXSn>Ap*4d}E@eon0SF{`XFketI-H>GM2sBrcbE*nOb1^W$;ZC+Cclb?Byb@8{#|aP5k9!?vmD9+b1hVjL~k=gWM2bsOubO09?Svium1@m1$P?fiUP9A$D#{#ShjUvD)|)|1>9<eaneqLd%JTGp{Cvv)#^>=pl^5AMfaw>|Pod2N?^yl$f1_S+}+p`CrwwxfInS6P>iJ4?S0UJhTsz7O|nIq(K~u7xfYzeqVb4;(vzd1dVuB=wwZkAAQuJwu-BPCiopx1wmL^~go^r{&u}6H)%vT=cWG;#G{JE!XM9&*!zHMFq4=j~gcC6WU6DzVt<Z>dsx|T;QF7ys}5%!un&6zql3Uf9@^oz}LN`pAVmfZ!Izbd8OWOLLNGXypG3p$NhmkSB(>J4zOQeC;p@Y$P?|T7usvDk+}usn#{W;^V}KvZ!10)zOC|2$;0aJP~MhSRLbYsF7vM237lW7Ia!-ffAk$0m*mAVE(Jrxf6+?vvQR0Eqvm~JBm7+}C7*|M$GAHtHW1%4MDnEgLOHkZezE~R_gPE1{pdIA*!1;i&&qi+z7s~v`TWos`1&Si^t-mctel4v7fbnp3D^hq#jWMMp*4~6wovq!E#FTVCoTEjI+Wj7Qt~8l#9{Q4*Znx?*4uKPZ|{w~Qe9WWS5Ms}pP$u6KG@H%SPTDhtmH|j26CRc;R#<mvrW#)@2kjs)QU>^q02Guj@kV%k8G{0ufg|LN6K?j>prqxlq$9wpXUVQIY=vb0rlvG)GE|dfBer-|Lu4lR7)Kzp$E^)e)QoI&I9_9-78Sf>;=d}J^y4mx9*-I{<ZtEPCq_?_UNY;;<;Akl!tGb8HsbB{>n}K2Y<+O>`^7>>l2y3U_KlS#PhLQ?IHWwfdu%<BS-QleFoNTwMG-)nuYVH!#`mG>UX&y=a?~ml2_;MVjofKj^TPXPY*nY>ciY*-nquZw~uQe=aRU`GVWj3l5=Weq&zQl>@M@m?<vl~x}%YtSDn43o|Xm05Bn4SV!L}p=5w#J(!Xa*$o=mxBmEOR7ry@I64{rtU&y(|`E?BHbuDmR=3Qkuhk53}S0&u}JW?Cus+RpAzV~1`*Qd^syc`s<SjM-I<Y(cdvY$O4D1Jtc?5AGcWqfN`#4piM_8tG#m{00M&LZfPo>I@dva;Uh?1Qf_iI;IHA1mwQ{b}Nd>9Q_7$tC;l$N}(eZs)N6INn9e`MBPPh0uHH@*Le_q4eip{-1HUFGtWw%xkrCJ$%Q&_vn8|t+!H7E)V$Dlg{$|Qf`!-<0HFA!*Ayz?=g}RWgmFx0$<f?E#osPF#y+Hd<S`?3b@Pq(_=QyH!400&$ZTiQF4w=NtXKa{sLb;Ux+-^jz!7(7a4~6q%U|a`|ZLm^87gaL?pD*ZrSh4&XajF)jk{bciJxR8C;8DomUC1;HwJl@%*N&p*5gg8qI>=%8K#VV`C!WZ~A>E{O>=>xo}?R{c^vTW}w|yba^l0J5uuV_bTvJ>1N0et*W!MKXYt2{PN#RUVm(M5dNz>)8M~YD(?l3444Jqy^k*Q<)gg6&^@I+b;`ll(_Aqx)PxkQ=W3T@GRlW!gdu;j9>l=+JwE}y%N=>I<NrX${nbeE2l*lYwclcJPF8^p#!LUCNk8<8$Nr+`^&Jbp&33fY-lw<pLz96&%KRUM^}#WJ9mY+iJ{k?bN;=x<==v|&4{YBKN56P%ljqm`_8Fi1>Rdg^kD2}pP*3@agYo%MBaD~!c#B*&x3d-X-?zwnrJkRXKKE5%BIcoLvup}J>rwrnhf?Hu_e#3_-BO~j+~)^b-@09v^N_vVchH_n*5%r@@!m`&uJ0xJ+Zxa9_EJM*;XC3x!H+A2&sso9Y0t&o9pL9`f#-SMTP>9FJlX>O>zcCv4ml*}KgX4(Xiw-Id7e5^eiO>uALBir>a-2(gXQT_?9;}CaYZ|N^v61HpPxtSvA?f|>v7$%KdB_=NY$|s>bw0|&Z|+C5~Q7TTFN;8i1s*|XUTP6`woKM@Ra9>C31dMZhMF0^PQ?FZ<$j7_ouGLheG?bk>_wng*bfPTw^@+o)6Y#?W`{S*>mbd=rIj>Y+H2-?_Jfb=Q^~}FyyV4or80n3ac~K^sN(;WM50kE6+z?=<u~S&a%!|7$)oF<IU6X_ljAvE*Hxq`(1MN>G<5xL*9qDBuINsXUu?K(MR@`$OiI0XL~ukmr@5G%6o<~M{(X#!)u7&WQWYdXSZa3ydO6c8hTsq%lDj|D`PgyK|9avk#pnLGO{mBdH`P)+9S_Xwv)0?Ja@so*Y{=1dF6-B($59L#E-5n?^Qf(IM=FhEed|`*Rr2psw?wp*iY~k&oipcYFU3=&x=1TT-MKU|IPUOyMglFuAHp@+NwXKo;_pW+p5lzeIciUoCDYFmhyMU$^KiZimY4fe~|tweOC6b7HZAszFxV9?2lt#qr5&Z1@m6t*--LrP;FUPSG<$;;IzLyuZ|6n{XH!p8alEkd`CteykF8gPld1gpON<o!C%O}^l2yNpRIJb?2nyO<aygCY%#u<FH_3TTp{gTd0G5hb{Us4<&ZbZ?fGKK+bi&`LF-Un-?|6uuHL4GJg5IQ$A<a~l>8ax&vumaWKN{yO}}R1|Mfnq<zi{4iWGlBQ#mKp4-0^Q;?mD@oh?$n&)zBc+&>GxrFsJL-_ov%%!}AAOYrx}@;ixsI!VsEE}7!Tc97>RElb*2qWn_yZ<lD4x7PSd%74s@^-eXuA@i<Cl<XJXGT>|V{A7P=*9PYq-D<~pI)?or{hVG|^5jA;tdI8TVc3_gZnveK-T|_1-fM(<EFsr7$n}=O*Y*06&*ksP`s^Hq_tt9R$7^VJw|M;Cp+~3UJ)$k~F6Nj1Boy^)#r@^?oNoDXZqdE7<UQZK-{IS?K9>8sRvP`F^?3nbJGE4PFG^?>g3n1^SL1sf*URrkWA5NRiG9Qh_<E(fQa<BlFv|O9NcpCr{2gSa{U82Ae;JpKedT@NnRoD&hm))i=f1`{Q0woD{BlILkl%eirQ<n4dv24wi+q1g=IvqZ3-)4D@!ndES%&sleRp9UwpaCnYL(ARJBx0rgU>PH@U0CS%Y6+DmiyWjDDP`exZ}F^hjG}~v}U^ak3FP**V$74%lYtal^aTb`dNCw_o<2BuhgI8r2SXl$@`*fZRB^YUU#HD@%`kwxxUBv>#3ckp0>HfFT6<dqU9l!w+xz#`?L@8#`(bJm5n^HzAh;J?DS0hIZaWI!+9vmYaeQ0f78<^VZP{(cVRuWx5$lkT5B;#{9OZ)=k_~u#qYaK#-&vSoSW<w_sRR*8mFXu^&lC?!>#1}8dX)+&v%6mxA6PNudSI){qKa7Fivbn<X3KLV8CZTwVI~+?=SuDe`+04|9|yUYyH~w|Gz)AUN+ir#fW6;Npdpz0QDI80QnU44B6CM<WuAf>I1T=zmqe_*BK^1p*|y<s+@$MkpHCSCYxdMYb9ZFKK|W>oR3_<i1$kL1=WRYhRKhppOmnvIb>5Gk{^+;Qq##-$tS4i$);W)pCG4FuaQ&9Y1GGLQ~ym)BcElMoXs%V-AS~lldu^kSEiOAS0-1b<|S7pm!oDW;d10chORc$VZ<^c5{y`A#Bu5}@-mh=PBp)GoSH@7j4ak+>Sb~Qc@;I8yo&q_^#J)7@>+(;N2#aCr<ij`sn^MCsavVn$y>=g87BWqeL{Z1{QH$*@^94F<XzP543lqDUz2Z>UsBC{eaX)z=V1;PAm<_H|178T^RvkxjJQX=OMOqiOTI~cLB2^oM}0&-M?OrwN<K{9Og%x~Ox{3EC2t__rKXWhJxg9pT~0kqUQS*|%_grS?`N1?&`H$H`-05>n&g7yFQ_%hUyzG2O#X^mll&FA7S)|xi(G|TnOucjom!P#o$N&|NA@CDq81`oB9}H|pK)Jrj7Tyfp8AUVhHPpDC*fCQHz!dG*^OM1TAEy%*D6VMDB+UiKa}Wd@@lr@59%wjspd6IE@wm;BfN}oHoSL+W-8G;<V^Ao>K5`2@?2^Zc`kVjbu4)dxj!|4+@I`A^&|U|n^BvSn~|$gy~tj?7n2Vv^EW@^vCoM5Ml?2}6}1hy6}dOH54krvgc?i^A^$|3LjH;TGc|@B!#0@gY4mLoBfg}TC4Wiwrh1UQ$<>S~Y(zyP%22D3tFes9#f^AtT&E7}H?LQUTAN&oT%KBoT!-H^`G}!=l+<VHTXG&l^C|gfYA$jv<8RLmJw)FuSBzSiT#Q_q>Q1gq?nLcK?nE9)9Yh{To<W^So<ZJCJw!J3Ir)+i+l<&mT}0kQUO=5hUO=8e9ZsG=9!mX=Je1s*+Me8(+=1GJ+=1NGh#J%{sZGdb%`s8tkyZ3dvIn^_wF$W~xec{Fxed7w^*eGOaxir`IhZ_!I*B}m97A11jv*hUZX+Kg-#5a^$P-s1o+{CgO4tmOZ&2@(@AJDisF%pYjQE!kLyQPDVw4e+875DqjwVkfPp5{Fr;}$>e<aT)&taH6-iRP-AoWLbAo&Ms82JaXl{%ViCHJF_BKISIPYor1Pxhw{Ci|1SQiqU-uz$KTOm4_9xemkRF4SS<F60qLL{P)2!^q*}Y1AR)X=I%`n5>g0QbWn19J7fGljku^j;2l}N0XOQr<0eGW2v*rvE((>Ipj6uIEKlQ)bZp<@;LSP*pFkFJiv%<)b7+Ea(8l1Y9P5Mxfk^ZaxZcZs+HV>+?m>s+?m{#`aQWV*@x;+_91^w?MgPaA^B@^NruTKsCCH2sWqu}$Ti8|QoE49C6A<zAde)^Qh(>!EQZNP7$)ywn7ol1PTojfL7hfkL0&@D$xF!dsT0Yj&Lgj<uB6T*uO!>3(PSGrk-C(eNKT=~l2gd1scXom$rq_{<U7<Y)Hw1MauhX^97P^W9Y-EZ4xkPo2ax^L-#P8aFu6IyWQ}2ROKNv=OLA*!PjYMWH`HF_Z^-SaJ;?3IEvTKzEy#_iZOM(u7OD@~LM~1Hnrv!Gav^2D{4t)nsjlRr<Wf{Oaw&3EYDIEYas%pD<Obw=)LP_vWN&H}vNyRp!{iDKlRX(G*QVAY*CyAcenqZJu0*X!u0;NV>PG&8T!iXME<!Fq%}*{!b)n`byO5o!g~+DnB|DRy7$)a7!mpE4E;r}@>Ayz&{ZBW)^pF22@n66B&)0mPe>2#q>px%m`E_zJ&#K0OHWxOfGUh6#{sWnimE!'

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

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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/844fc9a82f46421c9f10804bd8055212/part_002.stl', 'relative_path': '844fc9a82f46421c9f10804bd8055212/part_002.stl', 'source_sha256': '862517f06c3ef1dd1fd41904538630f1ad8f0fd6a2b39f6d5848b54e9e357c1e', 'input_faces': 756, 'input_vertices': 443, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.1577748954296112, -0.161460742354393, -0.3405901789665222], [0.16551154851913452, -0.053964532911777496, -0.06852572411298752]]}
GEOMETRY_BASE85 = 'c$}r22b2_5+J>u9STG<_1r}_A4mn5^5Q-o{(tsctiZDbaDuNhFvIGSaB7%*eh!O;bEYPT!1%@D|U0c_6UDvd0T6O<*`|JBu(f6C$bN=)H<GJT~>g_vsZr`u^R#7v@+-~QcU(PXKRh=)!486E`ZO4&zkyFl@kvHv@@uTvl*Pk?HR?I1t$>l5HgFXB8$Q>ASW;nBRM(0f*H7%!QJg4=T7CCj}Ib$YIyJgylNy8^k8=WV4rx7<z&r9di$Bmehmp-o9q)Fqt@y504#_x>(AHOb0Pa*kJqnF#J>9)D%#lva(-wr-`I4k$Y<wWL*hOtcURJ!m~cJ7m>s%<XF&YgAN9?2ZvSKR8KN|-#}XPedE-|S`b)UHide=o>um$b(p)jN}WYc|;9k0kF<*6Qz09-YkOjdD(B=W%lPqU9&7{%r<j@??X!)!!kHZ(nKk_iK+n9JOxAzI~$eBaJh;Q*ooc&g9AJrL5eYS;OR~p0e^dd1`!VD^JyV_E0AO^l$dhC3pVyrnNraCy!<F#IDcnpG)p8I%co`Z@HN~dFf1ReUkq+x%)<2YkiXKI-34<CR_b|@_3mp_WD0oa4?gPscO~NA@|QdY}a@EtC>92tcuk?9^{)=+4KK3`9kJ+Qb((Q@)wiGr%kud&rc3ya_{H1R)3e=?|7TlKk?d%1DU+?L#HG2`xo2mK%QEZdnzjT%XYUv7v%2S6APm9RR6K|`UL&A);$rG`!7|u@>I(S`=j1(l3c%EuUg*zsP%No^?Ew_!}dkhE47nc*K2OyeNpE_YL3bE`QY{XXm8Z{=8)_2&8u=|Z`AqhkbCNUPHbJYH|q1^lk3lm`}f(I-1)Qpd5j0S`aGsK#4>qGecprInP7k3-Q(Zv$>eH33GzbwN$Y}4UTFUxb2u_jl$*ReGat1ddgOXPOzs$z$$hoo`sAM8Z{PIuGr8K&9dcjo=ibYsGr7KA#L1mH_VvR5pySTWvAQ04<gU6Nr5aSt<Z*SqOOosBo!9;Bj;M7@C3af5|4GZp>q3z0eLl$bJ|E<I-wwx7`*xVCeKH(h?UO;S_q}uD+xuSFU+q`nJk@>`<a(b8*GKI$L9X|Wa2&O71iAj4hVxXP({LR1xzl;@xeM1peU98;+nRYE{nT7%AMbfMJ5M<;WO8qQ?POH$)bDaAJ5S`dGx=``tG`bkZ#np2cAl&?-&`L%{$}-0kh|N~zF^I>*`ww<SfkYuYn-Mg_rJNy>YsR(`Yz~Y_4mo0Cw@JUoqGe9?2j7XCD-Hod29DY&EF%}^H040vDwe{`jESNeJW1a8@2uka#yeajqOZM9i7j*MAkRRb$xXn)Hld=eS=)rH^_B;!*Nu7!+EOuhU2LEhU2LEhVxPN4RT%IAlLN`$5HhS$5HhS=cDQyj-%=uzAshZa2!?NFjw_WcI;)wKlJR&a-3Ri=c&qlGr8aC)g#$?l05lr$pcpZn+Cm<8Ry{km#qHeUc=^ltbEmJGw$-{N3HpgJB#b&XXnno0&`thc=an*|Gg%U*KD!Fnom&QPZnDJUGmgti?>_zd8fCzuUKS{A1C+J`0nR-nCqjOf9fwL_tgB|_EVqFjDN^ppHw@Or_}oR8-LuKIacfMlDp5@>+fE>?zznSrM`aA36b>;a$Vmb*YyqitNMohRei%;)i<1vs&A0%`iA{geZ%>v`UbhKZ#W-S-yqlZ4aZUS4S%kxZ`fbeH|($K8@?}9-*6mN-!ND8bvka2-k-?}?awL?_h<4#`!ji={h7Sb{v3>>_vc`qdVdba(fe~Sj^3Yx`RM(bywLtkUTA*~#?kw8Fpl1zgZb$FIT%Op&%yiB`*Sdk-k*b9?a%&@?PeT(|4d%!{+Ybc{WE!?`{!UBeg7Qf`u;f>U*A8I7rK8A$5;2yL4SS!9L!VSKa&@_e-741-#?QVx_=JF(f7~fh3=n&dFuP;U>tq_tn%>wIamjE|Lk|(A6;K^_rea*xvo2Tp}Ld%PnOB#iDetC+#`3MFJt##XY%Bt7RjjGSzYUpHJ?kqKNK}jzvTDUz7*tozY53c_NLiqPOd!}l_yG8u;+h0dFgt|sN65#!J4Pu4|N{whv7K-^AgNQe_n$1zw$ma{#&0}{T*_@T!Gc!tzq(1(SymT+^t*vpmm;1>uK_SADoQJlS@9d#&^j5%bvEzPfj(tQ=+#uzTW@CI;#CYoTuI&f_2dQL(sp)LG%5iD_Z>>a`(N*t^QtflY7l-9I?hBPqppyf;G><_nZBf=NLLq9o=k=pB!ZJ`1+#O_z807A1kc!_4O|7uda9D&(-^3c>bvUFj$8-cAM)>PHU@w@^$k4v+e#teqij8sN8+=?E}`&?X|}A-&*TbRGzqhnKi!O)8zi^?XB^>Ag@r~dcXSm9?oA~-^20s{;zUpZRf~5KBtM52iJ?_u(<`1dHX4md3b#Z>d1YCx9P4Uk@?gCk$G@`63$cIpXl7{_hn@6eD;Ku>-(9oUg~}(T<3NR_D9t>L9XkYa!s!5n+$SQU+;#=`=icJH^|lb>GvU5=ch-m&(A{F_h3Hy`W}q0?%%@k)%{zTH+?9R>;1tc*ZYIt#N@8pA3SosKg9n$&df*eZ{&J^b3Zk?-rwTnj%)94h3;p9b<_7V!Tdik_odG3?^@RjeIFb4SNE~uJo&wVzV5_>-y^8&j#t^_33c6Z$z65basRn8ll$tr87EJu>!$aU$(>^Ax=HS<>t><*y5Rll`??^nWbV(MrEBc#th%2M$5;3BVO<IanRQn8GeMqI_cL*FeLv#_{nh<Up?@y~^S`HoSqFWe={Jb(|8*%dzPdjQ^0>M`OnznZl)67mkn8)yLifok5ATzMbs&$IZ)M-7mHt!Y{d1gLzpwvxzwNgwu==}uiXF|ouM$q?xrY}#-zHC8Z2mp(9PfR~>QA01J*FT#_f{Ow{GEV1tHJ5)+$HzME;^B&$A6q`e(&GuBddSv2a_ioZ$EC0(_y@schTH4R{!=U_x2n=mYoN`hjmjktp0KGL~M@LKi+e{c^;z1PxLUkuf~r*)xrE8s<S=+<OY+c)cg~Z=4GDCcxrt-a$l`a@{2j!GUtO@f1f<5*54`HeQS2zon@Ds{^~hckn87QL9U;Jh5glYu&}>+4i@I>IaoL!^&Bk7^>eVWzj_W9&PP253v&G&ES!&e4i@D4IaoN3dJY!;T=g6*?601Kh5glYu<(7U=V0MD>N!}L>*t)a8<_E_Z}9mIa<_`9W8%w+r?T@ndHnls1y(+&PUJYwj`ERt{PGXXK2UFfHNHdc>>O^5@9cghle_=!dnzjTJ{f8CcW*Z5m0NSfY3t{bd*yFDVXZ^!@66vdHEV74Pm;UO&bIo;$9`=7uIX%3tG`2@EI!BT?>=VE+f?ZqXRQ9@&VZ|qXXlA2_nPzn_kXv>_sP9Q%dGz1&O1#1MxWd7m)sflgw;RE=fzvL&YF))?rf}k%o^wV`DXvTAkXTb>}qmn%Trc=-<e_hHydR2kCVqQ*>Cj^_S<C3x6VZ6-lC<^dHy~2_`$wicH*(9+?m)fGWUwT^S1TAmTxhiYc+qD+|~0xl`#F)`oziOdVS8CeZyDl?~upU`X_7GHrEAJUynSl>gzmT%Jf&~Phy+NeRclC|7!Lnr;L4mCfLW~>il$G^34ADu6_O|Uo?42o&SmTZ8Ld7eZD+$Pkp|e4rbr;)aN(JKIyB^uRpR;=DOyo{lO*o)&7t?@_y!emsI<YPaaqMk3a2)EtzArk0lG%M&|A&_Gh(!I^?d}Ka*|PpJkj}>#s;lzR~CNZ>u|wv=UA^XUvGKKOvP+z5+)73F-JI|EoVCZQium|MyQwTf`iveY!PGH}UH@7Isg!>){Rf^>`=P1Mh@i1Fyxe!Rx|?cwIaWYv6Ib94wEQ!!Lrx@r!T={>w4$;NLrj-{RlnpTm#w&+$*;AMj7{zrYm!7yLW;4gMYe8~hdj4ZkpE_`8^KY2syJ8N4ih1+0!=f!Bcz@H%)4*cxwvUkAHq)i#$J3j5*xs9)f{Iqrd93)|uCs9)esIBtm7fHm<NczJj!ULG$Fi{Zs_siE)}>M89PYAE~~{}%rkeuRHS{R01x<3Hdj_(wd2e*?e5zoL$T|IG2PxYSTslzK`lN)3gj@iKUIn1ffx8^FeR1H3hK@z!{En44AG_Z(A0;Rm=h@!s%#T$*@0_%1F@ya{{<mnL2lo_5aF^CYzrp1`G@pjN_T_%Ha^@Gbmn{3G}V{t^Bmd=38)|08@I|0Dhtd=vi){~5lG|BOqmgvW7d;-z7MbFOZu98(kF8C;sU3(w-x#B<?$&beBRpiaV3_y_p=a3uad{x0<Jcky@NF#H|-G#rvuGvTGwPW&XV4Z($j@RRrnH~>F^AA>jI$MCmcU;Hin4cG^N1Ah(X;;-Sa!`}Go_?z$s{7w9A*bjdjKMwoj$MFI<FssJG9BM6oiq{6>!om0{{0tn5pTW<<;rLnnJvhQScP_N1=0X=Ag^z^S;v;bnUW0r1FxUtmh7W=D@FDmhSQ8(F4}jJ20r-vZ3j9XAFT4!zi}!(L@jiGiyadn1d&4q#Z~O*$DSiXq4_3kZ;r(GXygxn==HLVI!LTkq7#|87;zRM_umwIG9|2qAZKz*sydB5ws9)f1IldOZ2DZwoXJcw5Y=GCpYr<N1O}sj+idV<4fR*tp@XKI%yfpPFi<jiMB=rcq6vt)oOJTXJ`uv`?7sl~wcn-V@&%x`$`uNqXZ$rE#$1U*IunjKn<zn8Cummo1xQL%Atcb_)tKgORRd{{aBx_FfnNLIfYS;u9w#To=Tf$CwOI+qH^_IFfqKP+V{_=h*!K!#Ayf&<b*T$Q|26$7v18j_Uz&pcMcxSvDY>Ripd%|{jPyBk=25-ZA6z@*Iz<XtVZ!g9c_Q?8KJ(!EIYu4PlGI!y1S?}dK-m9>A)_ZTx+6e1ptyLY?Qdl8tZ7Z<$!VB?>@e=TNxUguJpU1H<mgNq|@)?u!u`ErzG%SIa;QLC`#7n{$UJ?&Jd-A!fLK6?pcVTf@4lj<M4@=>t81sDS;PO=jFT(c+UMy?OV*E_u1^7jHMR+-05x)}Fz^}xcz-D+8yglrQx5qodF1YaeEbs1|JNL%L%(*6<fJ+na0mtLg#Jj?=xHR$WU>+__yg3|&OB1gHN8r-LE5PBnH1P}JP+Xe$@8Doun)rEeATDhn#T51r3hNjz0tevI#EZc}xHRz#;1FDz_~mdIE={}!^l)k7&EQB}ns`Sz8kZ*C1&+a`iFb$NV&`hRgSrZL;}h`la3?+<9}BnOWAQw=5zoU%!FBj3d<0yBkHCk+RrqjxD0~nfiVud%@WJ>%xDX$R_lI-w{`dg603U!4f=ltG)HLu1I39uzgOB3Fa1TC?d-zD0z(?Yv;nVnNd<@)-kHN>m9kFw@&8LRKJ@{^XC)|ba#J9k0_!fL4+=Oq$*TMDpI(!XWi?6{~!Ik(b{6V+^e-K{=m*C6rg>XK;5T6U@WYu#XwGuAIm*Nk=<@f{mqwo>@QT%bZ8h;#5z$ftp{xp0Be;VHmx8j@e9WWo48ttbh!hQHId>h=3Z^Jji=kQJVdiWH+9$yQez}Mm{;lub!d<DE8Ux6=y_u@<N`S2cmK0XKDomI0r)NKJi58jOneS99i7%svW<ICZF_;UOa_z?aGz8XG;ug0H*8}KLbXW+B=Gx%2cJiZmrr;bwBy)Ylor;qp(={<U9x~+lR@wMr;!!fV#;5G5b)9ra)f1cOGA4|8byuOv!#2-z!&Ah&u*Tf%4x2MzXA@~fwJl!_%`UYMTUy*K4rQ7{*J-#a4wxrui_#D1E-L~=iHeOrB`?xD+-ly;mT;9i>G4s0cE?nNn?3j67cqcCJV^++(E}V_ad%P`XUKh^7A4#`oS&v8Y&G6Qkap7(FL#)Xov}fomoE|eSycL&qni?~&3#a3<hLdCFb>UR}zI1z%^<Iu|fH%jC3n$}C(=EaG-G@I3C&r8mZ^oCU+d95)DV~5g#f%Fl;`dY2WwiD56;6s77v6-+IWQ$=UKdWnA56E6oG&Zzr{J`hap4sF;dI-?_dSSjgtx?u3#Z{LImaHRJx5>RjF@rZEx4R_Gh^m;;S5~P$=hS*b>U20K6~3ae^=w%pq#7Q;O+RW>2|N2Yj6pE8$JUr#%JKSz(x2i_%yfx7f#9Yc^pr{C&4-RB>X1m<H8A9eiz3R@Nw`Cd>lRo-j0vKN5h%;Xgm+j!t?O4a5g>`9}n-ug%h*<ZjLA7H^Y1IoAJqTE-sv!<?}h7icg0N@#*-j@ZPN29;JrDSMeqIV)zQa7+(Zm#uwoW;EVVId>%~V^YA(F5IzU@;S0Er-v#&Mcj0%yz4#sY?Ql1KJ3bTU<1_JDa2GxcpAGlmv++COKKxGnZg>E{8@~r0#P7l9!o&Dnd_Fva&&L<Sm+*!7z3^yOZ9BwF4TW8CY2vTIj<_`Omtk{Un)r*bHZDy(39I1J#1FxWxHRz>U@2Uh_<ndkE=_zd{3rF4_D^ak{1V@d=fltNe0&%D8@>zQ1AoHz;QQctG2{F21Mm`Dn)pFj0hcCz7*@umi64QraB1Q%!DhHL@uRQ<E;Z^xorJCMR@5l)`W)BBtH5e_6}%#>gjd8%!IF3>{CrphKOdKx2!EtL(te~S!Y}YI@z3C&aar>pSYu%<W?Wi~br)WYUxHVFm*W-i%CIV48LtKF;q_Saz*}<M4DSFt<HDZl)(!T>WzE~N#=@)d`gk>X6<!Um1b>fL!b`#n@RE2D_;1#`2rg?Z{0IIc{ssIK{?~N-gtZp_9sdEBH5UF4E=~MmSc3JIR)RGaUWQ+eSA|#NRq=YT5nc~(3ESW;@y@Vk*4p=B-Gw*eL2bIiZg^L`BTc*u?2EUhe!XB9ybFEAbGyZglsoUg{V(UveaXM&9P58Tr@zzwGo$S9?35lW{G+4XZbjvpoKqzIU*<wDPtu+L0Qpme{Q'

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

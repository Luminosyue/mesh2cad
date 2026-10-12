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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8ca1867c11bb48a39eb2aca203beb70b/part_010.stl', 'relative_path': '8ca1867c11bb48a39eb2aca203beb70b/part_010.stl', 'source_sha256': '6b4ed6c70d0803678a986f490c51c426ac1e8996dbbc1237769f6537716aa2a6', 'input_faces': 484, 'input_vertices': 323, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[0.1259925812482834, -0.2863118052482605, -0.12978513538837433], [0.18888671696186066, -0.12900589406490326, 0.025121668353676796]]}
GEOMETRY_BASE85 = 'c$}r133wIN*~d@VH`yU<!euc5Nm#<Z$q*N?XiY`Xiq(q{1Vyj`Yz2{9EJDSvD4;BYUI-|JEnx@K<U+`DC2aZFq+&1P@_k~Z7PL^ncFvvOxtTdRJkPh}d0zg%^Us+x?^$N%Wac4lc;zaMh4a%^d|CJWlO?T%kWoi87B8k}Oq)11eQKA<FT4~d>PLO~qjd4lM?RSL%Q*3(n3*^(ed^eZ#Qwg-f#droCixP_Psx~;F=p~pQ!>V-OaHzxlcuKI{?rL$UP!mg9ebqoNb>dQl;oS``#=8FvQzNC<_is$T4m4id|N~9OS1A^exUobs2})b`gWrq7`e*r`!8%cCd<~Wl07Cr@OhJf+xIoBd^B3WATQVC2bT7oJ=o=o<Tj<zJiDIG%QyJ`GhN^G)Sq2DY^;y3*Z0>;C^F@vd_AAQ<A(}N{Z+o+-^j4k1E%qe`Pz5}o9*52nU}w}-7o#ncMq4Dd=X#O@n0Ug!{}eGyTa}Jm)sGZN6~fEKBK=j^;d4+*JqV8FD*{wnSB4N?Va&ddA>a&IxoS}m7#o-|H|Iw?)t$6CreEAW4>13`es3)DIewQ`2???J7DT>%-8xGyxe-fX*^@THlC5YUk$nEC9>$l!e~C{pFV8zeU-aKeQVIxO(tLT{(8OJ4;1f?j$2^ojLjxLl-tr%KNK16To>O?$uaq%6}#4W@{GHy)Rd3%^?by){T=_uN!cdfnwPuQ)35fmOHJb-_Fg{}?bpH~+f2UoNTb!B{<bKK`r^UmTTQ-|aC4ofzk_B(ecwxCx0!tFcSnPs{=T2)_`Y*njsA$ep7wo{8btkIr-B@lZ~5wb#yRjC5%ohUp=^^c>NfR^o5<?;v8lfD_4?M%_>WEbC|}RVnsX*>?62~*{#ui>!=~|6zCNCjYLA9Z^QC-!zWfuC!>0A1e0@EL(4`XNI>gu4q2;?+VqE9=`Z~7`eO6++j+C!oM}aRgN{rVjzJ8rrt*;du^TAj7ggR6&imuyhDM#GbQOuut-MMc(khj(32NKV$bNg1(=%^n|xNV!sw-R1n?e+t&k8|!nsae}ie(2LzS9;F-Y;R{h_n*JR<XbmtFZY~x$d$0EzVh|@k#`Q3nDSA+o{#mz;bLQd@%8?O)+HAk#}i*4&rsrzMecbKRhmS7-`uOECO=g5E9X8rY~DtbFFM!r)Q{cg?>)ZJ<Oh-qH+cM?<{8^pzTUnyd%7{tK!>lK`_<&WIVL~wT$@a{@1OEn)b|&k%r^O<FTU~Ax6+E8_3+O89Fs4G&Ryd<@914l{Wi<8O@657__c0dWGr#=5zBH+ekfzSr+ralu5&-1x;ES72mC`l?ORVya@u+H@f@Rn;Jl~(P>=CW`|n=KHu+-UX3zKp|9T*7s;_*#zEzMLHs+&zEuTR1wP90#m9O{LzjaC2G@i=W$1_rx5jM@2^7Z)&jUF2|tq0}n>p^V$S=hARl&`P1z`T3H#`TP^uV-t`_7c-|5ox!&#B_ZrU%$SBE$=qgSAK=-ab-8pd96{;Ie8}cK5X(MT^cy|`Tfb8OuqHn(;M8rSXjr{j`ihb=YCR@x6$N_&8I!>sQZugb@3*XADYzG=m)A!H@EY~k@cQD+srWLqkKIdYx<Z{Q@;WypC~nrkMi~L37zU=Y$v$eSL(jLD)?Mq%J-dVSn6K?y06xM?7W#*o&9RTJvk;{d|M~eGY;b}IsUMMY?B|jP|w@`@-H0!neTH<e(1NGS9{ja!efp<J1fWJ2ksx>>94wP2d=iuHu`hY)_L-LE!XjVQ?pIJm6Gkr-zr<^jL*Mvb4<RN-pZ3t?0(L3U-#8>Kh{pkOsD?qbFxjoc=9dpcyizNuNjbS@<UzPc={WdINHho^rRe<Zx!Zx^7ro;;hgu0i`gbW@KL^JJ@|j<<FtQqNsh@^_vhGogPlFkYu#7(&)B>NZiY?um9N(qN#BP}`6$0aKL0osHuYEedVj^9!(r2SDqkN@_1x6wOZobIg)VFfo7RK!_4N>Yo@(n&`TBbEJ+wS*TF=U_u$~hphmF?@zJ9%^=cax=#(eF147~MN*mS)sU%%dC&rR)q5_`^S_Y><+{hWSj_bcV=_p9KnZqE2<_e16D_e1Ocrk?$V?(6qk|CO4a{Za*AyPt~(N}azuwC9NO_2-ChQ?c<m?yt1fX-9jmDZj#VmcJh>JZF`!JvV&=dl}nTzTUonQ7dDf)~x2n{wiPfH&`X9IJ&O1_mj%k-%nQXd7q|y{rzMGpZ9gK^Ikc3)O23`y`}D}_k_w1q`u*_Q?*J?zR7>)kC~qQ9~xymZ|E0wqJCulhuJ1y?W<$$JQs}qT^}jyvcu$C_oaKr$Je1>)DLu-v)$y2<PNJm=S}VBydP+|V3)}c488KE+mB57!Pzer26vkL(9Bg!Jnd-jdn@?7zm1LOxmTR$UD1)<`366*^uj#1Z{<DXJlEblu*>9&588S17i0H_P4$(p*N@zt6*lFgd_5oieRTz2?{7|z64Q7pzruKacB$AnU-<fbSvM~gnbw2y_4VN2HNVKT-juJex8TuMMW*$ve0@Fp%gPE(*F|9Bdxgg9OZnRMrN8Ibef|2ic0XV|um1kOg0J0A^!NW2eC>XvzyA-ukX#b&m-f9(`TBP;<y!}r9y7J$`)XX&7lSV5n0)JM{%W@$9FytXf99OuY4WY#uUPD9NBi!kd{Oqf^Y>%fi9PuSU%WVew#V1L$Hn?}eV=okZkezz-{hCBdCcvHvZsVi^<%zPU;o~x`+7dUvqOtb{ZhW(Fa7(V?(5?g%AZ?k8h_<i82^z^9W>4_zCOQ^W!DOf>rMMEsr&kR)4xkr@U?a8`7W8}`3ioc-lZGe;)Re=Q#2Oi$GAR$OH=+RHGcx1*z<q%3A|_Dp8wxZ;9Kk**4vS7$1XcE<dnnNlsn0M?O20m!DVt>?D#!gN?Gy=%2GduKec1N9k0V@Da+p%QD-1!3qC+u@?Dgr9)#sFFLT~f+L7f`cAVinQX}vw&i@+xDdh<H$nqcU_{xqq&@bR$*zu4Ze?|Wb{%<?pvST59k@C;%__-aQqhG_az5k$1$zM{Ib<(IO^;=lB_a<#h{)V#5VK{k6y#UX$qu7q$p@-rBwBrwU%!U6<S=K3_p43C|aXV()@hTjqe77C)8aRp;!bADpC+JaFp64%ioI}sU=it-mC-4yR7z7`3<#&kOrJjTr(AGTkG<+}hhQKE&hsn7ZEr4h9yIE*4d_TwD3;)G+?vwQIB>tbtb1q|kn0m7OAa(AC&r?24-;bk5;nR%$Joq@}p&a`l{0Zgb92-Up;Xjbq0`wd_h&qGe0?JeE$g$%$=x%tX9e=XpCG;a$*4auuse9oM?U-W6^Y8}BciPd#j!bkNEd7mkbcZu3%k#*4?RIo0ydB<*ZiIW-(T806kdMl5FS$$I56gCbZO3$YGi7<~0O}5){$BdAj()GB?Hu~Hf$`gbH<e@iaeP1epw7LY{_V&Ah&*R9=DVpklVf{PuNQsJC*O^X@kYk&L;UCI%VxaiIkr2;cjuU${63T1GwIs~a+=Ouf5aF~XPnnDhdmevSzc+!b9PLG-=n<BjtO==3$LIo>%31rsjK04?0CkGba*-CJM2ibV==l6?!fOBp^IU8o_Fn7iY|ed!f&IC;Ldh*C6}(`qw-r#?oxxWY-gMu<Ked{%VU$Mn?(K9^kW(QUPjw1@h8&9<#-c0wj;-Pqz~%cLHZZOUqPPFGUo45?^%vbpk4xfewTa~F~*A+w|DT<>C4-A=^WdE<2!K75`Mp!+!xcg<>VyCW&*sFaw22B41FKY70w=H2E2>1+>cBa&Ync_ddjj+h<Z}@z|-v5X2);QeQ-}Z`r5Gr&4at~yDW4EEYGvnjt|f^@CWcFGz;!;M{jcJO+G5WJ>)KR3p|OoUO+d&^4JvWrci$m{m7%=d9<C2KZ8E*!;|G?j!l8ry3Vcke_Qa^i(Bsl<*}Wp*NHx_CEqN@IE!)HhChwIY{Hu+ZoQw}#<Ba*Ja|20G#UPYa$m+e4-LV$+Ly|`;VZ(~A4)Ev{J-6=4inCP@d5ZV%J<=&K_jp{kKC^wLyy46;8W-s_#WZxe@~zvyYf?eWvK^X*^b=L&Vf%+zSUm(EIF5<C*ZS;*?hQ+@~!sXMQ90n5Dtj)eYty2E{{#6UMhV)C~m!1S9|o=g?F!>%2*#k&%mFG@_l@SzMUl}IX17r$0*-Joni0^$|6pP8@5!6b3*b@!qI=gKf(V*FT?+YucAM~SK({ub@&>56a5!_6OM~>v}&BgG9*_=Ys1yynrH*KCR`6~0@s5Zp)KG>a6H-?j)$A0E#c;HGeUA>v?(mLA>0_QkJf?f!?n<Aa4on7Dqz9fNcP*sr-gHVsbfWXK9ZZGV?=q*lH<{*M0p=2H$s0U%Ev@<J#@4vA4ADC(O-)4F_&B&eN>ds(WA_%)RCfmPDe85Qb)MfzzEie)Q4Sb=3&;9)JI%v>=D+W)KRWAIf^wa^)c5PevEZ4^>Nplms|sV0+u1U7W$+ppCifjQNJjkQ^}3dW@`SWC(3^$S3;Y@mEbC9Gq?&|4Q&BegKMCz;2Ll(v^87{u7mpEI&fXI9b6Z#kG6;F!wu+*T$&9D$&Jv;a3i=0S`}^r$D`HZc(^%Q6K)Q-L~Fw>;oH&M;M?IgXg#<M+!k#BH=tjVzq8|Su73TExsv*KxG~%m{Q+(YH$$t$Iou3xf!2j(NN$DR4$F|-8uh`^xr=k=N@_dB!r^vkd&R=x_VlF@{re8Sgf@XM!QZ3t@b~Z)v^jhQt{mrROIU{F+tAx#8IoI}ZD1ME`9a$%j&ryz+8%CCza-1&j(jF{jB`Tro#+i%hU8>aF4AN|ayPUZ+zn1a>%b{+Z?qxY8}5%bh5N$;(U$N)co5ne9t00STfhV0erOZ8AKVLV0QZ8sqqX7ga96Y{+!anj<uf>mvgA(aby$YvMD#~khU5hFGJKi&NgyP5ASB;`-U;6UcSe)p&TtpB8{7r%iKf6k;l5~ZxGy{y?GF!zhoA%DA#f@>2u_79bO3C@ccJ~@yWl=(FSrlf1MLo{4UenTxbm(3%UStPAWr`4{tsySk>1zz?jx(&7hLS6ecJG<^4VfPkSaxAr2Ja`RVMxo$pg*g'

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

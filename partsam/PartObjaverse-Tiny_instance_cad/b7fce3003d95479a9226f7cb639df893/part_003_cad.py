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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b7fce3003d95479a9226f7cb639df893/part_003.stl', 'relative_path': 'b7fce3003d95479a9226f7cb639df893/part_003.stl', 'source_sha256': '178483ece7e5621c0c12aa5f7ae865c65ae0ddd2983231ea4518e9a8ec15ca62', 'input_faces': 342, 'input_vertices': 231, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.34631797671318054, -0.06677189469337463, -0.36076828837394714], [0.2877069413661957, 0.4826311469078064, 0.2590872049331665]]}
GEOMETRY_BASE85 = 'c$}r032;<J8pj`(oC-n&L0E?~Tq1HvNWhG)K@<WJ0RaUjKmx%i5D+=#5tLg|xkNxhvK%5vKtL9R4B-kPkc2QmR>hGh7K)&|9_v~A`pvIryI<Z`ZSAJ&tN(BQucwdi>+Tt*Na$0ka)c53YifKrvFgCq^$kNrEhEC1nv^yrWpvWy4$n=TUcsni`{GaP@_vKj6NXkWrW!LN$0SW2ofaAGiR_Ua71`bsnLHtFN?PJ`BPXPdNfLgq#MH@2mOpu1;>0BDb?Z)@?`!Yr+@`%}w&#ERt6@zcShwwk95I*e&!3AG`f+Z4j^djw^UkY&#@H<Z+rQSaSopy;m-00K=ZTk9KNwjrp!I)GtD~wP?qB-%)(W-%D(<N8{T)}IRDE;Xth1``N&oG<?QcI+q>d|n|FdP<d@^cYw|(Q`sEzix@taO+epdAy)%RUq7xHVqmMeVo=~KGDs8gZp8{N`Fe&e(2Z2!xE=9}5ke$~$iMxR&LYu>n7p!#yX(l@_pq0Qg>g<toXzw~{7|E)x=mv{d9vu?h*qux=?r;g>?<IDEOtm`FOe%kde(0rL6eDmGX5;Z@*pFNr{^CNx#oGm44eZ9w~o^kVoMvr5vFYE4XAKnkLech#@`P|I3^Oi9nv`?h(zvwMieKU1@iMpSC-k2iQm-|`zzJlf@YJI&Q&pE34vcA&yj%ie)*4MNAu<lb|=^G6yYWWZ54?U*&<Uj0te>tb-KcnF?&6oKP`;YuH)V|6?0sCB3s65|3e>HBNQ}bqY`N_T?oWA$l11D5p=F{0;`m()u_JDKR{5ikgZ#!!93BG+L+s*g<nzYZ>1AB|z=IQk1xYBpd)9K6h=7DX+YCgS<nw?R7na{9amRYRTYuuB%FV`#mRf~(&{a|$ZUiamFh41Mww^-e8#<fmoRbTG6u)lOrsC~8I1+BgfVv5y$9?Xh4lB4)?pG)7I)KJT3_`Kjd&rxv3??rCs+Ud)4Dt+g<cKWit(f@RjS{I|>_2a59>mq&g#r;KUU3}G2bf3CN-&1XCs2|6@>h$G38TK9bs?(S4&C<*wwJ!c&4(@RCGlnMav7ZObB6Xj5g5QPiH|fiJ13%bse380O%(x?(AO76I_bhF$<<r;qqf@FMzPF{{xSF2Ni(l%#%qPC#`Ls|yzy1aBN8J33uC<TZ`pKk1b-lr>HACM|q|bV#Z+w?fsO>B66X`p@C-_$0SE%J@#a;QTAI=ZH*|&9}+c`4#w<uK4k@?dSyYAAL=ScegmcO1+_m7-U*mr)vT5{uzI&Lt1)H`mze|?wTcD}Dh>HgrOhjUzfb7=F>{WSWA0&V`MzOnB;>4)c!Z{D*l<d3_leO_e5y>?ply{r3e&T;XLt=qEg{t`yzYwMboc_7EdH?P;V_g(OhK%Tl!f?EfN^5gJ5Z5o`mb?5LrZQO)CALO|BzU|!(+2b_(>V!J3cS3gPesKCt((>%~drOb0zOS@2H^;>{7py&QkH2BmQEfg^0e_B*@4dRp-jBhh|Hx6-<xMHI^X~M`25Up-?CTqcw0y=Kvd>*P|JsWMc7ONg9@O?pL~`hJ+2IFsBTw1mbdNfq&eJ?w)n2F55BAGDVfX)0##U{fS5_3MemMX8n%a4G`sSFjlUhH_$Fs57=^Pi|7uayp%{S*I=DYRdZCZB5uEVCa(_>xM<@DvcjJZt~#k%Cp>C3zs*$=MNeCkrpr!M~4@!QpL<vwxxa-U>;9kEO8NA5$XFZZE&yz5@o5ASoQ&p!8l+IYV<AI_1}m*>dewAF{&x;WQPU!H4k_MF4oy0|x-zPvYr-wg9>zPx`nU-N5q;oful^4|0I-Ec&kC-<t;m-lM0R%x#4%W=Jve>|qO=X2cY%g^zQZNpBu_2a)i&91-sV}o6GJ$yGp|Gt&}&I$JSVE?=$0XN^g*hp({%=g&y@O(Mtf}8K1GPXqX-(0vwy!Pc@zu@K@Yxo{7{e<fo;&rg3{zW(6x8S(mzHY_}*Z%R#^*=F~?mB<`a`X4L9_f}J>6gooQ4$xc<k?&}C-l8J>ComJH$N`4FFny+0&c#y=~lh{@j9FA_PG-RZodDIRK5MnU9#-<X{!TnzQ13b-u{Cs8}0UkHwD~$|M+ft`x#r-yY`P?uK$5QtZ|(`e!2M%oUz(9KltVH6R~cUnrB~r$~m|FANC#l-|5TxO5eHvoxa>ZVc)U;oxa?kVgHY2TioVpyu2f{AAXMtxcSD2EWLgHP<uZZWzzz#{^ikn`_sei{a}8d8F2Ic$=&t#><3@<-2pe>7|>R4?>N^^U!Lo*-}|ZcuJge!H=kak*SM}%`p)&9JGja<pZMkSIX{1;Yh4`okJB$#U&sC9^vmrZ$Nl5<%k59~{z=e&W&Z3^>9vJ*3`0b9Bf>~dRDNO>rudWU{u6Ubm;dS~=FVL@{l7mkpS9+2(uzVf4;FqAp3qYYpX0UA(+Z#Gwa_yPU*NUSOA7yu*Fry2_+wrREmQb1uZ4c0@Ta^MdKLb}iqG*r#~1vO6<2tEg=d0G4e{GV=y{N5f&*4u<oQLO2`;gsfae7~6I^UXKF{-cRzgnmc%H{I!N;vQYQ+ik2rM)Q7J3L4dJq=+S6Ju=u+aVRF*KJD>?Z^tCIo*-2tI)Bhu^Vc3$;E4pG3F9C*eHWoaTM+!0)1G;CJC2=p}duyc7Kl-U;tQ%ivw``{)<&`|w`$D!doohkg$4gZH3U;63neGzjm8v(bxiHvAr10KW%sNAuzB@HR9L&Lf|K`&p4}MFJssEE*4wh5OT{0q^Sv-+@+w?|>_!_2G(e1lk|&Pyd4NwxYKoF1V2TV4;t|)!{!8kI+Ydcr5Bu=I>+fKKhmG?akbKGj;>wZsvYB<5eQ6GxzF@T_5caH?|_qifUFgL3<H`N1}1?NI0H|BM))(6+tv6e~o#+%x5+7Eyt7jZ$f>VFt)5$FKXM1v6Inwc#su|RtzQtk3t`SN5QeQY03Kr!7b3La0~br^mh0bxDFZ%$I`#x7%T3xVi+N~FCn-MA^288a6>c(ZV1N`F{~qoe&xD`v8G{+A@k6eHT7k@mP8xY)P}LE61TFZTN(RyG#0L9#hq5PCIt5(1P?`{;i2#YL^Sz{rd=K4PV#yuW5_($q7JnfPu8V1b!*MovW|VIc^}43L?3{kuwu9s0|~(+&>rvzxF>BQdEXOoE3_uu3a)|HgKNNb(VlQm`WM{JipQ*|jShi@c86=jcM;v`qbEE99iq&C2y-7ozjD2gG55z9JCbO}+}kl;O`<k)ug%!?(4O#ZRy4ArEg|?(LhzGl6#OLIgNPyzQM9W|G$MbE7(?dsHu8NN<H`KDr9N#LTh{AQYWpZ-4@Y~zU9I@D72OEI52Ib+hvEBa(~<Xeg*%{4;SR6|y%+Yt_n`N~_tU@NBrBR*@hl<uAwqB!v;sWFic~9_p%21BE5kw!#ZOiGOl6!@`jX?0VJ;6b&Vxi1`m4emDiakLqXP4jf6W=UIsG+5$H1elNU`EMLhwX14W0;3MQ6ZM;aO-pJPUpaT@1ejFF=>U3*cAKmGCR@a&#@c9A1NF!fW95XcoL4ejD8gzYVWL--6e{Z=x&UH{mzXSK&9{rRXAfDLfyY3(tq=q0`}c@Jwnkf%=Sw$Dz-|<KRi?On4^!2=-brK<Q@ywH5jdoC2qz)8I6C25Q1H;B<5eoDMHWUxydN%h1*EGI%AL0k4GDqMP8ga3;DL&V;kjzrb1WMsx$b5q=9@1-}KaKwpDbz^|eU;aA~B=p1+vJQsZdo(oT>7UQUo7k(U_1V0XsN2kNn=|^yT-ros*9PR`^g^q`xf+wRdz?0$G^dtHmfOdulz|Wvh!_UCe&?)dV*hF81O?V0VGQ0#9dnBPxg^CfC{?mVz`}dz|UwrC+oO8ZY|M^3GXR_5-_{WfhK2^l`9qY?+MLXGT#HX_HFFB=3f&'

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

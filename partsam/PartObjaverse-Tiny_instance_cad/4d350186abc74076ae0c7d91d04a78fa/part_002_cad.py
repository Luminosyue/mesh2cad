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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4d350186abc74076ae0c7d91d04a78fa/part_002.stl', 'relative_path': '4d350186abc74076ae0c7d91d04a78fa/part_002.stl', 'source_sha256': '3fff09591cf153ec299683a7fb6b2ac7c968f006dc39d983868fb2608a36960f', 'input_faces': 268, 'input_vertices': 322, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.471861869096756, -0.4101104140281677, -0.17959976196289062], [-0.15669023990631104, -0.22668129205703735, 0.2019459307193756]]}
GEOMETRY_BASE85 = 'c$}qL33L?27OjL$KsEu{)O1*6M+gQ8AQ|+F2u2nK0R@I7gdl4|+z@FMP!yEK1vKD97X5%?SUw<28j`RCNJat)g1`tESrkE#O^{zz@7CB=nSahd|L2^0-tAkj-&DVPuey6CJ-e4ES&h+OB%3m!<+yL|V@%*qR*k(7pENOXSbTDevEyG3W0j>Y{*;~fWS_X6{lnM`Y*NGF@yWxI8n(9@b{x^JVKb}Yh;d01lZK2PJT7T?ywJN08J!%@_2iL5#>eyHMy;cwnpv$IH?t;N|KnddJ_YM$)Ugb1y;pi46qX&@yCcJ;TS_1K!e_BAJ+OOoekgw*bUOk5t80<}?BoN|)~Pc``X8-M{`IHlO8<<A*-~#;R_bgH`Lhmxt(NB{-ywBpZ<5rlw3rX29af5T#BqjYkUt~cN}VcoR<GR$@;HZS@$FVuwn+V%TSw)2h~pcuUh2N<SC6_smpxr_t<<AQxB5(!x|4YR9eMur%To8?bA7L7uaWxpOB8?QTXel+&b=*<fBlVg#P@c)xm6z5{6*?s#IcjNNZq%oNc-HthN|*<eMKjv&c34f?8Jd|d4Ak6nve2dRi3Wv@L`GrfA68ao28A;mAY>f=JVLIA4}`aIqJ@5;OyX!<Z=HklppxBF7L_wc#Ae_d9cRyAbr(3($^zzX**;dthjYroIuCv8Pfl7I$hU<x9Pgh<V~0UFQx1GiGPgzqnB#&Syw;h!J9@p;@GF(m%6nxmEtJ>*j+LY*6;I4hrcgj2Ic4AESeAc!mfFEZLCYTQU6}(R<2F?+?w~j9G`J4E5oIGp?e0LTITk*zpg9eJBGgpy4|1r1N$fG^%?iL%yXdPB)vXc-#tqn|Meop_fDhhN-0PFF{E26&yynFmHLiktv=b_hh?4v7st_cA&xydob(Sy>Ghf3kLojHgqDAHq!#J-57p|EwdyVFGq7fmmVfVeRiy6i+n?fJLjOMHmHp*A*@xzNn);Vrj*z-_{VBTMO_$}mc>YSEJVSR*mDnfsTcmrt_0r-89`8qeR~V<QBioUm9ZGkeIFsqt)%w~Al@`Z_(4B#sm%DYf?j9q)(pj7yU)6&%LXU4Lf5i8ukj~B^KgqS|y286r9*`gVdebbo?)i!G;{^3cJ)eIr{5&><&MtOa?$!e;&o^{`m49}D{H?Jy^!eO~lzA|9XLFlOx9(N*H2l^4*%tW6<o}@c<C>Tqp>${Po0@-cy;i@N7VFYIs(-_Kt#s?b{x#wU*U_uTSL?`(_-Y;PFvK6e><4$AoxWw$Lg}7mCsw$1m4By??jNlGrR47$llp^}|9Wpx9U8im=ilzugZVf7gZcN9f8djTTAo!OnY!vDrJH?Z>Z*^FZuXI>t3Fb?*+)t@`zVmzRL?W&-_%w8E8VPrrJMEdUD80WPwf9nH}4lpH}4lpH}4nTyhwe0(J!X1`b+6%e<|JUFK^zpBU*m2-zweQZ+(Z(AJOKc_8I8r{uAiBUh3-p>+5_ZBi5y>`)^Qxok`uo^PVT_673I_ZXK3!8sPa;?YB#RBYhv;@0{=#W&is8=cI0{=gIuO)Yl2eq^|B?o{N(yKXVV0j^`_9+93MeQtPB1z;lk%b`!;!o36$8?ERGVDXCId&nHg1=P3T23&>wR&+O|+b^cniHh<5Q1r%rbIH^18e%<3`x-QR9ZT>7Ojq>pPAT7Qp{B`==@LuGv?!TSt%Q)WVaZ<N%e{uGgr1+^<4!PIM-uOvotV>txrF6E)DU|V4J-iyW-L2cIexQ54n5FwqD!(n1&Ng1r{Cz5p;jiL58_3^EnOdmTPwkVmj^VEtYV~t=JLP|Va-lo__WdJd9$416LT!CFb&<L~U}&LMKi`j`{7)NHsMXJyCn^8e+7)W`6S0Eg)Qi^QvkUJ?-IHV$YW4G6cZzfSo<ePXFE*7rD_d31XYXZBtV{Q(e4cnV)2#>dY4`{8`6KyTNmmQB`ds`r&2!<U0(X5nZ4;#)XkAp`&X3b)HqCSJi2`l@XU9w3{^LM_yFNWbt5O|W-xav))4oFcfN#|Nf>8Bi>Z*Q}Zq|>|&H8c9&7|v^QJVVZ#>QQ4-OBDr^UPUD`J5Q9&qviibhG|_YX{SOvRhDpN1Wg3)}6RxbRVfaZMR#u!s6+3*Y4Nic+OR$x($rX61siw?{r^@jir4hf5A?-?#tgt_oIQ|?{@2+NhuUR;kE5<-KtcQ;y2$y@egj3dZ5fA`uyW5*>2sw{wC>{uVsbQ-@Byw2O=M(JQZeTh0;AM8t%~ItSlWmzS52OY|$?V-ScF}*ORXHw>>{)x%J@w2HieA^<b#=Qo6ZbN;lU_>E?QQ(w{jPs@{}t)|)l)XE{H$zuDmp=zj6pNveD7Z=R1!Q9ni(<h%QqRr-?lx6J)?o$7rYeeJuNmGACfd)q46ch1ypq^s{M`chxpS3i}y+TYk6zta9zcfKA!bsyb#CcH`S+t}YcW#6MXsZ+>b-5;^9T9pQ9^S9s4p*X31>A45{53^`r4fwli^Y?VxPy5fHNA>voSJQP}ZcF~yf1HZ+oDhh3kn*hFzm7*s-D$ejA8NgnZmw5g%R0Y%y`0(<CvZC5?_MvqsygLu$`Zf(dOhbh(7N22=GXFx=LB!(d4BixItv}TuD)~pq54$mW}g<*(MQ2JMxUCx>eFBxqfd+JMtrkReV1qZL-n1~i|v!pi|v!p&A#*IzVFxSd907>t@9|qR?pTgy5Ef+q33_?QR=%*z5H4|M=qi`MR9(2y*cY%qx*Qm!{o2-7YTkjPo)R%7to!4jkJ1j5{^*+7S;E=>)&&eo=bfL>yd8k|4KLaf2EuIztW5C|Fvsq^`@S$d|y=6ulMUr(#KcQuGeXDgzmr4)$@sGNp_}NS9!1vf2A|{dpni(yZcu?zj+hG{qFu%&u^^P=)6#MrF65dly26Q(u>`Hmo(1PuJ@soZEihyy>pss{=w@t{Dar4{7+P&c^dnV(u+Nxbht#<AJg9Nt~aIomXz_k*TvLTo|SHQt(E7Vr>U!XDm_rXey)2RO}$wB`?l)!zqoa7sQOX5SwBiQ>&Mj9=i0C2?hDnAN;mt_UVUwk%#ZQDuXOXhUg^R2bVFC~>FgcoGv;aW)%Pu?uD)+ky7~QysjKf#l&<Du`YYY^SM#(DfAzlafj=9TNOAD{5!+gu@?6w~=7aC0?evdneG}_TJ@7Q%XK%kx{)zi@q#yQSdqZz}9~_t_b*A>)_35<kPb|vO)&<|=nY#L(Q0eCPex|Oz_fvXs9S#3r-VFcX`mWXegL#8LTkvF#J3lNsh4Rz=%iW>s!PHefDBY|FQ&;P&bh92z-Sju>LFr~aICUS<=BfHc>1Mwu-Ru{ooBiV1bd&C@#_yp@H=pyBZvGysbo2S2jj2eVWA2~Oi|wC=9^Buc7u!D#J-B~DFSdUgda?NK{j;a`Yj@=ykBqEbfiZ!ytQs3J#Pw6R5XGOep?~U5eDJ^esXMAoyZ`s6?#5x_p37JS?0w)7;P(Q8-@~zn&pDlA9qc#Y>%iB;t_EKZ{x3lAwH${zeh_5=dkp*#cp>aj@IvtK0l|-m1oAmu=jIwC`z!c0@Lym9;KCjUKaOL+2*cyt;Py{O_B{BX;J?BC2>u)R2|)1gIJR<Z;`kQ!EAVf@SHk`id?omofZ$6wHgjy@$N>Ku$6LTx!7c|Eb_Mtf953Za;26m99Bdr;bKp<Fwg-O#JO&WF0Y@T-mtzQQPw*k&y<i^#?*-lo5WFGB2##kt2EcX)9{}DBwjFpk@V0>9^*Kgz4B{9J`y}{a@E))oz<Ypq1O&gIBZ{wkQ;sIEb-|l}N5WPIj|8s<2ws_^HAgd!=CJj^n}gSfy&Jqfcnv`CDjW}TJiyTc_I~gd;0<7Ffj0oJ2?%}{M>I!Ej#jV@!CQehf~^hS2)qs;cvX(^JV(!SjDmdzd=z+J*vG*8f_DJ~_i#+$7|k&TwjcNy@cyt}!TW<h4hY_vV=Tuoj-jwmfe!`m4f_aqZ}5i!!5`!p$1$8E9`<SQc<?^3{{Zg;{wN@LG{-WIG!7r^$KXEjk6>qje+2$EAoz5SFE~EuSPVNKd@=X}*muAefWHd}{uW0mzGfvj%D{$$mjN#eTN1o1_#J@Yr8yqrh~?-2+ZntAczak6czf`UfZ&}tDskM&Q33WZM!W*}ZASJo_-*h%0Kw02ROJ5UIm*G_V#LdV-(+Mjf!_rG9T5C9M_cY6!?A&p-N=Xw2tE~d8u(Q3B-mu|B=EYh^}y?bhryNr4+Ceg;q31}!P|t9Z5KvdK=8J(G2lOQpCXQnuou7&avb2uhushU6UQlxpTd~n1&m^y1TVsIKF&P}TL6BJ<1FHxMJ&Oua$Ldq6^xz3oGxJe0>%X2&9RGPAM9T6Opfgw+h85=og6zbz5`=|XCYQL_%0l8!@1e8S>Ss(au6>Eu>{ZK$i;Xr#`a)NdojKjV}gIk@d3v|*i`WMIo{)#1v?Xb9>-ja&&8PFb2w%r-fYDB5a-Oq_)Lrm{t04z3O*OdpK&aLz6fKVVos?TPsNzvlQ~}HcpcUTf05$_juhC5;FCCB!T2i}6Z~b4mk{qI#F~tACSrUd#sq&2v8I5(g5x(i-hloF#-?CSHpXp?2_DH|akPSM30{SxGDmsXa^UxJ)WLWij0s*1v8sbxI4+NKtHV|UZ_d#S@tPr);NqR24aVDGtU2b?65}l~CU^vg_%GK7U|WD!Wa3|A`5p{g8oU-qO^nyXnBaFIR#ou(aC`^OtqOY=cq7DW0$vlxtvRBgM`5f9=F|e?EifkdJsh<;n!+{)FUwJeqZDjO@ERO<WBhK630?uQDuLI=anJ5y;nhm~r+*#(`_C2|s`ih>=9&6ynETB0JXY|ftY`O9B2Rqt4VMooF=7STzXAN6?8^'

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

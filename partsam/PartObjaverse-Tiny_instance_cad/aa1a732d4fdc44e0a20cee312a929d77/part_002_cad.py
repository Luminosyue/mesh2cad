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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/aa1a732d4fdc44e0a20cee312a929d77/part_002.stl', 'relative_path': 'aa1a732d4fdc44e0a20cee312a929d77/part_002.stl', 'source_sha256': 'ecdf75acd476bc66c6e3667e789967236d1f1d8b50529e2fb47ec53ca0c945f2', 'input_faces': 348, 'input_vertices': 301, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.10496720671653748, -0.18626345694065094, -0.35764652490615845], [0.21343328058719635, 0.08549230545759201, 0.46996888518333435]]}
GEOMETRY_BASE85 = 'c$}r033L@j7KWQ8DuDnAA+iW|fFwY|q6CnDyk;4c2}{DFAcMTH4JeC4f({_qf&m>sg$Otx@d*J16hyW_2<fl{3|kB#plnYt7-dlmyeOzMUAO+~>8dkx&YT&}sq_E!_3hi$x4Y|gbx2CARy|zf|01=;1!Y&WAJR0|YH8uxi{qxHO&l{Wwe6G_W>nGY5@-K}W(*kGKWTUs?L}=?%-C_MW2VI<=rP^KKNb_G$BdskEp1xLlu=WsjUC5$pOi_d<7}QfA?1Z}cE4qZ_K(Er9a_cdv-SV+U$8v{GxE|N57QF^$1?R--o8NEtXB?GZROeNdA3-UHzcli2v7I8xX~gb$DPOfbJ#`FsB6THzYUwl@)$pdNL-H{GSB1UMs)MNa-Mp`wU`mawRwwPXL)>;=P$Uq8UM@@kBj?aQhEGu?WgeL*1qWGM%4CKJrZ9a9oJuZi}F}4k8*yc{RDR%1ot<MH{EqGTYXF1n%*y+#p^%+Ci4+#Z+To?iyfFtd}7?(JUXs+(ap`Iv_&2l_s1^eJooGz7VoY6`huHVz2AAm<KkAEYWpaDaOvArhsu1J_xXOA$HldFqljC}CM{<1W@VYg&F+O69vAnwTSeTMKj{sAU9L%7?^KBE!nwEo7UJ4VAE)#2oRqjevg9p~i(4Hl@@W6z<CjwX18XF1^q;xH<Kq66K^EmVuP<QnTIFtu8wueHJpYDk9fFs*xxOldxRn%5b<-;gC2sakpt=cetP17vZ(m=?ugfW!Cj@7BT-<tZD(CUr={fQRKIZYO7xVn_<+G_Dc#ZQhnZ&(U<8r8O)3<$*=jKVRI3KZF;^v4L&cFFY;=WZ)h-+Q;$$26h64x7Tkhqo_Ox$-kU*h`4AmaYG_40AUZtkHvJh4vV)~a&iz908X+&FQDxV}-&qaQCOZvJY?dDb1|c^=y+^QQU4EiG5#{vWe>o`@~-`4;XZZhW<ixYlMpAJ5B$`4sQXDRy(S?+W7nKDQ+9y*iM%FER3zo9k~@S`<I3uf)xZYdBB+?xdSrI|dQ=HC`g~VP$zVp6tF7H%5QS`Kl4}cov@|?#&r1abtEK=lv$jJYoZJD?3f*(-#x>#m<tro)^O7(<7wu=;_h>=)59-IU$YzS}o#M^TkC{9rTJ^8c)~x64(7D#EnI!#I4rbi2GK*Ea%zuCULXnOgVnp;B3m%_og&{Uqn0NTFEtuYbhbby=C7@+|qy8MR_`1mhXq5r-^F=&dK%Jn?v04Uz6{Lxg|S^x4j^7?bs0FdY>E8__f$B#QoV7689fyM%){9PmbRn#`(@_(*3MmdVuFIttD|^`L8>uZp#ix<FQV6BksTQzQm2!-rG*&-<2wHe~XH3#6usJuS;4_;(GKG5;rz)`;79pen~#BC;JmOLO+qOqZvlrx^$Jexq2%<FZ_;Jfwla17F_&}2yU&;;l~XvPowRDSNQzD`g5KK?+LzuPv+4j^qwHNo_U(*!S9_`xkuvS_fBwc<~7`h{P)xfY?iqAJr&&l_6?qA)|taphu_oadI_$z%O!5MnNjTKM#DwKeQi>UBp%nDxPEN<DL1zQ=L_gQdGp>0DgOCqi5opqN+f>ti$j#ZTestG?wc1w+(>@(v^38Aw1YIxIlGU#x%W`k0g5m6OY!;##rvr~%jXtK`BTeiUeza!FLiVO&U-XZTBp~1?&fCyJA8ioEmw~JsXEO++NtJJyg&FR|9#wiMT$2&-QG?8`8A|??|=*RT<fowO7T|3b$VW`@*z^Z_RNF)ey&+vIxp|y$3La`t}#*`WAY=PP`^_hscy!cTN|jJpDmQ@oEH5domY=Z$E5KLot;H>7+fe{$JT#bL-8NgmaqGVNj}QI@q6h$G1snGP2*22J1OymmaC`^z3)i(p&57lT{>=R1>Lv4%v+p`_s_sQ{(dgFc>e^qGK2Ezyk_q2N8<_nUE=;G<u7?$+!s@yxD{SN_m!4dO5+h+%j-zo`{0yQZf@2;NB5f^Jo%&)f94ndyT3B^gcRTZI^A!2uT96L_=z*<elu<~lDL0P8@k`jM{k!%@z2-hzjt5q_c6is@EZL0Zr~A#`$PV*mp?}t61TSBByNRXmbkIx2664`kz-PP{5j5_n<?k7pHJKfyDR6plttXPag4;h+Fas#&pL9Q`-~*+*OKJ;;T`z+TSm(9e>%(G8*|%A+%(?dd`Yd-Qhab4e=ptMS&pCCgTKdiYb)0$lfSQe7j~86{RKY$e%LWV;zs8w{QWSuy_`oIz~3|TcFFbJ+l9D)bq6Vrx2y)|+qy`3wDQd~pBR0gkn3-FiJR?)%lE_R$BAo)tIOvb8%f+dYKoly)7$jkV*OrCs++l}g1CRweEGU`xWeCyDoW(*-sVgG{?p7S$CsYs{M|hgH}`Mf#qZB@sXoTp3H*KI-dEE7Z@ti!zi*5jE<G<+d@#LNm}N_)cwh2enm^6!LDKVRWZc|JJgcn~Z$!k=yz0BYRes)oT*v3ttVoF)X_q(Ac_q!GI(y%5%;UxPhrn_^|GeLebF90Kz!Hgzb+_O?-z?6tuD1f~B`((Wf_pz$$2q<;7=d(&i|-7An;(40^W!^%7^lPWok4JI%^`lD;QNXH&P0ie?<fD_how5`fmiwX*L=tG;C;y(cvs@$yNcjuW!?RhSD6n5SLZ{))%noLqs)hbtMi`V>b&Q~EAyM+>U`ylQ<<*>SLZ7yUYW0)cxAqF#;MF#&iN|yl{0>2zH;&?^ObX6%Dm)^Q<;~X`YZE~6R*rOPJU%RamK04Cr-RFpE&hV<`d_<lzBsNb$)P;tIPvVeq|nT;+1(oTN}FHeg7MQ41PbajpFg*duCvP#GUV%;CfavuN%Ijdha|farOBUTzp>@@mAJ6c|3QL`TTI^$%7QHtQQ1V*9(HH>jj4^>jlBp^@0<xtQQ=vtQQ1V*9*=#mGy$)>UzOBUuC`E<X6@Uf~)HV!PWJG6R)fn9ImVvoN+48my=&vM>yxJJa<kWWqsk)Us+!`TzM{>Iw;SDb6jOT;v835k2u#+S&ukeS&umRmGy`-PGvpf<Wbfm4p-JAPCb?Nh{Kijh{Kijh`FWtA-azFnOo^T8umH$%`K0RTKOx9dxzI6pmA(nOWeD+`=@k%!#44_t=mYAy$Qs9!|w37T``9#Z~k*U|5F2bT=q!fM*cL;hu5I|zU-;Qt>WSxG_Ikshd7_b;}6_Lp3Z#S*>4dy5ByHtdg>KE{@v?{`-;Efd4`qo@$BBh^AvR=?j72YxVGmIac@z=4xVQWk58=NT=~xIaOFF*;Oci~!PW1~P9Ehuv*7A?X2I3(%+7I@@63X$-<bthzcV}emG8_>9_2f;!<FyMf~((|o%2<`GkXtCF68&&Qo4@Dpb>n2Iru7ZU;c99=HRvbc{sFzxRLi0-EZcgME<-L93XBMb*Jm74|<%>j|FFVd{Iw+-3O=h=e*z&kI%bHdHh3y_;o+r_$cw>QXZci$@3gZChjl3%=wUW2R%vBUp;?lnp>}^uBNe8Lkri&r?~#)$sqeD^xyx<b7K5|_b1Qz$Nt|xdCq6&V7Fa%%eUK3yX8RV!|%1*0&HJ^ZOmueEd|?Cu#Nd=?G}aYQP{@3ZnuZA{b6ilzOmg}*sUSFj((`!>Ven8Hs;yiX+y9*1lyRu&u%rby(YFXUklr6z}G}S46H7EE%Y1Mtr2)5Y-7GDwl#-ug#Ku|jRYTwZOrdRT}MMl!slSye)wJJ=YxF>pM(AZ)b(p<K72N|?SbEm{utDC4>TLT1!_A6`Yil|sB1H53;0lMs{`K<{UFq}4m1?L8tNJZ4Ti6dx>keU2VWa?tq!dL-vHYp;On9viMmEW8^Djowz2Td(a%L)$3jQLUq)SXp}XPBP}j@Q{qR>%*D~nW@cU5LE6@Y*<51Uq&^_?YP}_0PG4M_7Rv+8zqsGENfc^uhG4rD|{;WkqQ{Y)lRm4?A?S<FS*HC-mtDs*6wHN+=^zTRQg%3wR9JLqzA@m<Y?S+30{nt=?;q%bXL+yqC2K{ePd*Q!D|69~v_^aq&MeT*R(6>-~;nUGiN9~1g;<^^i;A`83sAIQU&=B}~cB^Z*n$TdEuZ@0f#4;ahw{W|KLF>DGOZ1txf{(&J(a<pX`iKdGM#D#8{}^bj%ZH;Mj`77JXB5U5h1lAN2}N8em^h~x)PQMgmyboCX`E|YJ=CinY7>H(x`?ZbZDOA|>=y@K2jh>zxkll9nSaE-Htp=z0gd^N&^Y*x@bS>r@bU1ELR-Q!je&m@zCE-Re0%t|&{+7k@NMj-+v96yx2Dh*@J-<xLz}}lhHnUsgl`D{AR6-#(1+ofHi3_TZvcG=z5#qAyFG7@?}ptbLa)J3g#R=2JNQ4tkB64SkB6TC{T_Y-{BzLj@RRIz({59sKf+Iee*yXv{4~4Wwp$uB0G|f`BJ>yd7vcX3{T2SN@H3$QfS&<B3tFWL_p{(<L#x5F#{4VLAb8f8e-(N^{5-qWu>D-<1MsXdZ$j^bXN~ze(CYB4G5<2ODm-h<&xC65FWK#$-KIk;;ito=Lhrz*!v6(Y0sj~HsnA>SQ{g8=e}JD1|2*^t{O@-A&2AT<=i%>S+iB<p_@A+@1bP~NmEGR7+i~bY_^o!!!v0x^XMPK|orhk4-)Ogw?RFOW75qmy#u?~w_~mwc$8Lqt&*4A8G0s8H!?T>5keBI~@bBXoUqH{mvz$wim+4{n4{(fA&~xxC<}JiAJp`YDeU3m+!T;TEEA4g^dJLZJ`!@DxS^&QqxlTflz_Wed!~RT9z;CnLdb?eOmcnnxwoA~9@NC~q?9a3ao?W}OxPEJK&6(eUTz=>!_)OHa2>Jy)+t-KvnHIypVYk=q)*0Ff{#{(-KR|oKv+=O|CJ8zW{v#Z30JJasW^5Y>9RR<~ZY%8Ofg14a-q>KbA<)6_pCZ>#=s@@txRwUA2Rz&NL+sCV5d3Gz^%Qg{d<L#@FX)r-i?OXIv==<fxej@mCc|&TF`kA#1<&rKrFMH9+8uroj?oR;6Mh|PoeWKaUyoz-hdvFz6gBM*^}sL0F}gy#!T$~05};k-*|l4P>&Ntu@XN7JZ)gI%2leg@eaz*1pwF}md|%`o03GP^iRdTdx(MG7{eGyY@cq&6k2)|v1lRdb&=D>_2z{o{xO_7DOozLC68cPs!L$3~360+ez2JL7`@r{v?*{z?d{SbSs^QiC(|-Z~*FTf}Zb|<kT-{UtjN;xiVCQl^sw5=_vGt_A$f-&{TvgcHnD$R;TcNc'

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

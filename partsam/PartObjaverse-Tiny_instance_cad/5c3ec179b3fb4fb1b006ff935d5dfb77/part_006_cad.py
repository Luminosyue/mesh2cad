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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5c3ec179b3fb4fb1b006ff935d5dfb77/part_006.stl', 'relative_path': '5c3ec179b3fb4fb1b006ff935d5dfb77/part_006.stl', 'source_sha256': 'cfcdf43e3424c3ab98fd8c96b15530ce8721731912963fbc412dccb897aaffbc', 'input_faces': 228, 'input_vertices': 231, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-15.37193489074707, 2.050689697265625, 8.71784782409668], [1.3922076225280762, 7.424163818359375, 19.948379516601562]]}
GEOMETRY_BASE85 = 'c$}r03s_It`p0)Ax>2ezxnzD4B_ZT8B>OaFTszT>V#1H)8d8Zu?Py#Qay=pDHzp**VAAB)Y)&pQsL)`B^K+St`MWeS#JHTb-tXHPbDsbIdCqhGJ<s>qYk&4y?|Rp})_&L8Kf(rC)pJ$w*Gj2$cX{I7L{X$16jvoFCO&a;bWB3W>2b*xiW719S9e_#`r(kU5f)04GS_Q-OhR<LS1*HCz=WP&z6P%eGvX8D$4(zJBYu30<o(9RCd3GyFllUDjJWsi(zUa%p=&!|!+gVk`DZ6wP^Xu4)TJ*^lH65!_58+5Ud^))f`7llP2Q`=&lA^1?FQGky2yJy&cRz=4Q}b+KC7s{UbMo8xKk?ljbyT~ZCnX{Xd3v&ZDdDv%p$IahJ)vfXh{AHZAA9XuiAlEuXLb#g{W^{-4gsX+fN+QMqW)Hxr6__68^j#1m4vOJU@r}RhqXUt{g1tK-_a$BdYIm$5UR7R@=evt)qUG^)G$N{~@1(k1Kbj`VKuh(DPMWz)uI&qx=4j<iBxqHh9h|vTwGV*NM18GPpwq)z_yTC4cn5IPl1o7?%s|8zZKG$EJ}TgZj*muAha2FL_4(sEcY*zxExrKggQ=$z6sx$5?}x%%J+(%mngByY$SLc%CK2U)$M};-ILH!S~LAKfRB%CO;D%fk$Q|&ZA4flW&7(VSbgvXNa3Ts@T2>@!U1L3;ENa2>gSf2E?CDBY%|i1K?M3>QlX%T8h6qZ4-F2GQ?kT>`d2@e*=$thwNy5ex>-Rzb*&Ak%{`2W2nCI{Y-Gb_0AYiSMo>SJr_Lg6xq=you~Th_7w1+UpFE9g@5fRujU&gzz4T?qH%`bB0C0s2zanF**BU_W4sIdfcL*<Lw34mQJl@y-M~Lr>}dR%JE^|O+6_G3vl-ndyHdY;fg|{tqPOV&6Gs}a9$ws@xM?=cm#OqQtp~j*AG~_LE#04Vrg>3qc7VH%wV-~hHe;QfP603dl(-&fg>_XN&)mwA{BIhE`ErW}ztotx^5`-7qxJ6w9=V_VF~oV3|Jp+Xc==E(s_&bJ_s*U9y%4P1t7qZo^S8lI$C5u<6!L@O&HS29^P;Z(4)4W=hTyR}{JG#q@ica~2XBP<sD}r8&~>vlxaD%J=b$j+n*CiL;uCU_ulyp3>jB5WKQE{GGH*QEm3Y!F@T_%Y#}w#F@zIO(!M|Tbekxx@kw4m#_26gn@ILxaB|GZ%7U0SN$`9I<aN?$QPT(V*-X?yrGse~YTsz{0{GPt7ZbkhXzXtb2epdV+6IZ+rcoSFM9O=I7QCILS;BH%xmwI$3uC3S%o|i**jLTYMT<Odsk%!fz<;aHva>1)3Xdd++W?&x2tOqacgn8VJeMIfc+&fz#9=(v(p_Z`(e4`EgfB!zckEU-m@VHdisp*aP>zf4dl16wha<eh6xQXE1Qz-uWCVn4FyMQ~SQNN}Kzaej|VqR>4Jk~7_ar?0yc)_<6f7Sje)i+OV&Es;V^{ltMLhIR7;tD=*AM($r<zz>j(-3^Z66~`UDa1{$?ZKZXQatsgGl-j$ZNXialb`yDA1NQ|!<gq!f&V$vJHg&9FXCBuDc|Z%U%~&NPT)<Bz@J?gi5p#g!Fxr~xJ>Ss5QmTL!CPYeXsH!gSLyY^Z*4_BeD(wKYJ>uw`xmlrsEEdT{{3lN;#;sj)oW!K@A50)t7j57KG=lylT!(v*O&6Y64(Umf5=|&*e|dzI6uI?GjJ*RJR|L2X6vso@1OX9mtLfKQNQd*^KPDA(}sBeX0$%l;|p+3IDd+HYg#`_)G)lKo+aR6J;;uhj{V5c@(B3aTlQ3cXqgB3W0?*9V@Fy)TKy;w#D67t+zaHr9rKZI1D1g+sd(S-KE-*gb0T<4tOvzEgzT6vCxDwi#=MjdC$2u20iFx{ns+_yU)v^g{Q}~KpgGw0Hw*@MwM1Sz?237>^#>2Ip!HyW?M(H}XZ_fI742Wj`o$DCbyNrNqDq=~^O5JUv#%Mr+dAa`fhNpvNPY01ThP8{p7|R4R6}cU<8a!i)E(o=e{I%tPvV95(eJ8`6d$9{PvEu7D39sI!8Bir<xTJ@TN=}SZ~^ROTnBduAUnEy1@h0q3h?i9X&=|^y3zZqmYoClzmN04&b1hq)d}!=<;2ys8JNe`2f<6T!1u%=&PNY`yX`<enQBpY&IC7&!ntJz)|KhbHt^GYzB+WB*0~mJ0?)^Lr0lIEZj4z8{_}b|9~w;uFy3AZ!1vsx`89Tor~OwkOal)pKzyuzz_<p)fZME~c&epSXnwU%y0iT%dcO>98^Hd4AMiWfac*q>8s7_ZT7geGjJ!R!FXs0^Gw_@+>{EBABaa!F=cb|l8l1ybtH$5~JMrD|6QAeP8iA_`h=cD<s;|3Pf%gi>e!a9W&f95sS`)8cLHST?iucaE>neC{2yt^-BGortz6>5!gLAdzRGfeGB5-GX2PyA2#5sS_0dQju<pF)^V~lI^9`K%X;iqXS^{d}20N;c8RTklU!89ii{5<dD`@og!Tfrl-el)+2@jVs2f$guxKC)*q_RagfoQN;jj<|J0ebc}W;QQC0-}g}8Jn5Mu@z^nlPhcw6?bI^xjN>#eZ5hU8I(`g1`wRG!{yXyFv8RoQJH%q&S)K-ePDg`ZL)=WeL&?6OcO>)481L-4WJlX&2kyFs*0b`vHTIX3Lk)>1Hf~COC(fsN(T3JI5I^$}`}>_VTIYtVnc%^{ksU2(FV=0l;owDybUs&qdqnHs)ZPm`<0E<>4KCPEwHvL#ZKmVBPUZLX<uZHX`45pFOvn%BSxMkg+o@l*bANmnY={7_LSE8-*^Y6=y$zmJLi1v-@g@I_0Umb5O9xOMHaydbt9P4%8*bv<xC`Hd>SGu1lLfSYX@{GGkNeD)c)v`XD_)(YxS7?vHpH)Z<GVF)9_B0h6u9RroM+y#grD2q19uvZ{iPD`i#emL0db$J<d4y1F!s%6`QW~7QU624&D<=)n)u^|_#W()gL9^XeLd9oL7XdI;C$QmCoAIT3vu2!_YmXim<%3?-!ZiEaLoJWVoTy}H&cDnueZs6Ly8@^X&B=6U<~@b>YxyR@eBMJ%I9If^jBY#KacSpG%^X}3U2<Ac&tX}E~V-r*6l1y@bZbo4R>eY`^dBL3*z@?;e0y;=S<DE>UZMCdH8<uE93LV2=KMVIPXOyV_p*4f|no0`Tx5ouw&l>Jn|KdODW!jaV@y`jCfEw&a2~bo>7`!sU_ZJG`&ZrR44fPybwHR9>vqFEyjK^DWryYVLhyqeX)p-@9kfRk8_4Ut?)gfJneIvcnN=Jg${+CsZQYITaX>oc_Z7|af^6HJ@Us`VF7=tzPd{M&=8zgJ(5sAc<W`<KZ<pJ^(6Z3nN~^MrpA(Z_EhlL(hB0g6yu!pu$<zi6fQZ3`aNj>QmyyHesSRm#JN7%(J$b8R`Ktn6QA?~-yOC5{p%fCLOd&zxSDN=bB?y<Q{uJb@O}My6V0Qd%unbmFI#6J&PSf0{*sADh_5iwxYV#}^!p<4@5F<9()XrTu@2)he0`F5(SCgIeAF2ARfjU-VV!Wk%4&@GuO3)QyxNZPp4Orqc2fISfxpJ@Z#^o(AB?z8Jbw^=pXq_$Rg}ROz}-&Z9De5st$)Sm)eYjVj#S@d%fIIwa{dSL?TI)a)_)B<3&)r-uA}^2JQ{wEJa?0L>RX7z7lUAD{GQvy=aiG5dQdq0Tzl>(jJF2+;2}O|E}r>6#0yVhAL&$!ejl~GM?B{d>=dNHe$#>AVcEzhMV_!zW>byv?!mtQu7Z8%{(Ip59{Bw*(FXN<c-Ig=@)E!2Oge`5x5LTbV296vPw=~(Hn-ms;*t2yQomX5qlW$ISLO#7+#mVbi;N^>tGFr?#=h|rvxM@m?)ty~#5~#mKl_QfOV9uBPt3aTp;YLY&_SW|Lg!>SxLhok1ha314h#KVNWLql_`XEwEMJR+j>~BfIw5pR=sThBg?{AwAA~M4Kgs1YLKVy|F~7vVo#b|Aq1()F3YD`>S-!z`<?}m2*Vt|ax0Cn(;Bj0Lx+-*m%XMS^mdAKm=roV7QmBf@cb1<?ex1wm*><5VLOX<Za(N?PbGW>ppXD=KC$v`ROKvaQuIFce6WT0PAhe0wnYgXawvKZ7OK!V~ZEj{88`zGC?dA$?71}NIsn8b+=6g5uUCcgX_Br3nbx_Rg5OX=_g+hCT@`SbteZu^J^2a)m<-L5(<MKYCuN172E<zzf{e)%-EfmTWY9Lf!sF6^%&>ErDLaT&U^1ZCPoVk^dg^(qe>nZrNW+rXL2u<LALbx2meMmpr3;76rAQUVV&wa@HqlBV`rt$M=W=3YRZX0gjnah4cPTaRWmu21<EYw3Nkng+m{b083$2Nkw9LoMq<9?HbCJD_GN@2<JBB8~6l`#twiV*sc6~XQL^0U8kyZJ&(*lr5jn9t8-{qf9`c%0IYbZ)bX`%33_az2I%jpY6!xIB^j4dmy8x&IH@el(9gl*c`a#~jKrmj4cBE9CY@yqYSQbK5tb+X%fa)P(1v4aeS&>v!Y!ZfwJc>nhyVmgmco+c@zY$o28Q&=8@nLjFP>g$4=zMMxFuDKt|kL1>I3w*f_ICgdzMTWA44Um>(iC|PKZg7sd<7I0l@GfHSQ+Z)aI&4nBl`A?USd{11t4@Z99iv4RV6u^GTa-xtXG@bpBeWmjKaG^-na31FZt}om566(Wae@Dn&$iQ;v{$(sCzcKcf9HSsbZoz2#F5kZ=<SR5xD4fgk{gZj112buFAjiEAm!%)QIo<=f9Khr4FO(*fArvRHl<#AOvY5;JHC&c#DnB32ZDt64#PgBGHsZMc#~hEP+)mnA$$T}}ubaoETz5Fz4`Ri#{V77@gy!;Chw;74M{}6VI&zK7=I8zRc{o3t%rP0u^OnH#Dd(#N$Fu{_jhv&mguMAG@8$Yws31o+R**Ag?(`CB$IOxI%X*!dd$C-EJl>dBZ`Qla8*&{hw&B6|a-QTGiDI9n|08%#M{{`u^MO1TxyI%CkZY<rk4vrvgOI0CYX$FGTQ18r-<!*xT(1kqP}-3>J(FWC-=Rj_M>fx;%wwx~jwM^jJd?*`$#Iiq`DelR_1Rtw_aW_v@O?k-r#<&2bC1k*GS|m*eYq#e+$VFaQ9(`|#r2F_Pu6L}?fkeb^OQaJ@5KGcd@FOD%y)r&?Z)f_?%$7XhjKZD<0Si+`CjIAxd+JnU$+m`?K6uxHZoRnKash-E~nS+8-1C{d@uKtCEPxV+e`cNx&B0MBcDa{SkpQ7OSmuDHf)fErK{Ed^<O&v_|xR1{OLb<{CmqkAJgA#IYHR^*P%UZkhP4fm~=}@oE0*=DgOkQ)?Ii'

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

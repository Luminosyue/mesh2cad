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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/78a7c30405f64b0f8137c3922c1464a0/part_001.stl', 'relative_path': '78a7c30405f64b0f8137c3922c1464a0/part_001.stl', 'source_sha256': '2ee6f2e7a0c83385e0b792cb3860980abf84e37ca8454ef40ae573404d2a9996', 'input_faces': 440, 'input_vertices': 241, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.04006216675043106, -0.042460888624191284, -0.19893403351306915], [0.19925463199615479, 0.3320960998535156, -0.09404366463422775]]}
GEOMETRY_BASE85 = 'c$}r033L=yzK08fU_e<E1ciYH(SRZZ$si&ljVJ<P$q+yk#6}3nBIJc#1RIEKVH*$v0-=MTEVA!Jk`|IQiLwNP?AR_asGx}N%+q=L-t_<8uR2vVHRsHEFP{JTefQ($R`p$~LL@0Mrb10ae>F5#e)2?Yo!W*Wb(c}on2?e-ZusDovCT)PPA+FuS6;r%T-u{g_oNrg854{taYItZ4o-_}>xpYOv`t(yPu$QkY2(rcjeccJ+K?3Sod%5>n-cM3UmKK~5@|PiJfUSXPphWQJX1aY$FItfTkuwzxxRfQ{T*7ImNY)d{Wwqj@4s%4wzqS4<^7{?9(D6Z=lXf#jhF8JK($M^msrOM_DtU>?cjyuCDw7AKK#5MC)m01X7&B=u2bWCp9vMXd0${ej=JublRs4BEU06@|G7Jr_n&BF8|R-q<M?~d+p5}4nkye{*6XO752QR2RKEDRZEBpexwg;iPfXsf+G(XFws9OjI!>_R4%M&gPTM%f<(A6(H#PiB`E@ZNs}JHmU;cDJjWe*5_8*Sa^U!=_zMBsp+jv;Kr)ahEMvVe>T~F8MN8P-)a}RZ&-sEOG)&2afhHZSO4>G>5;zZ@W?euzuv-SO(-j6r$KiKm(-M{wl`ntxjd^hh|)ht)t=lI#X)HusRdOr+XP~hf`<6o%t4G({Pw;Jb**KPfsKH7id7s>~l9MJRpb6Uviji%a%pT75i)%$1BpLGnctg=Uq^HY+ZpWj*+xOxAh86T<p@AB|oHGWPT+jULv#Ye9@H(q&v-vsU3UM_I+-tAB8&o%A7ed@YvFX;O*`#ZeZ-;+H_dH>1Xx_=vgftxq?t<(E<|Dvz^{lfjqckNMX-Or{E;=SyLaMpR{y$1v8{{7~9IlQ@EfqJ<IR6FK*TYslF`+I7YD(}B^!gjt)AH<vcGtlxI<-JvE>v?7!o!(qW-`)ofsd0_p^*Edtr#Ff?FOO|iKDht5ng<`xE2sDKyb4VDS$Y4}5o#PC=f&y0oEKlK|JB#Mu}<H=`5d^hDo6E8Z>z=+^SpBUAkV9C-`hFXbu{nO>COA}J=pjob=?L@rPg!dDWCk2^?tnO^T*+RJb%LB>B@Uk!=G92$5(t*d4KGKXCwo>U!2~<d&*PggdTs_KHE9<J@?jO<*Ro%WAi`XnX9h1>b+9i_zrK5?;D-3{j(q2KCeGedPI$1=zT}E4<;8%dMo{1`?kxM*!<zjN0tB2hn7h@cy(6D&3hJj^n0ywy!NA}EVcD__-OwI8??W@F;lhcXB>0$!8vvHbADE__9OmhnXSLWNBdvP$X7lqb(LzTJXz%C19y+sKM&N|rTxCVmDc`FZ}#_Q)+kW^(DQ4o^XAW~r+wFPYjnRQu0B|;rk>|5O|-u&X0>hpPqxy2b&J*3ah%>9$DjX{_J99XjqlrY%+-5yuc-Mq)+cM<ZSQJpf2TM52WO7dzHeTZZr><$^Tv;dbpOm5+HZVgjjg}KoBjP4R%?Ii@>(^|TP75_d2c9Q&A(A$z4qU1R^HS8*Frb%Z?#R2ziNZ_v(~S*tykU-?fY$8YV}5)9PL{V&9aT}@X_(V#&`NsjT3%#X`!1pp1oJEV}~Q!cW#ws{k%?ZeqQf^i`qY#7_iQ#)0^|@O~0i5FGJON4<;5Dx_Ki`zkmIo-qt?<&ugvYJAHJ$CRQm_{@T`nZNE9Zxqti}@6tZ0nSO56{h`p!hcgc7{uzz5UsT0DzQaey@AjznxwitgbLa5U^OD+H`-+vaZRgJSjP}EN*v4`C==ojroc8VNFIVHN`)^n8JGDjMXL@(-w+{)}_F=VY+84)W+UCdM&G|86wran#$vSmCo>xw9KCk@mZqt6onM~_`aC&n;c#C#w-(>J~$$)t-HWg`~n(1$^u6x<l2k$P{<BU0>ee3=!tmne%&2tePep>rKC1qPbm(xd|!%NR=UpRY(bv}dDe$;+Pow?Tg_vTaz>HXhrj$}CgimUfcIHuR@o2uG}_q-|T@%0M1`S3k`^mFfT-LyBV&r;+3S8~YB2e$Xp^W*8Q{ejI3t@jyRJzV=qzbsJK{rVGEA6#@%kJE30_DMgDSNAg@5OVXL`zq=EQ@m9BezEISKi;QKZ@y21i5s-PUTMC%ZeGifoA>P=ukWYzUhXq{hPt1;bs;xz?5?2a`L~1G-<$BB^?sZ_`hM^FsrKi_F1GE@;TN@!Pf*^!Ws|E9hkn=hdG(g|o?k|){X8-!<mQcb->d5y6^vu5eXEMvSN;|gLT=vIv8CP*gDPr&E@qLsZmrveZr*r#ukQb7bM4P|-Jsh19Od-p&r!yrc<sFjQ`P;yn;UZT!E@L3yq)c&eVv<Xy^QQeAvf<iov!bvq^tHppM9P~y|lmKRX%uas;l?TZ>rDNz~0&~8Nc58xtu=wxw;I|e$3$wwsSpknD#49s(JJ5%XaraRnX73_eW^Iaq-*geyS}Dx%uGW`}ICd8>zj&Za?KYM^0~Wj{MzbYu_econQZ;LxpbMSL3GcKV_cwO|P%FelBmjrP@zQou{tbC?VwLy-8#By8LyE_SM^ux1KMjH_w;%t*zPzmZ;}OxbKldH}9)=RrepaSNl2Xw&#*@?X>pBia6EgdFb>(o`+GN)O)^lew^N%AEV0|?LCcV*v^;3N6*)pE1aXBXIuBP(?|F7q1&9(&Kb7-<Miww?-O?x>3y<%o^_u)y}8eWzG~VVFU+&fn>Vhe_Ti(W)cx~baC-B-5NudS`{0G%>Rj-ib^3t$o=t3^ef7&~Kby}Pr#GK7-g5EU``h%l?L*W1x=mA`m*>3Go6q@RwM6aDjZ9bT#q-wb&F8JZ`Agb+P7PM$^Zs>uulfEpz5m8c+dh1Al=j|{Z>aU+{pj@3_hZ#G#?SV(w|rjXvFXfb#mUj}lWf0LFXxFp@2MrfnlX%6qoy%*kmXnEBGs^@`>)i8C;VH#Qcp;T|Ns6<{fWpuG>cR#O8617G5iSJfUFBQfNPVr;M#E2NIf4ZnWs*a@Y7@h{50H#d=zd2Hzz%CbNC^$4*U>YkE{mQgYP5nhVO%`lU3oW+`n-5NOg%+N3tE<5pGS!!>!>svJo5yKS16CKLA%IE5ViFJIM0z9dHb3z%g(IvK(9ij^+O4^CXfz;6%7H*$wUtKSe$RKLxiS{|L8$8<G#h4dEK({csJqA{h(Ea?iqd^4Y4872vy=i#y2}xH5lM6TX9Xedf9*Ss8B1+SDf>fFEZqo04&GTSKq?<78{NJAc*z?nwJt=ClLZ9riM(&yqdhCz(?(*$r;VoIXiD12<t#Tatf-|G=C!As>eCWq$ua-Vayc&#J(&wB;N;X6Um}9X8L7uz9|O%`+%$o>O7-EDM|GUD$jk2zRA~pQD8TL<v7Z2{)sJ8&kq{$y%`NBl&ueEDuXof+g>PB^$w#@vvk&Sh5Q&nFvdEh9#eZC0oFf4PnU|uw+HJBKIx)cBJ-4Djoiq_Pj{Vj#M!jglE#{ZFnE;S$t0(Sqx95&rEm&ZRx)yQq$o)+R|qt{UjH_Q|P;#+ycK&pNa5D+W*1#j3<}F(q|a`BwvK3fB#4ghsV>FK7;8e*$0+>FGMN@?oV6#45XjrpW#9DO(tJ}U#8DMxF>DtpJd4Y$IzTi`xW}U4ELff{d!00RXB<E5c<3V_oY3QzWvDFu=IJ2ev&W2Blw;HWItH?jHaLDC|LSWh*TOpfc7N%jD{D|ev`hL<OEpyOrxLV`>^!?Fj6z%Oxo%6nFjBtE&YOq-pe!S8>D3a7Q_23ZP}-J@W+<6?8hzeKHAH13&;(yc-dd$;RUq&<6b03!Y}Y=eaIJK@v<+H;XamjPu4pbXSRE>u1UCFtXpr^v^TCV>(h_5>xX-Zbr`@J4Zw}UFJ#^);1)8knap`6?tT1z=J-RLwB_u~G0M)XWCl40&VUQa9kAp9xDY-bsn5xL@&KF<@1le^kvrf`@OzZ-TjU&g4)-nmZlsn(Y9%H7mq;xo$5Fzm<Pta)9vi92<Z5yWyo774ri8O7;cQAcK(2%X@H$F(75Nv~yw_Ef@LEcE4JG^rISw8{4kgFIL*ZA+RQOfcM~;Pk@F2@v45Eb1XKV^{o`Qdin#@{FW{%z?vn=bF#oF#7KOnQ<Eap*o54nxZhPT06$pE|+-cGKAx5IlW;f>@fcolQKkrLib32!FXz?<Rql(3(C12)%2Se}h@jk4!(8a@s0r{*%A<W5-fpygTzx&CglfIJ8nz-KAp6XZ_#1RSD-=aX~cx!kw#)kysqsjtZI;jiG&DB&<A`~xL?i~JG31>dBEzay{0l3&8#!Cz3qrzzn@l<+&`Rrnov1^E@c0$xUb21_o6m%+0sVe@@AgZY_(pHD4jUKcY~hzwiiJj^<rCI3o>;V^S2{0;dn`2+kde1p6N-+-@^H{t8>*Oc%z@;mrD=Jy&U{5d6joIDL5ht21|a0a=^D0_DZPoadTlkdRO;aTJgcosa5Tm~;=J%mdmbuLmT$xq;u@G<fbd<;GksiH{bMCugzDSQe(LkXX^tjAgMyis=6gbT<|jk5D7yqnB1%API4<}*ilFIfaj9yQ9IUBcVRT%+vyCcKsW$S8Xr3U4D18)eT=;XULL_y}`iK6fQ|k%x@3_qA|7`H4~XP8a^1JZF^c8DVoT34cwN!jcz^vOOt$oxEg}?OWj+<Q1cAp9_D>T1Z|dufUh#67mv!iEEUQrLg2lSn?Qrj5#VH55tF<-x4wx&SjlS$Rb$s6fAiLE`cwS=i&2wwu|ItSbnx1W9Xl+)8V%%;hB{1R7!XvCHy)iJd6?^ObHL9gkPqFU!jDDP{OZK!lNnSN#r!RgwG+LCn>R9`I<5R>Ypr^efia2^sWDZ+4-IJU&~s*vu|Xq=r3uL67P_|e;ef^|H%)zJLR_w#y<d|aPgr'

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

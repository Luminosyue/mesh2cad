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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5f1e1e7148424a6bae25b5138ba0088e/part_003.stl', 'relative_path': '5f1e1e7148424a6bae25b5138ba0088e/part_003.stl', 'source_sha256': '0ef3446dba48b1cd2cdd0ddaf766500341103ef0aaaf5ce7938769bb26fd951a', 'input_faces': 312, 'input_vertices': 256, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1776563972234726, -0.1316446214914322, 0.10327371954917908], [0.1636752486228943, 0.014104628935456276, 0.2717522978782654]]}
GEOMETRY_BASE85 = 'c$}r033L`!vd5dSlMoierU-4=0!EOX38FoypoUcmLsUWs2oQDx69xmJA%q=q*klb242v*8*g`^BIw33q5fD)pg>Tpd!zQayk#}#^zd!qWeCNFLCg;?ty1%Ylw{G3K{e2;Hi7Z+yMB|?qv@1!=+gepMO-hg!q9w*9jEe6QH?rZ-;bV$u<%!E5SI_Mf)v-%-5iL<ms@FGeWS@k35qiB>`n9STuGi}~EMZha?9g7r68gqT-Y$0V$T-1A4u~BdC&pn-nzsnoo7NB4$LasipE4o^--ta2_sLu;j>(kT*EI6zYf{HBx5pb<QX8qGh+EOjeTBKZq;{?kJ4W1KZVb9f{#Nb|@;6E|H&a&bBz^W3;*M`OaedTqj#DLw;uvWIbCfvOIF7ZDxtph*{*KC{@-w{LnZex6(>VENzU10u=62Er;^vZbw62~Cj{WKZykFmVHI5y}`_=n1clTvH;eFY!GI#f7wdQ@<x2kiTX`8btj+MuCyU5%KTgW_pAaUmcbL&%^^N$|O``yD_TOLgQR`opI?^fn^<~gd5F{$8)<mO7|`lN}pFQ;=b`I{DVvs*6L?a4**_jN=ZE0Ol4jsA+b)$3li*WYO8Bd*Q-G282JRb_u|9CLTSRy6NdON76hXR({SuF2f3gEfuoVD)0|uR{~AgA>Kv-Islw_vKV)?yt|o{oIF9-Lt*t<vYOVWfWuXo|jP!eRw4*Tj|4D8C?G}%-ue8{uZfn^r6d*ZOq+%v)i8MI&1}Z@7HIzUu&8B?^n=pu0t1<yZvkxnN0JwpKnn<*5|JuCw?n6%e!A|YBci#=GLZ%6wf)igzI*dxi2`B;`>f*p>r|vRqj+MMsb`&Y8)-(*)ND6P}kLae#rf^B~{7OsGgv3V@Qt-FE>_#N7%bbFXww|bztu34S3z`G+NiF`Ul>-3h%2F;<Ow^akQ)Bscy!tNecIU(wyR(GY4iV{V*qx*B#8<-w)4mKR70He?MG(N9ArmfE(?ZyXR<@Xvg`qX72Whb%OV6M1Z?}(h_~rNR8tx=J%5GBwjuDCT+-H+mX0kIhXb5hgm9jl5t*VmTghaWefT$kGcPSKAhv&OI5DD$#Kl^5QSUwm>X9DIez>j_MaQee9gmjrJp-+KWOJ}Fu&M>>l!(M-x~o3)4lzv6>{I|U9*TgUw%Mb|L`!!FS3fbp0$hp*YW$u>N+)D>7Oy^p9^D%TSedH`*NT$e=bZk(!Kp}*nE$){HB~|dLZ}JhukN2{esQjelt38ziF?WCT>+pBJOnT#OMB?`(|(dYYq6l;k0i@+{s!@+={)!pGWz}H+kbbchTps9bo=-e_prbC(K)zo4onk75V;ZH{NHSf0^GmW*xp?7usy{_Jf|s{osr(yUANOpTYOh-V(@hE>`CE@aomfH<u!ACP&e^+he<NoSHvvRQe~0`%2665jRe+rGC)Px92|W!`y%FM~V_RKVWX<2lM@^Rf^-xKF|D{!yM=NcEt6s&JwqKoaOI7U%bJ*+L?{sKC~^~ufBBON{Z*}G@0^vrxw@$xXO()bEwXG4TrdK`O-}C&*gh<Ka<P;<9jDiKP7V<dp`INH@XpjgzqO+_bdL+P{hAd_un*c_c4d^-MRfR@q}>V&dFK(=zRM0J?Z5}>P&_EmNiu3=pCLOBL88H6mD$#jd@rzCBC_~6veTZw@|p1!(8t_mgBU1f#Udv?4msFfhu>Bb`v+(P9(0y{$(%4$&BGR8&q!Y>&5FHOyzw|3g!Gy7eDOfZhSvCr*oY4Z77abv>3;4GDC^4Z7)jPs{Pzn()oMW)4Giwp73&KX#KScA8|zSw*$ML^m5nV<;J*-?WEfr;C}b5J*@DcZGXzG3ys!$xfPwIaBcP~_Rs!O<!h!9cgjcZ@UH7@DarmBF$&i^-=lNa8pNvpOKvONDc5%WpK*6xms=?_GU<6xn<$!>&3&%b*p}(-bG-!L3!|mVow?lq+TegJ>X%9peDA{8-%3@vmcjl`%?8AcPFZvx4UONc*3Qt~q+4b$rusyrWz+cMz`ZoDa;@dmhjoVUqH%?I;>Pq6%cwp9i8-{+%X!4LyZ2Vo`Nmv#cz*AF{QQDV{a+<Nm-wx5#I45(<0$^6$&`n4ZWZ&lt0fa}c7(XG^dxbk>!o=V=kOX@*Z8}SxZO2j1=V>#nf<ihrSFORhUt`#FFu91)8i>|b9@^4YuBD<|6u`?uT`rZ^P}HUp4QMn;=X+iiR*a>iJOHLh-<T}^SYIGFpsatd}Ik)*Lu4n#rMr?#qq~>pHBV{_}qObIy&Aw^`mc)zuvhUalLya=W}EY=abT%xP7tiYKq^jD~-+DaU4H-*&_0P<~Q=!HpKHebnC%!TCdFIJ{UsWh@CTu&T9|etHqO;UtO5Od4}?Pcw92C)2c1!84<yG4w%k7J)P_D<>wUN7x6LYS*9}iYiEPG4xi3vezquaBj;E4U$&h0n|PD++;)ZQnUjS+3YbFi*L^_!X?DnEKD7(^+ogMQU#&XDyw4<h&sb^es84)rzUKPWsGmT*DL!|$soconI{0cn=5zc=r@l3645Ik<lVTLlJUoZbx9}ORgBi&8U}4JpRG(k*`DIk%K0W>V9LjTA42`V<@G^PpDE{sku0#JS#O-UwD(c&`lDzJTPVAqMMEB8b-kr}eDVqK3ru>WYd4Dha&+5hNw0J`Ct@MHX{;4{QxKrl>pG(F)p8s$n?`y?3w60O9G@sMFIqbi_Z~@i7Irq5}wt(}QlKvUx^JqWEZ_V5a?92DPdIR=fw2*oCH1gN_WgOzVtl&6_ukri*3!UG?omO!@t8Ak4H5X{Sug;%wK0m)narE#(6vr2q!|}%k^5;&ks~kTqkK+`+Oa4Z1Ec1=0*x!9WXWl1n2A@;%asFD!@hkEA=FBE*D4$*?*Xsat?a^S0Z;gM8{OxgNm~Y=eb<-;!;(N6}nD23&nOwJ@-{a4V<Y)OjL)UP9O2qKGIknh-bqwX>D>%pTZ#QE9IZ@>A1XbeiCz*|zpXtN(e0-YE<xETFWoB^yl#k%^o%<T|kmtB=NuP2Z65rr+yYdUg_YFv9zIy=o>AVGWznogD@@W273GCl$KF5hU%Kk4b;&V$K$oG09z6Z`;#_QIMr+ON#won|qfbYF^Bb>k2Eh^yOBPw0xI1?KYx0dca=H<@pmlSReRsHSA>-h>VUr*usFxB6wQBvW?=-LYRjZnG$R$2a>P5DEfV=f-`a(7=Yw^uUPidX0O8^7m&-`M*T@2lBPx<}3kysw_B+>XWP`^f71z3ZBb`1d32SOenz?^h+yE8PD*3fwIHk`l)XJ;Cp>EdCtRv(NImJU*vz*WcyZ<$3D5^=m2Izb?3QNA=fsVqbSuf0ye=GL(F5z4kFL_n$kseOmQ5?SJNbxxa4U=H^V!=l+s3%CilxYhTV(>$9Bw^`I=p-<g2(`k^ZIwNv9|`o3hf;5yqi;`6-wwSEazxVvAMn=h*V#x%~y<^Fnt>vg8)dGj=SavhBM)AE#a3{$!P9Kn6I>hG-O{kq(LUtE5Ey27mh{=Hi-n6L86<G7w}PpNg-fcFEqzYgHm*n8@}V$U+~d|%1aE`DC&{(g|Wi}Kft)KcLy^m1aVkkVR+)-Trcrwa+?kE{RuPZ#mc{!f3pXxg~RfBUD4(jo`>_lw$))<PmQnK+N@K}W!D1E0FkwP9Bi@*M2C;MEYj9LD9qYJ&#}DGw<JRu^%Cpv%K9E+kk;03;YZ2(}JsfgFP{t_$4;_6tH<!mkCMNmd=Y2DA=a#;%BQMKB$_gpdl5iePT663`W3zk+q^2q_{YP)JcoAbbMxyac2U;?==i*A7KIsawH*UdXdxq40YiTE-25cv(py&p<*vEEKVx#WTrX#acC?Ltz&aQdax@r!4%-;(1BvP}r4)R0XREzsk_1gj9lfSuG(|AeB6<CSp~^Gs*sfTx&tsg#EIRhG4J4PqIeXPebTeVZV-N26RK%?J#~5`gPb+zX7|wkQd?mBK+EczXkRp?55Cf!<PCT*iuKr?jWQA#tpzC!8?L=64D&w=3pJcJA-u*(ir2$V4cCcg1sxG8OF`Px`Mw4)=kJu7{3Je9(WX3cOgwMZUPns-UBRJNI1sfU_HQlg2h1hgdOJLu^4|SM821MLDz>Zwdt|LFb>096aI33Tj&p9zYpyl{}uXgu;&SxD`YnG0@zZ23R~)hu%%uHTh5)2dD32lv9y<9EbWyTOM4^6Qvb_iuf|x~YcSr3wbnqd^4QBUmiAJN*C9VSJ|^S~AxEJ<_t=LpmUa%t($2<MYR6;m#aP;z7)yIQ#!~NsE!RDac+x(IvD61(OT8cVe$036eHcr<2lgJsm-aXzV}<x2(!L0t1pBIxWIRvC9M_i5#zRknJyA%CkSmZBJWqj-v?n081)T(Y0_Mwk9|`$~kTKAsVSg*+HsVPABW#(|aXkOl!@d{t9iAQcuwRAT7xD}AJ=ixf{uOe^!@h@~)Yo9!LZ%2wg)9bJFJ!8a>5xrei{UpJvI4BHklsT22<Z>q54tyOspDYxL!2p){$O#4>*nLK72s1LlM!z+p7%x$(>*>elQ~TD?8VDAU~il7%w;!GyE}Nc0d>2N^SBS6?;tl(H+TQjpr^o|273dv4co@t4XERBPfQz3?)_Ws_a1QBZE*Lj)`PDHUxD23!1p$uxlH!QkC5A7vWM<!zxU5wJeT?kY^krp_Gx?v{sBE2_D86f58|?G;A5aaf;}4ZuR&ZU^SOuhCt&T1(05_qh0jIkYp}l*GC;_GpfACe`m%?+&!qowjHP`FWBKd?=1BW%jHR83vDDwdmi+Hv(jJ2Gc_9OZoQ6pIE9f6!OI_gM@nCXp0@w{9*M*#g9tB(Ka~?htOxlAnJ|koV;*CJe^WceKXRwz<#2Y5$B=m6D!%?4;@EL{YgRtiTu&-l02svCwJ>;H-LdU}%0^c9t_s}zz`Z4rF*i!!n`zIl{VBf+V*Dk>LC$K{3-(VNQ{u%ly><7rht@i`0`4oOnpdZ410{ap41K2Z!{8Pv$&~m&P`eWF6LY4_x3q2F|X86p4%mG^lJ`;Kd>?1-l5HACM(#{pKL&z4$XJ99U<O|siy#w}6AzOuH2}u+3Z;ZF%nPlt0XG5pKPDgxqt!-dkB8vos6#d`+YvAucmi(nk`HzBsoT>g=?wz?;#Pa`=-X*fQ{M}3Zk{LjaT}^&d)cyx}zZYf'

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

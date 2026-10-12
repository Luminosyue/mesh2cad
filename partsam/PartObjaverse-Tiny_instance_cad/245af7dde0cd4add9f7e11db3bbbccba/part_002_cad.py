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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/245af7dde0cd4add9f7e11db3bbbccba/part_002.stl', 'relative_path': '245af7dde0cd4add9f7e11db3bbbccba/part_002.stl', 'source_sha256': 'b2f7d649c2b7a4bed15eee4df1f8b8a07697d43b97d41b3db70fd70b83fedbc2', 'input_faces': 432, 'input_vertices': 271, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3601418733596802, -0.2612365484237671, -0.2026285082101822], [0.3037778437137604, -0.0695919394493103, 0.341397762298584]]}
GEOMETRY_BASE85 = 'c$}r02UJwo+J-m9jvY&^qeQS^LoA@;!GcDDVr<uPbu^-)qOlhgj)KMl(O@)|prc}o6*Z{TGXo+j2qMH1LndmXu|#7u#(M9Z{k?~~4|o2x{`LQ6?e#wMWV6rS-#%@`;6Nv5S4MxDu|@6YjlTZ@V`_6@u53ZboOz+2hRkg@^RvYctOob$A1yZy8Xgop%7HCl;U1Gh=6*WI!`I-^V{$hSPlLzgS###inJ{zwtT~fHR39*5#@rB_pF4HJXCb!FExo#S^fYv8<!M-E_&@%sY@33-!R1<pEtR-7=hT!cM<n*LrRmnq@72$&PNxg@ymEkX&(=8}wdbY$*C$0UCxzv3pY!=ayS`TUB;9fAtv%0k;H$m%ykUsr8QnN9LbKI0%18Ft^Q=qDv$}a|>&?Hj+pez`tLra!c${f>eE9zwKk~B0-uyLRcK(v}f!SVtN`0C7D33>)?baXuzv{odg<0H3=Fyw#8I?+PUT{bey;cX-p|)A{a_w&{Vt><2e;ViXolAWD8ADQZey7Vt{&UH1(?zem3{>oSIpeofaU3a0A}`g-Q`1`KRFcjgj!721@~#)v?bcG>U+x^2D0(*k^jXo%{ops&<^9>cn+HTMSBOp)J&X0D@t6F@*Q?xayi@edrzBPMrlOwIe_}1F!}d`dM6XQBp!&C%60Y-F{WnC-5IytSYO&W}_6|_Q@r`eziupKiM)T{7m4ruTh+Z3ihWT@y-}cTd_Gf+JPy6uovY6nRy#&wFd!~!tv~C6WQjKV;XP?)bM9*9fo)x{d!E)}cQSUDE<J4HRPxQ<^DM|E(ZzH)kR9lhHGc`U@^sMHQ??f;8M9}!BovDAPa%V&@r|nM?y&^BealfGXcf6b?dim$C&Whfcvy}S#^`rCQ6K}K5C%UJLp4EWQFw%W5`-nyK+P)}1b;uOGeC?%K>~H;LY7zGdaRq9c!qO6TKDj^nYKIc+`e7~3irzTk7Oy`G>K|**D}P+c5IrmIoXfMwbxDTcrBy%C`Bv2UE75D~lIP`a5xrbvvDsdK7S%7+-uP_#-%0l7srj<=lzYdWv|9(wm#G8WKKX=LPh(sCdW|dBTSQ;F-mSf}L|=M+g<aSA()E_<udP=b-|)>y?yUot^7Gc%a6H{_?~I^vJ~+eo(KuL16upu@oqHvISc2%K^5l&(hn^L^;ZA)%KD)SatzEynj_$ZDVj}JPnnF249Dn0qREK)wHjBP=-!t8|i(Yn`Xtvj%b$pa!Z+tc-GRfXNOMTgSdO4o7R|n0Ptpht>kSNwuYNKDTR3X<QdTqVNU2C&MU%Kxj-Oh<#TW{I^+IqF|jnUny{-=-f`dfR-d|lQ{zBJC8d_Euf)i{2CFn;4mUh<&#mKR6({l<9t<yAhPnB#c=X_g^+_B=jQ^zw^)SH*FRHyrqLMtN|X`rrDM_VHj7z27?}OZ0}~>om?JS6&~(HeW^O8~Ivv{^C^{=i@j&Px<_37M<^$nkjk~c2PG^<@P>aKV^Ozt@n9t{yde6eNsg)$M|N7-s+r6{aZHV{pEi>wTNE&N2g5Dv$z8^j-?&F_xklVi(X1^Y8Jh5=?)sd(p)~iGAb@p^wPo~ETXrz+NN8VVcTe4SL^!C)c;66Jumv+O%uI*HNq@<L#+s^Ti};;+?fGcI^QMDB6?-ybQ*uaUA`{k;tdwjE8V6kqPOn<r*2)QsMlGd*Vd(ZDSI?|ulD@?M|tF@h+Y}gR1v+wX*jKGUOPIUSC_lWuhZkfH2>&le0=G^QT`k@HkEYyXeil!PW0M7YThuqrS5!VbsJ^tJkB@Gn|67SKkUZmZ$0CfC3>m2wW9MCJ|w^DIjwW+CVqa(J|F0=BWuE}Y@Nq-q<N*CtL}V|oY!$L1=XbfeoN@RF?lerkJYU@9rtN<dJjpm^7Eq9Urnd)WoyPHi=H{j>0*EO(c?n?d2DmKE>_0#@s)>n$hW#j=gHsm==y_aBc~{$w^~c6f8Ou(-rMJkbkVaZ8R?=oHNHV!dyn#Z&(CM(n^j14TEM+LdMo#)pj7Uqo1^KywDqw}(X*g?X`(kK?xX$*9r^s_gsg1QE4Lb%MQ=FsIgQiw86V$N;%*kboOvcy^ekyU^$(~=_r0@u=S44d?`jdfl0KD=8()QwZ}ePxPV_8$WxD7M&Lil!Gf&d|S}o4e`C8jEb-qhrp?LlneNWNz*~^2*pB>1bBi0H&nWC4QmQNME6x)R6|K5Y|BdbH#ndX%h?uzJ5nYXX-&kru}<5^=q%@Ms)VU=0*)<fA>bameK@j20#)*0S3D2;n*cXfU|>+Q}LM6Z<iWs2T7^7s|84u-LjbpMW;Mg7M<ru)+4*5^gf23XQXFO6+Y{a=sbKX2%>KS%W1^{#o-^!NOIOL{kk|GY6}+Xc~U_c6^I0-qG<=9%(@e7*ZL&YX|wx@a@8NWC6S&$Fq2Nd$fGt{TEU3l63J6|(7i-{e`Wdg~3heE$F2`_prL(Pr*VyMnlva}Lt_S5MP<sr*fg=w<J7)PGhH)iL-%k<O1lrik8Xs$am5JE9}K7cIEK$6>ji+)HgQ()f9YxtF5baxXvGdS2&O^&%e-OLeH;yh!KqykONX>H4#pkJH5dR)+w6|9z>vzv0y<+$%$)X}`ZP(RveyQvXfY>A6_Elj=Ed6pgRlhu!0JUOIH!B6{PdsWeWV9g4UwN>C{EFS}nuVyS<#o#dao>Ach}gX-K3erz21DKT_^ORT5!Y(;@0dc)IGwBCgM{63(3>wZ=AY}lC;(JMaL<d<EfdJdaJ`}>T1+4IoqdY|S~=DgLs_Ptn|JAwSshcurkFW%p}YLw2)hexK1UK-N%3LmFUMgBeA^lSA(ogeTrS@fno-N~EjdCZ<p<?E7NdvdSz*h=5;4uq1wJBoX`%{Z#h>oA>Xeop+pB=;t796pA|dC)6Y9AES79ldv!`V(i#d+($B@Xc2RI^QKFMf8euI?d-)Q8Lx@6TU9v{0us-<yEfer9ZFHIP2rNH%%L-^YY1v6nmb%=+C{uZ9LWO&~@_uX}O}88nx%C6tAQGdiXY9^zySOX`;7=NZhmCTj;n`Xg{PT{^WDN&K14k%V9Lm7=QZy^~+G5*XpTxWAcbXalfR%V4c_YOY>6280!DNknXd$!Y+%R6&zPYujGG6{m13e`-h`M=ke+!s>9pxOQJV*%_<bnXQlikotG~TOV{};=c)h51N0vI<IFtKYwy*XXKQn49EU)9e`qkaK=drG6<sfd<gIUiAdmaM^-WzGKcyC(*Q<8&^_pHh<?A(iy3%#OIqQPxO=}u+&#uRk?>{hK=W(AY^<OpTUb|mOjk?ftD9DYDi~F1DkT>^APkNtakz43};;%pQM6W$BtSg_ApFM*5<322p8-7{z+I?8_#>Zo6UAWJitUYvId)}4$W|L@qJikl{Td4l=(`f#9j#$Srs!#pdI?sN-m)9#;_gkXXjz0z{wvTG7#9Z0r3Bs?46!g>5{;!Baz5iFgBJ%F!_5b}9(dV`~d|_+L&{STD+y-6=-h|u@-UQx(JOthW-iJ&C?*kt}CV`KDk0H;1kAY7jlffs!r;sV&Q{WTGv)~ipqsY_Xqu|5H@4$z_dy&V%d%^L@Z^7~4jmTZ#jo@hHR<N2&!O`HEXex&y=Ym7QQ;~DPQ^C`a^T5-<vyjWcv%rgxE5VDv%aNPF%fYe89pG5-7UVwg7O)9<1Z)B)Adi6)zz2{g!3V$xk*B~1!TXUX!27{_kVnCLz&nwL!8^fUBlm*82FD=d!7*SNxe+Xb7b2s<(b&s{Xexh(rt%DAD0l{VI&vy_IyekD4IBoZjhqFZ4PJm;1YQ7Mf?N(>0**w+f+N9E$SvR~@EW8Eyav1unE+k~-hey+-T?j*c@X?1cs+7Ics+P6au0Ydcr|h-cr|zh@@w!4a0D_2906X8l);O^^N|a|3$d5;(Nqpc&H&HA{)HpMz+u>@aO48;0_;aPG7=n#x`!jzfY+eD;m8f(4X9%{ay@uG>J^S$4PK49gd-!s5m>*<6Krjwt$mE9auD)Ua1eM9auRqDcrY>qJQy5|{3kdVJODW!JODfpX#@`h2O`IT1Hm65$AUis_eYKa_Xh_cM}q^v{g9);{lI;Z{{Z&|_d$*X_W}1t4hQ!JOUR*M3G9db1ndXyi5v#*3GRg)0qzC%M@|4wz+U>JsoV`sWnW|v*caR#ISAYx+ygln+ym@`3<mpvyCMgGyMj9-2ZB3;J0SzXoxmNDAAvi9+avpf+k@L81Hf&;ZIJ!IZNROOeZj54t&n}dt-zkh-e6B~JER0|2kwCM19t#>A$x+oz~0DSU~h02q(9gnd)Wm|<qyzQu7mUi*8$f>b_dr5*F*LI*8?{|`hXjN8zQ@c8-g1nJA)g8n<6`bn}VAmJA#{m-H`3UZs3;4w&0dv4`ds#2iP6i8te{kfouhC0sau_3H}h=9N7-s9Be>#02{zfkY3;>;6_Mqa3gSiWEXH3>}7p4l`EjBTnSkRTnStSSr=RdToqXlToqg$*#KM}Toc(4ToYUy*%(|K?22p(b_Lf$HUrlJ*Fd^~Yk;dETY{^BU63AN7jR{yJGe5qBC-XzBDg&ALvVSpGqO3@8SIEOfE~dO$R=P1uoJQo*a=(?Ssz><dsz-mWrnN-u7v$#$g1F~*e8ap39gC#U`XvNt1IfxkTt+HP+x|00lT1%3|SFe5%pq7XRtHs!jKMN2dtlAjSQdFcPjP0Lw*0)Y-_7*EzZ^^+u9Uc8)9qU*xFaNw%yj!Y%Sf^Qf=+Ntv$81M`$YliToS<C-@!G!GZW4xSRuJd2l&!WuyzZGPoMD0=OEu3X*}VfSr*q8L>0?J)?XAeh+?*ya#>`eu(@D{1AK_c@2CUd=r@uz6mZwo&y(xbCFr#TyPGW%GtJNK`O{Buma9No&#rq&B%PP8Jvl{2F?UuK>h^20RA3%5Bxp21o;G90{#{G68tOpcci*EzvHvYe<3S?)u!@WqzhPWD*p>v9;`N%-yj{pZ*ac7K&t2B3pAA<BcFmFgMUHZ2mb>8(bkHQR^)xK75p>u5%>q>9poeM9q@0+Kf%9&|3JP2{{eo5RIiy=_^h%cuA|CeM{q@CHE>06Rb&-#Rd6MwGq@7i38`K)PWY_yYexAT{2KfW`4IdJ`~Z0y`~Z9xc@umWd<$6!z6CBq=7NjBmytQ(%ixQ)mWRBA%mJ&J4ZZ{}VE?)H3Xtc)1>oz*VsJ6egX?H2-$4Eh*3O9=$gAKR;48>HaB!f5qpQ>Z^iSmf^GD`4eeoa6m;FioUz>_Q>27<`DE&*+;J|YH8RKaCPyGVjOnuv9{|2w5R*('

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
